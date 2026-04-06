import discord
from discord.ext import commands
import random

WELCOME_CHANNEL_ID = 1490485785034621154

WELCOME_MESSAGES = [
    "A new hero has entered Azeroth. The raid leader is already nervous.",
    "Welcome! Please note that standing in fire is NOT a healing strategy.",
    "A wild {name} appeared! Someone check if they know what an interrupt is.",
    "{name} just walked in. Guild repair bill incoming.",
    "Everyone say hi to {name}! They claim they never stand in fire. We'll see.",
    "{name} has joined. Current interrupt count on the server: still optional.",
    "Breaking news: {name} has arrived. Tanks are already blaming healers just in case.",
    "{name} joined the server. Leeroy Jenkins has entered the chat.",
    "Welcome {name}! You are not prepared. But neither was anyone else here.",
    "{name} has connected. Please set your loot spec before asking for carries.",
    "A fresh {name} has joined. The guild bank is NOT a free store. Probably.",
    "{name} arrived just in time. We were about to wipe anyway.",
]


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
        if not channel:
            return

        message = random.choice(WELCOME_MESSAGES).format(name=member.display_name)

        embed = discord.Embed(
            description=f"*{message}*",
            color=0xC69B3A,
        )
        embed.set_author(name=f"{member.display_name} joined the server", icon_url=member.display_avatar.url)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Member #{member.guild.member_count}")

        await channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Welcome(bot))
