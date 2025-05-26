# SNH48 Weibo Discord Bot - User Guide

## Overview
This Discord bot fetches and displays Weibo posts from SNH48 members and related accounts. It allows users to subscribe to specific accounts and receive updates in designated Discord channels.

## Features
- Fetch Weibo posts from SNH48 members, official accounts, and fan accounts
- Subscribe Discord channels to specific Weibo accounts
- Display posts with rich embeds including text, images, and metadata
- Periodic checking for new posts
- On-demand fetching of latest posts

## Supported Accounts
The bot currently supports the following Weibo accounts:
- Yang Bingyi (SNH48-杨冰怡)
- Lin Shuqing (SNH48-林舒晴)
- Yuan Yiqi (袁一琦each)
- Bai Xinyu (SNH48-柏欣妤)
- Zheng Danni (郑丹妮_)
- SNH48 Official (SNH48)
- GNZ48 Official (GNZ48)
- Mango_Cumquat (Fan account)

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- A Discord account and a Discord server where you have admin permissions
- A Discord bot token

### Installation
1. Clone or download this repository to your server
2. Install the required dependencies:
   ```
   pip install discord.py requests beautifulsoup4
   ```
3. Edit the `src/config.py` file:
   - Replace `YOUR_DISCORD_BOT_TOKEN` with your actual Discord bot token
   - Customize other settings as needed (command prefix, fetch interval, etc.)

### Creating a Discord Bot
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" tab and click "Add Bot"
4. Under the "TOKEN" section, click "Copy" to copy your bot token
5. Enable the "Message Content Intent" under Privileged Gateway Intents
6. Use this token in the `config.py` file

### Inviting the Bot to Your Server
1. In the Discord Developer Portal, go to the "OAuth2" tab
2. In the "URL Generator" section, select the "bot" scope
3. Select the following permissions:
   - Read Messages/View Channels
   - Send Messages
   - Embed Links
   - Attach Files
   - Read Message History
4. Copy the generated URL and open it in your browser
5. Select your server and authorize the bot

### Running the Bot
1. Navigate to the bot directory
2. Run the bot:
   ```
   python src/main.py
   ```
3. For continuous operation, consider using a process manager like PM2 or a systemd service

## Bot Commands
- `!subscribe <username>` - Subscribe the current channel to a Weibo account's posts
- `!unsubscribe <username>` - Unsubscribe the current channel from a Weibo account's posts
- `!list` - List all available Weibo accounts
- `!subscriptions` - List all subscriptions for the current channel
- `!latest <username>` - Show the latest posts from a Weibo account
- `!help` - Show help information for the bot

## Example Usage
1. Invite the bot to your server
2. In a channel, type `!list` to see all available accounts
3. Subscribe to an account with `!subscribe yangbingyi`
4. Check the latest posts with `!latest yangbingyi`
5. The bot will automatically post new updates to subscribed channels

## Troubleshooting
- If the bot doesn't respond, check if it's online and has the correct permissions
- If posts aren't being fetched, check the console logs for errors
- For any issues, check the `discord_weibo_bot.log` file for detailed error messages

## Customization
You can customize the bot by editing the following files:
- `src/config.py` - Bot configuration, including accounts to track
- `src/discord_bot.py` - Discord bot functionality
- `src/weibo_fetcher.py` - Weibo post fetching logic

## Adding More Accounts
To add more accounts, edit the `WEIBO_ACCOUNTS` dictionary in `src/config.py`:
```python
"new_account": {
    "name": "Display Name",
    "weibo_id": "Weibo-Username",
    "numeric_id": "1234567890",  # Numeric Weibo ID
    "description": "Description"
}
```

## License
This project is provided as-is with no warranty. You are free to modify and distribute it as needed.
