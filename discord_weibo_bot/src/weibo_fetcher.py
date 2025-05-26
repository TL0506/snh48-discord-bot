import requests
import time
import json
import logging
from typing import Dict, List, Optional, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('weibo_fetcher')

class WeiboFetcher:
    """Class to fetch posts from Weibo accounts."""
    
    def __init__(self, config: Dict):
        """Initialize the WeiboFetcher with configuration."""
        self.config = config
        self.weibo_accounts = config['WEIBO_ACCOUNTS']
        self.api_base_url = config['WEIBO_API_BASE_URL']
        self.max_posts = config['MAX_POSTS_PER_ACCOUNT']
        self.cache = {}
        self.cache_duration = config['CACHE_DURATION']
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        
    def get_user_info(self, username: str) -> Optional[Dict]:
        """Get user information for a Weibo account."""
        if username not in self.weibo_accounts:
            logger.error(f"Unknown Weibo account: {username}")
            return None
            
        account_info = self.weibo_accounts[username]
        
        # If we already have the numeric ID, return the account info
        if account_info['numeric_id']:
            return account_info
            
        # Otherwise, try to fetch the numeric ID
        try:
            # For accounts where we only have the display name, we need to search
            search_url = f"https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D3%26q%3D{account_info['weibo_id']}&page_type=searchall"
            headers = {'User-Agent': self.user_agent}
            
            response = requests.get(search_url, headers=headers)
            data = response.json()
            
            if data['ok'] == 1 and 'cards' in data['data']:
                for card in data['data']['cards']:
                    if card.get('card_type') == 11 and 'card_group' in card:
                        for user in card['card_group']:
                            if user.get('user', {}).get('screen_name') == account_info['weibo_id']:
                                account_info['numeric_id'] = user['user']['id']
                                return account_info
            
            logger.warning(f"Could not find numeric ID for {username} ({account_info['weibo_id']})")
            return account_info
            
        except Exception as e:
            logger.error(f"Error fetching user info for {username}: {str(e)}")
            return account_info
    
    def fetch_posts(self, username: str, force_refresh: bool = False) -> List[Dict]:
        """Fetch posts for a specific Weibo account."""
        # Check cache first if not forcing refresh
        if not force_refresh and username in self.cache:
            cache_time, posts = self.cache[username]
            if time.time() - cache_time < self.cache_duration:
                logger.info(f"Using cached posts for {username}")
                return posts
        
        # Get user info
        user_info = self.get_user_info(username)
        if not user_info:
            return []
            
        # If we don't have a numeric ID, we can't fetch posts
        if not user_info['numeric_id']:
            logger.warning(f"No numeric ID available for {username}, cannot fetch posts")
            return []
            
        try:
            # Construct the API URL
            user_id = user_info['numeric_id']
            container_id = f"107603{user_id}"
            url = f"{self.api_base_url}?type=uid&value={user_id}&containerid={container_id}"
            
            headers = {'User-Agent': self.user_agent}
            response = requests.get(url, headers=headers)
            data = response.json()
            
            if data['ok'] != 1:
                logger.error(f"Error fetching posts for {username}: {data.get('msg', 'Unknown error')}")
                return []
                
            posts = []
            if 'cards' in data['data']:
                for card in data['data']['cards']:
                    # Only process blog posts (card_type 9)
                    if card.get('card_type') == 9:
                        post = self._parse_post(card, user_info)
                        if post:
                            posts.append(post)
                            if len(posts) >= self.max_posts:
                                break
            
            # Update cache
            self.cache[username] = (time.time(), posts)
            logger.info(f"Fetched {len(posts)} posts for {username}")
            return posts
            
        except Exception as e:
            logger.error(f"Error fetching posts for {username}: {str(e)}")
            return []
    
    def _parse_post(self, card: Dict, user_info: Dict) -> Optional[Dict]:
        """Parse a Weibo post from the API response."""
        try:
            mblog = card.get('mblog', {})
            if not mblog:
                return None
                
            # Extract basic post info
            post = {
                'id': mblog.get('id', ''),
                'created_at': mblog.get('created_at', ''),
                'text': mblog.get('text', ''),
                'source': mblog.get('source', ''),
                'reposts_count': mblog.get('reposts_count', 0),
                'comments_count': mblog.get('comments_count', 0),
                'attitudes_count': mblog.get('attitudes_count', 0),  # likes
                'user': {
                    'id': user_info['numeric_id'],
                    'screen_name': user_info['weibo_id'],
                    'name': user_info['name'],
                    'description': user_info['description']
                },
                'url': f"https://m.weibo.cn/detail/{mblog.get('id', '')}",
                'images': []
            }
            
            # Extract images if available
            if 'pics' in mblog:
                for pic in mblog['pics']:
                    if 'large' in pic:
                        post['images'].append(pic['large']['url'])
                    elif 'url' in pic:
                        post['images'].append(pic['url'])
            
            # Handle retweeted content
            if 'retweeted_status' in mblog:
                retweeted = mblog['retweeted_status']
                post['retweeted'] = {
                    'id': retweeted.get('id', ''),
                    'created_at': retweeted.get('created_at', ''),
                    'text': retweeted.get('text', ''),
                    'user': {
                        'screen_name': retweeted.get('user', {}).get('screen_name', 'Unknown')
                    }
                }
                
                # Extract retweeted images if available
                if 'pics' in retweeted:
                    post['retweeted']['images'] = []
                    for pic in retweeted['pics']:
                        if 'large' in pic:
                            post['retweeted']['images'].append(pic['large']['url'])
                        elif 'url' in pic:
                            post['retweeted']['images'].append(pic['url'])
            
            return post
            
        except Exception as e:
            logger.error(f"Error parsing post: {str(e)}")
            return None
    
    def fetch_all_posts(self, force_refresh: bool = False) -> Dict[str, List[Dict]]:
        """Fetch posts for all configured Weibo accounts."""
        all_posts = {}
        for username in self.weibo_accounts:
            all_posts[username] = self.fetch_posts(username, force_refresh)
        return all_posts
