import sys
import os
import json
import logging
from typing import Dict, List, Optional

# Add the parent directory to sys.path to import config and weibo_fetcher
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.weibo_fetcher import WeiboFetcher
from src.config import WEIBO_ACCOUNTS

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_fetcher')

def test_weibo_fetcher():
    """Test the WeiboFetcher class by fetching posts for all accounts."""
    # Create configuration dictionary for the WeiboFetcher
    config = {
        'WEIBO_ACCOUNTS': WEIBO_ACCOUNTS,
        'WEIBO_API_BASE_URL': 'https://m.weibo.cn/api/container/getIndex',
        'CACHE_DURATION': 300,  # 5 minutes
        'MAX_POSTS_PER_ACCOUNT': 3
    }
    
    # Initialize the WeiboFetcher
    weibo_fetcher = WeiboFetcher(config)
    
    # Test fetching posts for each account
    results = {}
    
    for username, account_info in WEIBO_ACCOUNTS.items():
        logger.info(f"Testing fetching posts for {username} ({account_info['name']})...")
        
        # Get user info
        user_info = weibo_fetcher.get_user_info(username)
        if not user_info:
            logger.error(f"Failed to get user info for {username}")
            results[username] = {
                'status': 'error',
                'message': 'Failed to get user info',
                'posts': []
            }
            continue
            
        # Fetch posts
        posts = weibo_fetcher.fetch_posts(username, force_refresh=True)
        
        # Log results
        if posts:
            logger.info(f"Successfully fetched {len(posts)} posts for {username}")
            results[username] = {
                'status': 'success',
                'message': f'Fetched {len(posts)} posts',
                'posts': posts
            }
        else:
            logger.warning(f"No posts found for {username}")
            results[username] = {
                'status': 'warning',
                'message': 'No posts found',
                'posts': []
            }
    
    # Save results to a file
    with open('test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    logger.info("Test results saved to test_results.json")
    
    # Print summary
    print("\n=== Test Summary ===")
    for username, result in results.items():
        status_emoji = "✅" if result['status'] == 'success' else "⚠️" if result['status'] == 'warning' else "❌"
        print(f"{status_emoji} {username} ({WEIBO_ACCOUNTS[username]['name']}): {result['message']}")
    
    return results

if __name__ == "__main__":
    test_weibo_fetcher()
