import discord
from discord.ext import commands
from discord import app_commands
import database as db
from datetime import timedelta
import re


MOD_ROLE_IDS = {1490485778453889148, 1490485778453889147}


def has_mod_role():
    async def predicate(interaction: discord.Interaction) -> bool:
        user_role_ids = {r.id for r in interaction.user.roles}
        return bool(user_role_ids & MOD_ROLE_IDS)
    return app_commands.check(predicate)


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

    async def cog_check(self, ctx: commands.Context) -> bool:
        user_role_ids = {r.id for r in ctx.author.roles}
        if not user_role_ids & MOD_ROLE_IDS:
            await ctx.send("You don't have permission to use moderation commands.", ephemeral=True)
            return False
        return True

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message("You don't have permission to use moderation commands.", ephemeral=True)

    # ── BAN ──────────────────────────────────────────────────────────────────

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        await member.ban(reason=reason)
        embed = discord.Embed(title="Banned", description=f"{member.mention} has been banned.\n**Reason:** {reason}", color=discord.Color.red())
        await ctx.send(embed=embed)

    @app_commands.command(name="ban", description="Ban a server member")
    @app_commands.describe(member="Member to ban", reason="Reason for the ban")
    @has_mod_role()
    async def ban_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        await member.ban(reason=reason)
        embed = discord.Embed(title="Banned", description=f"{member.mention} has been banned.\n**Reason:** {reason}", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)

    # ── KICK ─────────────────────────────────────────────────────────────────

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        await member.kick(reason=reason)
        embed = discord.Embed(title="Kicked", description=f"{member.mention} has been kicked.\n**Reason:** {reason}", color=discord.Color.orange())
        await ctx.send(embed=embed)

    @app_commands.command(name="kick", description="Kick a server member")
    @app_commands.describe(member="Member to kick", reason="Reason for the kick")
    @has_mod_role()
    async def kick_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        await member.kick(reason=reason)
        embed = discord.Embed(title="Kicked", description=f"{member.mention} has been kicked.\n**Reason:** {reason}", color=discord.Color.orange())
        await interaction.response.send_message(embed=embed)

    # ── TIMEOUT ───────────────────────────────────────────────────────────────

    @commands.command(name="timeout", aliases=["mute"])
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, duration: str, *, reason: str = "No reason provided"):
        delta = parse_duration(duration)
        if not delta:
            return await ctx.send("Invalid duration format. Use e.g. `10m`, `2h`, `1d`.")
        await member.timeout(delta, reason=reason)
        embed = discord.Embed(title="Timeout", description=f"{member.mention} has been timed out for **{duration}**.\n**Reason:** {reason}", color=discord.Color.gold())
        await ctx.send(embed=embed)

    @app_commands.command(name="timeout", description="Timeout a member")
    @app_commands.describe(member="Member to timeout", duration="Duration (10m, 2h, 1d...)", reason="Reason")
    @has_mod_role()
    async def timeout_slash(self, interaction: discord.Interaction, member: discord.Member, duration: str, reason: str = "No reason provided"):
        delta = parse_duration(duration)
        if not delta:
            return await interaction.response.send_message("Invalid duration format. Use e.g. `10m`, `2h`, `1d`.", ephemeral=True)
        await member.timeout(delta, reason=reason)
        embed = discord.Embed(title="Timeout", description=f"{member.mention} has been timed out for **{duration}**.\n**Reason:** {reason}", color=discord.Color.gold())
        await interaction.response.send_message(embed=embed)

    # ── WARN ──────────────────────────────────────────────────────────────────

    @commands.command(name="warn")
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        warn_id = await db.add_warning(ctx.guild.id, member.id, ctx.author.id, reason)
        warnings = await db.get_warnings(ctx.guild.id, member.id)
        embed = discord.Embed(title="Warning", description=f"{member.mention} received warning #{warn_id}.\n**Reason:** {reason}\n**Total warnings:** {len(warnings)}", color=discord.Color.yellow())
        await ctx.send(embed=embed)

    @app_commands.command(name="warn", description="Warn a member")
    @app_commands.describe(member="Member to warn", reason="Reason")
    @has_mod_role()
    async def warn_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        warn_id = await db.add_warning(interaction.guild.id, member.id, interaction.user.id, reason)
        warnings = await db.get_warnings(interaction.guild.id, member.id)
        embed = discord.Embed(title="Warning", description=f"{member.mention} received warning #{warn_id}.\n**Reason:** {reason}\n**Total warnings:** {len(warnings)}", color=discord.Color.yellow())
        await interaction.response.send_message(embed=embed)

    # ── WARNINGS ──────────────────────────────────────────────────────────────

    @commands.command(name="warnings", aliases=["warns"])
    @commands.has_permissions(moderate_members=True)
    async def warnings(self, ctx, member: discord.Member):
        warns = await db.get_warnings(ctx.guild.id, member.id)
        if not warns:
            return await ctx.send(f"{member.mention} has no warnings.")
        embed = discord.Embed(title=f"Warnings - {member.display_name}", color=discord.Color.yellow())
        for w in warns:
            embed.add_field(name=f"#{w['id']} | {w['created_at'][:10]}", value=f"**Reason:** {w['reason']}", inline=False)
        await ctx.send(embed=embed)

    @app_commands.command(name="warnings", description="View a member's warnings")
    @app_commands.describe(member="Member to check")
    @has_mod_role()
    async def warnings_slash(self, interaction: discord.Interaction, member: discord.Member):
        warns = await db.get_warnings(interaction.guild.id, member.id)
        if not warns:
            return await interaction.response.send_message(f"{member.mention} has no warnings.", ephemeral=True)
        embed = discord.Embed(title=f"Warnings - {member.display_name}", color=discord.Color.yellow())
        for w in warns:
            embed.add_field(name=f"#{w['id']} | {w['created_at'][:10]}", value=f"**Reason:** {w['reason']}", inline=False)
        await interaction.response.send_message(embed=embed)

    # ── CLEARWARNS ────────────────────────────────────────────────────────────

    @commands.command(name="clearwarns")
    @commands.has_permissions(moderate_members=True)
    async def clearwarns(self, ctx, member: discord.Member):
        count = await db.clear_warnings(ctx.guild.id, member.id)
        await ctx.send(f"Cleared **{count}** warnings for {member.mention}.")

    @app_commands.command(name="clearwarns", description="Clear all warnings for a member")
    @app_commands.describe(member="Member to clear warnings for")
    @has_mod_role()
    async def clearwarns_slash(self, interaction: discord.Interaction, member: discord.Member):
        count = await db.clear_warnings(interaction.guild.id, member.id)
        await interaction.response.send_message(f"Cleared **{count}** warnings for {member.mention}.")

    # ── PURGE ─────────────────────────────────────────────────────────────────

    @commands.command(name="purge", aliases=["clear"])
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"Deleted **{amount}** messages.", delete_after=3)

    @app_commands.command(name="purge", description="Delete messages in a channel")
    @app_commands.describe(amount="Number of messages to delete")
    @has_mod_role()
    async def purge_slash(self, interaction: discord.Interaction, amount: int):
        await interaction.response.defer(ephemeral=True)
        await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"Deleted **{amount}** messages.", ephemeral=True)

    # ── SLOWMODE ──────────────────────────────────────────────────────────────

    @commands.command(name="slowmode")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int):
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.send(f"Slowmode set to **{seconds}s**." if seconds > 0 else "Slowmode disabled.")

    @app_commands.command(name="slowmode", description="Set slowmode in a channel")
    @app_commands.describe(seconds="Seconds (0 = disable)")
    @has_mod_role()
    async def slowmode_slash(self, interaction: discord.Interaction, seconds: int):
        await interaction.channel.edit(slowmode_delay=seconds)
        await interaction.response.send_message(f"Slowmode set to **{seconds}s**." if seconds > 0 else "Slowmode disabled.")

    # ── LOCK / UNLOCK ─────────────────────────────────────────────────────────

    @commands.command(name="lock")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send("Channel locked.")

    @commands.command(name="unlock")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=None)
        await ctx.send("Channel unlocked.")

    @app_commands.command(name="lock", description="Lock a channel")
    @has_mod_role()
    async def lock_slash(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
        await interaction.response.send_message("Channel locked.")

    @app_commands.command(name="unlock", description="Unlock a channel")
    @has_mod_role()
    async def unlock_slash(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=None)
        await interaction.response.send_message("Channel unlocked.")

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
            await ctx.send("You don't have permission to use this command.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("Member not found.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Missing argument: `{error.param.name}`")
        else:
            await ctx.send(f"Error: {error}")


async def setup(bot):
    await bot.add_cog(Moderation(bot))
