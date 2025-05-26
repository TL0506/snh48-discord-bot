#!/usr/bin/env python3
"""
Main entry point for the Discord Weibo Bot.
This script initializes and runs the Discord bot.
"""

import os
import sys
import logging
from src.discord_bot import run_bot

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('discord_weibo_bot.log')
    ]
)
logger = logging.getLogger('main')

def main():
    """Main function to run the Discord bot."""
    logger.info("Starting Discord Weibo Bot...")
    
    try:
        # Run the Discord bot
        run_bot()
    except Exception as e:
        logger.error(f"Error running Discord bot: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
