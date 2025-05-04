# telegram_handler.py
from telegram.ext import Application, CommandHandler
from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger
from config import Config
from database import Database
import asyncio
from typing import Optional

class TelegramBot:
    def __init__(self):
        self.token = Config.TELEGRAM_TOKEN
        self.channel_id = Config.TELEGRAM_CHANNEL
        self.app = Application.builder().token(self.token).build()
        self.db = Database()
        self._setup_handlers()
        self._setup_logging()

    def _setup_logging(self):
        logger.add(Config.LOG_FILE, level=Config.LOG_LEVEL, rotation="10 MB")

    def _setup_handlers(self):
        self.app.add_handler(CommandHandler("tool", self.tool_command))
        self.app.add_handler(CommandHandler("command", self.command_command))
        self.app.add_handler(CommandHandler("code", self.code_command))
        self.app.add_handler(CommandHandler("tabletop", self.tabletop_command))

    async def tool_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        tool = context.args[0] if context.args else "nmap"
        resources = self.db.get_resources({"type": "search_result", "title": {"$regex": tool, "$options": "i"}})
        if resources:
            message = f"**Tool: {tool}**\nDescription: {resources[0]['description']}\nSource: {resources[0]['source']}"
        else:
            message = f"No information found for tool: {tool}\nExample: `nmap -sS -p- target.com`"
        await update.message.reply_text(message, parse_mode="Markdown")
        logger.info(f"Processed /tool command for {tool}")

    async def command_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        tool = context.args[0] if context.args else "metasploit"
        resources = self.db.get_resources({"type": "command", "description": {"$regex": tool, "$options": "i"}})
        if resources:
            message = f"**Command for {tool}**\n{resources[0]['description']}\nSource: {resources[0]['source']}"
        else:
            message = f"No commands found for {tool}\nExample: `msfconsole -q`"
        await update.message.reply_text(message, parse_mode="Markdown")
        logger.info(f"Processed /command command for {tool}")

    async def code_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        topic = context.args[0] if context.args else "port_scanner"
        resources = self.db.get_resources({"type": "code", "title": {"$regex": topic, "$options": "i"}})
        if resources:
            message = f"**Code: {resources[0]['title']}**\n```python\n{resources[0]['description']}\n```\nSource: {resources[0]['source']}"
        else:
            message = f"No code snippets found for {topic}\nExample: `import socket`"
        await update.message.reply_text(message, parse_mode="Markdown")
        logger.info(f"Processed /code command for {topic}")

    async def tabletop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        resources = self.db.get_resources({"title": {"$regex": "tabletop", "$options": "i"}})
        if resources:
            message = f"**Tabletop Exercise**\n{resources[0]['description']}\nSource: {resources[0]['source']}"
        else:
            message = "No tabletop exercises found\nExample: Simulate a phishing attack response."
        await update.message.reply_text(message, parse_mode="Markdown")
        logger.info("Processed /tabletop command")

    async def post_to_channel(self, resource: Dict) -> Optional[str]:
        try:
            message = f"**{resource['title']}**\n{resource['description']}\nSource: {resource['source']}"
            if resource["type"] == "code":
                message = f"**{resource['title']}**\n```python\n{resource['description']}\n```\nSource: {resource['source']}"
            await self.app.bot.send_message(chat_id=self.channel_id, text=message, parse_mode="Markdown")
            logger.info(f"Posted to Telegram channel: {resource['title']}")
            return message
        except Exception as e:
            logger.error(f"Failed to post to Telegram: {e}")
            return None

    def start(self):
        logger.info("Starting Telegram bot")
        self.app.run_polling()
