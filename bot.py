import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from database import init_db

load_dotenv()

TOKEN = os.getenv("TOKEN")
PREFIX = os.getenv("PREFIX", ".")

COGS = [
    "cogs.moderation",
    "cogs.utility",
    "cogs.admin",
]


class OptionalBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix=PREFIX,
            intents=intents,
            help_command=None,
        )

    async def setup_hook(self):
        await init_db()
        for cog in COGS:
            try:
                await self.load_extension(cog)
                print(f"[OK] Loaded {cog}")
            except Exception as e:
                print(f"[ERR] Failed to load {cog}: {e}")
        await self.tree.sync()
        print("[OK] Slash commands synced")

    async def on_ready(self):
        print(f"[BOT] Logged in as {self.user} ({self.user.id})")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{PREFIX}help | Optional Bot"
            )
        )


bot = OptionalBot()


@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(
        title="Optional Bot - Help",
        description=f"Prefix: `{PREFIX}` | Slash commands: `/`",
        color=discord.Color.blurple()
    )
    embed.add_field(
        name="Moderation",
        value="`ban` `kick` `timeout` `warn` `warnings` `clearwarns` `purge` `slowmode` `lock` `unlock`",
        inline=False
    )
    embed.add_field(
        name="Utility",
        value="`ping` `serverinfo` `userinfo` `avatar` `uptime`",
        inline=False
    )
    embed.add_field(
        name="Admin",
        value="`reload` `setlog`",
        inline=False
    )
    embed.set_footer(text="Optional Bot")
    await ctx.send(embed=embed)


bot.run(TOKEN)
