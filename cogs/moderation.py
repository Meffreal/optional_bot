import discord
from discord.ext import commands
from discord import app_commands
import database as db
from datetime import timedelta
import re


def parse_duration(text: str) -> timedelta | None:
    match = re.fullmatch(r"(\d+)([smhd])", text.strip().lower())
    if not match:
        return None
    value, unit = int(match.group(1)), match.group(2)
    return {"s": timedelta(seconds=value), "m": timedelta(minutes=value),
            "h": timedelta(hours=value), "d": timedelta(days=value)}[unit]


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── BAN ──────────────────────────────────────────────────────────────────

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "Bez důvodu"):
        await member.ban(reason=reason)
        embed = discord.Embed(title="Banned", description=f"{member.mention} byl zabanován.\n**Důvod:** {reason}", color=discord.Color.red())
        await ctx.send(embed=embed)

    @app_commands.command(name="ban", description="Zabanuje člena serveru")
    @app_commands.describe(member="Člen k zabanování", reason="Důvod banu")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "Bez důvodu"):
        await member.ban(reason=reason)
        embed = discord.Embed(title="Banned", description=f"{member.mention} byl zabanován.\n**Důvod:** {reason}", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)

    # ── KICK ─────────────────────────────────────────────────────────────────

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "Bez důvodu"):
        await member.kick(reason=reason)
        embed = discord.Embed(title="Kicked", description=f"{member.mention} byl vykopnut.\n**Důvod:** {reason}", color=discord.Color.orange())
        await ctx.send(embed=embed)

    @app_commands.command(name="kick", description="Vykopne člena ze serveru")
    @app_commands.describe(member="Člen k vykopnutí", reason="Důvod")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "Bez důvodu"):
        await member.kick(reason=reason)
        embed = discord.Embed(title="Kicked", description=f"{member.mention} byl vykopnut.\n**Důvod:** {reason}", color=discord.Color.orange())
        await interaction.response.send_message(embed=embed)

    # ── TIMEOUT ───────────────────────────────────────────────────────────────

    @commands.command(name="timeout", aliases=["mute"])
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, duration: str, *, reason: str = "Bez důvodu"):
        delta = parse_duration(duration)
        if not delta:
            return await ctx.send("Neplatný formát doby. Použij např. `10m`, `2h`, `1d`.")
        await member.timeout(delta, reason=reason)
        embed = discord.Embed(title="Timeout", description=f"{member.mention} dostal timeout na **{duration}**.\n**Důvod:** {reason}", color=discord.Color.gold())
        await ctx.send(embed=embed)

    @app_commands.command(name="timeout", description="Dá členovi timeout")
    @app_commands.describe(member="Člen", duration="Délka (10m, 2h, 1d...)", reason="Důvod")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout_slash(self, interaction: discord.Interaction, member: discord.Member, duration: str, reason: str = "Bez důvodu"):
        delta = parse_duration(duration)
        if not delta:
            return await interaction.response.send_message("Neplatný formát doby. Použij např. `10m`, `2h`, `1d`.", ephemeral=True)
        await member.timeout(delta, reason=reason)
        embed = discord.Embed(title="Timeout", description=f"{member.mention} dostal timeout na **{duration}**.\n**Důvod:** {reason}", color=discord.Color.gold())
        await interaction.response.send_message(embed=embed)

    # ── WARN ──────────────────────────────────────────────────────────────────

    @commands.command(name="warn")
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str = "Bez důvodu"):
        warn_id = await db.add_warning(ctx.guild.id, member.id, ctx.author.id, reason)
        warnings = await db.get_warnings(ctx.guild.id, member.id)
        embed = discord.Embed(title="Warning", description=f"{member.mention} dostal varování #{warn_id}.\n**Důvod:** {reason}\n**Celkem varování:** {len(warnings)}", color=discord.Color.yellow())
        await ctx.send(embed=embed)

    @app_commands.command(name="warn", description="Dá členovi varování")
    @app_commands.describe(member="Člen", reason="Důvod")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "Bez důvodu"):
        warn_id = await db.add_warning(interaction.guild.id, member.id, interaction.user.id, reason)
        warnings = await db.get_warnings(interaction.guild.id, member.id)
        embed = discord.Embed(title="Warning", description=f"{member.mention} dostal varování #{warn_id}.\n**Důvod:** {reason}\n**Celkem varování:** {len(warnings)}", color=discord.Color.yellow())
        await interaction.response.send_message(embed=embed)

    # ── WARNINGS ──────────────────────────────────────────────────────────────

    @commands.command(name="warnings", aliases=["warns"])
    @commands.has_permissions(moderate_members=True)
    async def warnings(self, ctx, member: discord.Member):
        warns = await db.get_warnings(ctx.guild.id, member.id)
        if not warns:
            return await ctx.send(f"{member.mention} nemá žádná varování.")
        embed = discord.Embed(title=f"Varování - {member.display_name}", color=discord.Color.yellow())
        for w in warns:
            embed.add_field(name=f"#{w['id']} | {w['created_at'][:10]}", value=f"**Důvod:** {w['reason']}", inline=False)
        await ctx.send(embed=embed)

    @app_commands.command(name="warnings", description="Zobrazí varování člena")
    @app_commands.describe(member="Člen")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warnings_slash(self, interaction: discord.Interaction, member: discord.Member):
        warns = await db.get_warnings(interaction.guild.id, member.id)
        if not warns:
            return await interaction.response.send_message(f"{member.mention} nemá žádná varování.", ephemeral=True)
        embed = discord.Embed(title=f"Varování - {member.display_name}", color=discord.Color.yellow())
        for w in warns:
            embed.add_field(name=f"#{w['id']} | {w['created_at'][:10]}", value=f"**Důvod:** {w['reason']}", inline=False)
        await interaction.response.send_message(embed=embed)

    # ── CLEARWARNS ────────────────────────────────────────────────────────────

    @commands.command(name="clearwarns")
    @commands.has_permissions(moderate_members=True)
    async def clearwarns(self, ctx, member: discord.Member):
        count = await db.clear_warnings(ctx.guild.id, member.id)
        await ctx.send(f"Smazáno **{count}** varování pro {member.mention}.")

    @app_commands.command(name="clearwarns", description="Smaže všechna varování člena")
    @app_commands.describe(member="Člen")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def clearwarns_slash(self, interaction: discord.Interaction, member: discord.Member):
        count = await db.clear_warnings(interaction.guild.id, member.id)
        await interaction.response.send_message(f"Smazáno **{count}** varování pro {member.mention}.")

    # ── PURGE ─────────────────────────────────────────────────────────────────

    @commands.command(name="purge", aliases=["clear"])
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount + 1)
        msg = await ctx.send(f"Smazáno **{amount}** zpráv.", delete_after=3)

    @app_commands.command(name="purge", description="Smaže zprávy v kanálu")
    @app_commands.describe(amount="Počet zpráv ke smazání")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def purge_slash(self, interaction: discord.Interaction, amount: int):
        await interaction.response.defer(ephemeral=True)
        await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"Smazáno **{amount}** zpráv.", ephemeral=True)

    # ── SLOWMODE ──────────────────────────────────────────────────────────────

    @commands.command(name="slowmode")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int):
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.send(f"Slowmode nastaven na **{seconds}s**." if seconds > 0 else "Slowmode vypnut.")

    @app_commands.command(name="slowmode", description="Nastaví slowmode v kanálu")
    @app_commands.describe(seconds="Počet sekund (0 = vypnout)")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def slowmode_slash(self, interaction: discord.Interaction, seconds: int):
        await interaction.channel.edit(slowmode_delay=seconds)
        await interaction.response.send_message(f"Slowmode nastaven na **{seconds}s**." if seconds > 0 else "Slowmode vypnut.")

    # ── LOCK / UNLOCK ─────────────────────────────────────────────────────────

    @commands.command(name="lock")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send("Kanál uzamcen.")

    @commands.command(name="unlock")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=None)
        await ctx.send("Kanál odemcen.")

    @app_commands.command(name="lock", description="Uzamkne kanál")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def lock_slash(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
        await interaction.response.send_message("Kanál uzamcen.")

    @app_commands.command(name="unlock", description="Odemkne kanál")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def unlock_slash(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=None)
        await interaction.response.send_message("Kanál odemcen.")

    # ── ERROR HANDLERS ────────────────────────────────────────────────────────

    @ban.error
    @kick.error
    @timeout.error
    @warn.error
    @warnings.error
    @clearwarns.error
    @purge.error
    @slowmode.error
    @lock.error
    @unlock.error
    async def mod_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nemáš oprávnění k tomuto příkazu.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("Člen nenalezen.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Chybí argument: `{error.param.name}`")
        else:
            await ctx.send(f"Chyba: {error}")


async def setup(bot):
    await bot.add_cog(Moderation(bot))
