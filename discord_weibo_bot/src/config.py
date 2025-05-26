# Configuration file for the Discord Weibo Bot

# Discord Bot Token (to be replaced with actual token)
DISCORD_TOKEN = "YOUR_DISCORD_BOT_TOKEN"

# Command prefix for the bot
COMMAND_PREFIX = "!"

# Weibo accounts to track
WEIBO_ACCOUNTS = {
    "yangbingyi": {
        "name": "Yang Bingyi",
        "weibo_id": "SNH48-杨冰怡",
        "numeric_id": None,  # Will be filled during runtime if needed
        "description": "SNH48 member"
    },
    "linshuqing": {
        "name": "Lin Shuqing",
        "weibo_id": "SNH48-林舒晴",
        "numeric_id": "6371378471",
        "description": "SNH48 member"
    },
    "yuanyiqi": {
        "name": "Yuan Yiqi",
        "weibo_id": "袁一琦each",
        "numeric_id": "6021695822",
        "description": "SNH48 member"
    },
    "baixinyu": {
        "name": "Bai Xinyu",
        "weibo_id": "SNH48-柏欣妤",
        "numeric_id": None,
        "description": "SNH48 member"
    },
    "zhengdanni": {
        "name": "Zheng Danni",
        "weibo_id": "郑丹妮_",
        "numeric_id": "5887697249",
        "description": "SNH48 member"
    },
    "snh48": {
        "name": "SNH48 Official",
        "weibo_id": "SNH48",
        "numeric_id": "2689280541",
        "description": "SNH48 official account"
    },
    "gnz48": {
        "name": "GNZ48 Official",
        "weibo_id": "GNZ48",
        "numeric_id": "5675361083",
        "description": "GNZ48 official account"
    },
    "mango_cumquat": {
        "name": "Mango_Cumquat",
        "weibo_id": "Mango_Cumquat",
        "numeric_id": "7761857762",
        "description": "SNH48 fan account"
    }
}

# Weibo API settings
WEIBO_API_BASE_URL = "https://m.weibo.cn/api/container/getIndex"

# Cache settings
CACHE_DURATION = 300  # 5 minutes in seconds

# Fetch interval (in seconds)
FETCH_INTERVAL = 600  # 10 minutes

# Maximum number of posts to fetch per account
MAX_POSTS_PER_ACCOUNT = 5

# Discord embed settings
EMBED_COLOR = 0x1DA1F2  # Twitter blue color
EMBED_FOOTER = "SNH48 Weibo Bot"
