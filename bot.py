# bot.py
import asyncio
from loguru import logger
from config import Config
from telegram_handler import TelegramBot
from discord_handler import DiscordBot
from database import Database
import threading

def setup_logging():
    logger.add(Config.LOG_FILE, level=Config.LOG_LEVEL, rotation="10 MB")

def run_telegram_bot():
    telegram_bot = TelegramBot()
    telegram_bot.start()

def run_discord_bot():
    discord_bot = DiscordBot()
    discord_bot.start()

def main():
    setup_logging()
    logger.info("Starting Cyber Tricks Bot")
    
    Config.validate()
    
    # Initialize database
    db = Database()
    
    # Run bots in separate threads
    telegram_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    discord_thread = threading.Thread(target=run_discord_bot, daemon=True)
    
    telegram_thread.start()
    discord_thread.start()
    
    try:
        # Keep main thread alive
        while True:
            asyncio.run(asyncio.sleep(1))
    except KeyboardInterrupt:
        logger.info("Shutting down bot")
        db.close()

if __name__ == "__main__":
    main()
