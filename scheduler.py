# scheduler.py
from celery import Celery
from celery.schedules import crontab
from loguru import logger
from config import Config
from data_collector import DataCollector
from database import Database
from telegram_handler import TelegramBot
from discord_handler import DiscordBot
from typing import List, Dict

app = Celery("cyber_tricks", broker=Config.REDIS_URL, backend=Config.REDIS_URL)
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

app.conf.beat_schedule = {
    "collect-and-post-every-hour": {
        "task": "scheduler.collect_and_post",
        "schedule": crontab(minute=0, hour="*"),
    },
}

def setup_logging():
    logger.add(Config.LOG_FILE, level=Config.LOG_LEVEL, rotation="10 MB")

@app.task
def collect_and_post():
    setup_logging()
    logger.info("Starting scheduled data collection and posting")
    
    collector = DataCollector()
    db = Database()
    telegram_bot = TelegramBot()
    discord_bot = DiscordBot()
    
    resources = collector.collect_all()
    
    for resource in resources:
        db.save_resource(resource)
        telegram_bot.post_to_channel(resource)
        discord_bot.post_to_channel(resource)
    
    db.close()
    logger.info("Completed scheduled task")
