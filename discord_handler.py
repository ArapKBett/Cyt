# discord_handler.py
import discord
from discord.ext import commands
from loguru import logger
from config import Config
from database import Database
from typing import Optional

class DiscordBot:
    def __init__(self):
        self.token = Config.DISCORD_TOKEN
        self.channel_id = int(Config.DISCORD_CHANNEL)
        intents = discord.Intents.default()
        intents.message_content = True
        self.bot = commands.Bot(command_prefix="/", intents=intents)
        self.db = Database()
        self._setup_commands()
        self._setup_logging()

    def _setup_logging(self):
        logger.add(Config.LOG_FILE, level=Config.LOG_LEVEL, rotation="10 MB")

    def _setup_commands(self):
        @self.bot.command(name="tool")
        async def tool_command(ctx, tool: str = "nmap"):
            resources = self.db.get_resources({"type": "search_result", "title": {"$regex": tool, "$options": "i"}})
            embed = discord.Embed(title=f"Tool: {tool}", color=discord.Color.blue())
            if resources:
                embed.description = f"{resources[0]['description']}\n**Source**: {resources[0]['source']}"
            else:
                embed.description = f"No information found for {tool}\nExample: `nmap -sS -p- target.com`"
            await ctx.send(embed=embed)
            logger.info(f"Processed /tool command for {tool}")

        @self.bot.command(name="command")
        async def command_command(ctx, tool: str = "metasploit"):
            resources = self.db.get_resources({"type": "command", "description": {"$regex": tool, "$options": "i"}})
            embed = discord.Embed(title=f"Command for {tool}", color=discord.Color.green())
            if resources:
                embed.description = f"```{resources[0]['description']}```\n**Source**: {resources[0]['source']}"
            else:
                embed.description = f"No commands found for {tool}\nExample: `msfconsole -q`"
            await ctx.send(embed=embed)
            logger.info(f"Processed /command command for {tool}")

        @self.bot.command(name="code")
        async def code_command(ctx, topic: str = "port_scanner"):
            resources = self.db.get_resources({"type": "code", "title": {"$regex": topic, "$options": "i"}})
            embed = discord.Embed(title=f"Code: {topic}", color=discord.Color.purple())
            if resources:
                embed.description = f"```python\n{resources[0]['description']}```\n**Source**: {resources[0]['source']}"
            else:
                embed.description = f"No code snippets found for {topic}\nExample: `import socket`"
            await ctx.send(embed=embed)
            logger.info(f"Processed /code command for {topic}")

        @self.bot.command(name="tabletop")
        async def tabletop_command(ctx):
            resources = self.db.get_resources({"title": {"$regex": "tabletop", "$options": "i"}})
            embed = discord.Embed(title="Tabletop Exercise", color=discord.Color.red())
            if resources:
                embed.description = f"{resources[0]['description']}\n**Source**: {resources[0]['source']}"
            else:
                embed.description = "No tabletop exercises found\nExample: Simulate a phishing attack response."
            await ctx.send(embed=embed)
            logger.info("Processed /tabletop command")

    async def post_to_channel(self, resource: Dict) -> Optional[discord.Embed]:
        try:
            embed = discord.Embed(title=resource["title"], description=resource["description"], color=discord.Color.blue())
            if resource["type"] == "code":
                embed.description = f"```python\n{resource['description']}```"
            embed.add_field(name="Source", value=resource["source"], inline=False)
            channel = self.bot.get_channel(self.channel_id)
            await channel.send(embed=embed)
            logger.info(f"Posted to Discord channel: {resource['title']}")
            return embed
        except Exception as e:
            logger.error(f"Failed to post to Discord: {e}")
            return None

    def start(self):
        logger.info("Starting Discord bot")
        self.bot.run(self.token)
