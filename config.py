# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    TELEGRAM_CHANNEL = os.getenv("TELEGRAM_CHANNEL")
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    DISCORD_CHANNEL = os.getenv("DISCORD_CHANNEL")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    SERPAPI_KEY = os.getenv("SERPAPI_KEY")
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Logging configuration
    LOG_FILE = "logs/cyber_tricks_bot.log"
    LOG_LEVEL = "INFO"
    
    # API endpoints
    GITHUB_API = "https://api.github.com"
    SERPAPI_URL = "https://serpapi.com/search"
    
    # Data collection settings
    SEARCH_QUERIES = [
        "penetration testing tools",
        "white hat hacking commands",
        "cybersecurity tabletop exercises",
        "programming tricks python"
    ]
    MAX_REPOS = 10
    SCRAPE_URLS = [
        "https://book.hacktricks.wiki/pentesting",
        "https://owasp.org/www-project-web-security-testing-guide/"
    ]

    @staticmethod
    def validate():
        required = [
            Config.TELEGRAM_TOKEN, Config.TELEGRAM_CHANNEL,
            Config.DISCORD_TOKEN, Config.DISCORD_CHANNEL,
            Config.GITHUB_TOKEN, Config.SERPAPI_KEY
        ]
        if not all(required):
            raise ValueError("Missing required environment variables")
