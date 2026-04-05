import discord
from discord.ext import commands
from discord import app_commands
import database as db


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_owner():
        async def predicate(ctx):
            return await ctx.bot.is_owner(ctx.author)
        return commands.check(predicate)

    # ── RELOAD ────────────────────────────────────────────────────────────────

    @commands.command(name="reload")
    @commands.is_owner()
    async def reload(self, ctx, cog: str):
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
            await ctx.send(f"Cog `{cog}` reloadovan.")
        except Exception as e:
            await ctx.send(f"Chyba pri reloadu `{cog}`: {e}")

    # ── SETLOG ────────────────────────────────────────────────────────────────

    @commands.command(name="setlog")
    @commands.has_permissions(administrator=True)
    async def setlog(self, ctx, channel: discord.TextChannel):
        await db.set_guild_setting(ctx.guild.id, "log_channel_id", channel.id)
        await ctx.send(f"Log kanal nastaven na {channel.mention}.")

    @app_commands.command(name="setlog", description="Nastavi log kanal")
    @app_commands.describe(channel="Log kanal")
    @app_commands.checks.has_permissions(administrator=True)
    async def setlog_slash(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await db.set_guild_setting(interaction.guild.id, "log_channel_id", channel.id)
        await interaction.response.send_message(f"Log kanal nastaven na {channel.mention}.")


async def setup(bot):
    await bot.add_cog(Admin(bot))
