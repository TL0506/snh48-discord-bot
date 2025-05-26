import discord
from discord.ext import commands, tasks
import asyncio
import logging
import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Optional

# Add the parent directory to sys.path to import config and weibo_fetcher
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.weibo_fetcher import WeiboFetcher
from src.config import (
    DISCORD_TOKEN, COMMAND_PREFIX, WEIBO_ACCOUNTS, 
    FETCH_INTERVAL, EMBED_COLOR, EMBED_FOOTER
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('discord_bot')

# Create configuration dictionary for the WeiboFetcher
config = {
    'WEIBO_ACCOUNTS': WEIBO_ACCOUNTS,
    'WEIBO_API_BASE_URL': 'https://m.weibo.cn/api/container/getIndex',
    'CACHE_DURATION': 300,  # 5 minutes
    'MAX_POSTS_PER_ACCOUNT': 5
}

# Initialize the bot with intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

# Initialize the WeiboFetcher
weibo_fetcher = WeiboFetcher(config)

# Store the last post IDs to avoid duplicates
last_post_ids = {}

@bot.event
async def on_ready():
    """Event handler for when the bot is ready."""
    logger.info(f'Logged in as {bot.user.name} ({bot.user.id})')
    logger.info('------')
    
    # Start the background task to fetch posts
    if not fetch_weibo_posts.is_running():
        fetch_weibo_posts.start()

@tasks.loop(seconds=FETCH_INTERVAL)
async def fetch_weibo_posts():
    """Background task to fetch Weibo posts periodically."""
    logger.info("Fetching Weibo posts...")
    
    try:
        # Fetch posts for all accounts
        all_posts = weibo_fetcher.fetch_all_posts()
        
        # Check for new posts and send them to subscribed channels
        for username, posts in all_posts.items():
            if not posts:
                continue
                
            # Get the latest post ID
            latest_post_id = posts[0]['id'] if posts else None
            
            # If we have a new post, send it to subscribed channels
            if latest_post_id and username in last_post_ids and latest_post_id != last_post_ids[username]:
                # Get subscribed channels from the subscription file
                subscribed_channels = get_subscriptions(username)
                
                # Send the new post to all subscribed channels
                for channel_id in subscribed_channels:
                    try:
                        channel = bot.get_channel(int(channel_id))
                        if channel:
                            # Find the new posts (those with IDs we haven't seen)
                            new_posts = []
                            for post in posts:
                                if post['id'] not in last_post_ids.get(username, []):
                                    new_posts.append(post)
                            
                            # Send each new post
                            for post in reversed(new_posts):  # Send oldest first
                                embed = create_post_embed(post)
                                await channel.send(embed=embed)
                    except Exception as e:
                        logger.error(f"Error sending post to channel {channel_id}: {str(e)}")
            
            # Update the last post ID
            if latest_post_id:
                last_post_ids[username] = latest_post_id
                
    except Exception as e:
        logger.error(f"Error in fetch_weibo_posts task: {str(e)}")

@fetch_weibo_posts.before_loop
async def before_fetch_weibo_posts():
    """Wait until the bot is ready before starting the fetch task."""
    await bot.wait_until_ready()
    
    # Initialize last_post_ids with current latest posts
    try:
        all_posts = weibo_fetcher.fetch_all_posts()
        for username, posts in all_posts.items():
            if posts:
                last_post_ids[username] = posts[0]['id']
    except Exception as e:
        logger.error(f"Error initializing last_post_ids: {str(e)}")

def get_subscriptions(username: str) -> List[str]:
    """Get the list of channel IDs subscribed to a Weibo account."""
    try:
        subscription_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'subscriptions.json')
        
        if not os.path.exists(subscription_file):
            with open(subscription_file, 'w') as f:
                json.dump({}, f)
            return []
            
        with open(subscription_file, 'r') as f:
            subscriptions = json.load(f)
            
        return subscriptions.get(username, [])
    except Exception as e:
        logger.error(f"Error getting subscriptions: {str(e)}")
        return []

def save_subscriptions(subscriptions: Dict[str, List[str]]):
    """Save the subscription data to a file."""
    try:
        subscription_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'subscriptions.json')
        
        with open(subscription_file, 'w') as f:
            json.dump(subscriptions, f)
    except Exception as e:
        logger.error(f"Error saving subscriptions: {str(e)}")

def create_post_embed(post: Dict) -> discord.Embed:
    """Create a Discord embed for a Weibo post."""
    # Create the embed
    embed = discord.Embed(
        title=f"New Weibo post from {post['user']['name']}",
        description=post['text'],
        url=post['url'],
        color=EMBED_COLOR,
        timestamp=datetime.now()
    )
    
    # Add author info
    embed.set_author(
        name=f"{post['user']['screen_name']} ({post['user']['description']})",
        url=f"https://m.weibo.cn/u/{post['user']['id']}"
    )
    
    # Add post metadata
    embed.add_field(name="Posted via", value=post['source'], inline=True)
    embed.add_field(name="Reposts", value=str(post['reposts_count']), inline=True)
    embed.add_field(name="Comments", value=str(post['comments_count']), inline=True)
    embed.add_field(name="Likes", value=str(post['attitudes_count']), inline=True)
    
    # Add the first image if available
    if post['images'] and len(post['images']) > 0:
        embed.set_image(url=post['images'][0])
        
        # Add additional images as fields if there are more
        if len(post['images']) > 1:
            for i, image_url in enumerate(post['images'][1:], 1):
                embed.add_field(
                    name=f"Additional Image {i}",
                    value=f"[View Image]({image_url})",
                    inline=False
                )
    
    # Add retweeted content if available
    if 'retweeted' in post:
        retweeted = post['retweeted']
        embed.add_field(
            name=f"Retweeted from {retweeted['user']['screen_name']}",
            value=retweeted['text'],
            inline=False
        )
        
        # Add retweeted image if available
        if 'images' in retweeted and retweeted['images']:
            embed.add_field(
                name="Retweeted Image",
                value=f"[View Image]({retweeted['images'][0]})",
                inline=False
            )
    
    # Set footer
    embed.set_footer(text=EMBED_FOOTER)
    
    return embed

@bot.command(name='subscribe')
async def subscribe(ctx, username: str):
    """Subscribe the current channel to a Weibo account's posts."""
    if username not in WEIBO_ACCOUNTS:
        available_accounts = ', '.join(WEIBO_ACCOUNTS.keys())
        await ctx.send(f"Unknown account: {username}. Available accounts: {available_accounts}")
        return
        
    try:
        # Get current subscriptions
        subscription_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'subscriptions.json')
        
        if os.path.exists(subscription_file):
            with open(subscription_file, 'r') as f:
                subscriptions = json.load(f)
        else:
            subscriptions = {}
            
        # Add the current channel to the subscriptions
        if username not in subscriptions:
            subscriptions[username] = []
            
        channel_id = str(ctx.channel.id)
        if channel_id not in subscriptions[username]:
            subscriptions[username].append(channel_id)
            save_subscriptions(subscriptions)
            await ctx.send(f"Subscribed to {WEIBO_ACCOUNTS[username]['name']}'s Weibo posts!")
        else:
            await ctx.send(f"This channel is already subscribed to {WEIBO_ACCOUNTS[username]['name']}'s Weibo posts.")
            
    except Exception as e:
        logger.error(f"Error in subscribe command: {str(e)}")
        await ctx.send("An error occurred while subscribing. Please try again later.")

@bot.command(name='unsubscribe')
async def unsubscribe(ctx, username: str):
    """Unsubscribe the current channel from a Weibo account's posts."""
    if username not in WEIBO_ACCOUNTS:
        available_accounts = ', '.join(WEIBO_ACCOUNTS.keys())
        await ctx.send(f"Unknown account: {username}. Available accounts: {available_accounts}")
        return
        
    try:
        # Get current subscriptions
        subscription_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'subscriptions.json')
        
        if not os.path.exists(subscription_file):
            await ctx.send(f"This channel is not subscribed to {WEIBO_ACCOUNTS[username]['name']}'s Weibo posts.")
            return
            
        with open(subscription_file, 'r') as f:
            subscriptions = json.load(f)
            
        # Remove the current channel from the subscriptions
        channel_id = str(ctx.channel.id)
        if username in subscriptions and channel_id in subscriptions[username]:
            subscriptions[username].remove(channel_id)
            save_subscriptions(subscriptions)
            await ctx.send(f"Unsubscribed from {WEIBO_ACCOUNTS[username]['name']}'s Weibo posts.")
        else:
            await ctx.send(f"This channel is not subscribed to {WEIBO_ACCOUNTS[username]['name']}'s Weibo posts.")
            
    except Exception as e:
        logger.error(f"Error in unsubscribe command: {str(e)}")
        await ctx.send("An error occurred while unsubscribing. Please try again later.")

@bot.command(name='list')
async def list_accounts(ctx):
    """List all available Weibo accounts."""
    embed = discord.Embed(
        title="Available Weibo Accounts",
        description="Here are all the Weibo accounts you can subscribe to:",
        color=EMBED_COLOR
    )
    
    for username, account in WEIBO_ACCOUNTS.items():
        embed.add_field(
            name=f"{account['name']} ({username})",
            value=f"Weibo ID: {account['weibo_id']}\nDescription: {account['description']}",
            inline=False
        )
    
    embed.set_footer(text=f"Use {COMMAND_PREFIX}subscribe <username> to subscribe to an account.")
    await ctx.send(embed=embed)

@bot.command(name='subscriptions')
async def list_subscriptions(ctx):
    """List all subscriptions for the current channel."""
    try:
        # Get current subscriptions
        subscription_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'subscriptions.json')
        
        if not os.path.exists(subscription_file):
            await ctx.send("This channel is not subscribed to any Weibo accounts.")
            return
            
        with open(subscription_file, 'r') as f:
            subscriptions = json.load(f)
            
        # Find subscriptions for the current channel
        channel_id = str(ctx.channel.id)
        channel_subscriptions = []
        
        for username, channels in subscriptions.items():
            if channel_id in channels:
                channel_subscriptions.append(username)
                
        if not channel_subscriptions:
            await ctx.send("This channel is not subscribed to any Weibo accounts.")
            return
            
        # Create an embed with the subscriptions
        embed = discord.Embed(
            title="Channel Subscriptions",
            description="This channel is subscribed to the following Weibo accounts:",
            color=EMBED_COLOR
        )
        
        for username in channel_subscriptions:
            account = WEIBO_ACCOUNTS[username]
            embed.add_field(
                name=f"{account['name']} ({username})",
                value=f"Weibo ID: {account['weibo_id']}\nDescription: {account['description']}",
                inline=False
            )
        
        embed.set_footer(text=f"Use {COMMAND_PREFIX}unsubscribe <username> to unsubscribe from an account.")
        await ctx.send(embed=embed)
            
    except Exception as e:
        logger.error(f"Error in subscriptions command: {str(e)}")
        await ctx.send("An error occurred while fetching subscriptions. Please try again later.")

@bot.command(name='latest')
async def latest_posts(ctx, username: str):
    """Show the latest posts from a Weibo account."""
    if username not in WEIBO_ACCOUNTS:
        available_accounts = ', '.join(WEIBO_ACCOUNTS.keys())
        await ctx.send(f"Unknown account: {username}. Available accounts: {available_accounts}")
        return
        
    try:
        # Fetch the latest posts
        posts = weibo_fetcher.fetch_posts(username, force_refresh=True)
        
        if not posts:
            await ctx.send(f"No posts found for {WEIBO_ACCOUNTS[username]['name']}.")
            return
            
        # Send the latest posts
        await ctx.send(f"Latest posts from {WEIBO_ACCOUNTS[username]['name']}:")
        
        for post in posts[:3]:  # Show up to 3 latest posts
            embed = create_post_embed(post)
            await ctx.send(embed=embed)
            
    except Exception as e:
        logger.error(f"Error in latest command: {str(e)}")
        await ctx.send("An error occurred while fetching the latest posts. Please try again later.")

@bot.command(name='help')
async def help_command(ctx):
    """Show help information for the bot."""
    embed = discord.Embed(
        title="SNH48 Weibo Bot Help",
        description="This bot fetches and displays Weibo posts from SNH48 members and related accounts.",
        color=EMBED_COLOR
    )
    
    embed.add_field(
        name=f"{COMMAND_PREFIX}subscribe <username>",
        value="Subscribe the current channel to a Weibo account's posts.",
        inline=False
    )
    
    embed.add_field(
        name=f"{COMMAND_PREFIX}unsubscribe <username>",
        value="Unsubscribe the current channel from a Weibo account's posts.",
        inline=False
    )
    
    embed.add_field(
        name=f"{COMMAND_PREFIX}list",
        value="List all available Weibo accounts.",
        inline=False
    )
    
    embed.add_field(
        name=f"{COMMAND_PREFIX}subscriptions",
        value="List all subscriptions for the current channel.",
        inline=False
    )
    
    embed.add_field(
        name=f"{COMMAND_PREFIX}latest <username>",
        value="Show the latest posts from a Weibo account.",
        inline=False
    )
    
    embed.add_field(
        name=f"{COMMAND_PREFIX}help",
        value="Show this help message.",
        inline=False
    )
    
    embed.set_footer(text=EMBED_FOOTER)
    await ctx.send(embed=embed)

def run_bot():
    """Run the Discord bot."""
    bot.run(DISCORD_TOKEN)

if __name__ == '__main__':
    run_bot()
