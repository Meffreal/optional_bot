import discord
from discord.ext import commands
from discord import app_commands
import time


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    # ── PING ──────────────────────────────────────────────────────────────────

    @commands.command(name="ping")
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"Pong! **{latency}ms**")

    @app_commands.command(name="ping", description="Show bot latency")
    async def ping_slash(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong! **{latency}ms**")

    # ── UPTIME ────────────────────────────────────────────────────────────────

    @commands.command(name="uptime")
    async def uptime(self, ctx):
        elapsed = int(time.time() - self.start_time)
        h, rem = divmod(elapsed, 3600)
        m, s = divmod(rem, 60)
        await ctx.send(f"Online for: **{h}h {m}m {s}s**")

    @app_commands.command(name="uptime", description="Show how long the bot has been online")
    async def uptime_slash(self, interaction: discord.Interaction):
        elapsed = int(time.time() - self.start_time)
        h, rem = divmod(elapsed, 3600)
        m, s = divmod(rem, 60)
        await interaction.response.send_message(f"Online for: **{h}h {m}m {s}s**")

    # ── SERVERINFO ────────────────────────────────────────────────────────────

    @commands.command(name="serverinfo")
    async def serverinfo(self, ctx):
        g = ctx.guild
        embed = discord.Embed(title=g.name, color=discord.Color.blurple())
        embed.set_thumbnail(url=g.icon.url if g.icon else None)
        embed.add_field(name="Owner", value=g.owner.mention, inline=True)
        embed.add_field(name="Members", value=g.member_count, inline=True)
        embed.add_field(name="Channels", value=len(g.channels), inline=True)
        embed.add_field(name="Roles", value=len(g.roles), inline=True)
        embed.add_field(name="Boost Level", value=g.premium_tier, inline=True)
        embed.add_field(name="Created", value=g.created_at.strftime("%d.%m.%Y"), inline=True)
        await ctx.send(embed=embed)

    @app_commands.command(name="serverinfo", description="Show server information")
    async def serverinfo_slash(self, interaction: discord.Interaction):
        g = interaction.guild
        embed = discord.Embed(title=g.name, color=discord.Color.blurple())
        embed.set_thumbnail(url=g.icon.url if g.icon else None)
        embed.add_field(name="Owner", value=g.owner.mention, inline=True)
        embed.add_field(name="Members", value=g.member_count, inline=True)
        embed.add_field(name="Channels", value=len(g.channels), inline=True)
        embed.add_field(name="Roles", value=len(g.roles), inline=True)
        embed.add_field(name="Boost Level", value=g.premium_tier, inline=True)
        embed.add_field(name="Created", value=g.created_at.strftime("%d.%m.%Y"), inline=True)
        await interaction.response.send_message(embed=embed)

    # ── USERINFO ──────────────────────────────────────────────────────────────

    @commands.command(name="userinfo")
    async def userinfo(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(title=str(member), color=member.color)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Nickname", value=member.display_name, inline=True)
        embed.add_field(name="Account Created", value=member.created_at.strftime("%d.%m.%Y"), inline=True)
        embed.add_field(name="Joined Server", value=member.joined_at.strftime("%d.%m.%Y"), inline=True)
        roles = [r.mention for r in member.roles[1:]]
        embed.add_field(name=f"Roles ({len(roles)})", value=", ".join(roles) if roles else "None", inline=False)
        await ctx.send(embed=embed)

    @app_commands.command(name="userinfo", description="Show information about a user")
    @app_commands.describe(member="User to check (default: you)")
    async def userinfo_slash(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        embed = discord.Embed(title=str(member), color=member.color)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Nickname", value=member.display_name, inline=True)
        embed.add_field(name="Account Created", value=member.created_at.strftime("%d.%m.%Y"), inline=True)
        embed.add_field(name="Joined Server", value=member.joined_at.strftime("%d.%m.%Y"), inline=True)
        roles = [r.mention for r in member.roles[1:]]
        embed.add_field(name=f"Roles ({len(roles)})", value=", ".join(roles) if roles else "None", inline=False)
        await interaction.response.send_message(embed=embed)

    # ── AVATAR ────────────────────────────────────────────────────────────────

    @commands.command(name="avatar", aliases=["av"])
    async def avatar(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(title=f"Avatar - {member.display_name}", color=discord.Color.blurple())
        embed.set_image(url=member.display_avatar.url)
        await ctx.send(embed=embed)

    @app_commands.command(name="avatar", description="Show a user's avatar")
    @app_commands.describe(member="User (default: you)")
    async def avatar_slash(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        embed = discord.Embed(title=f"Avatar - {member.display_name}", color=discord.Color.blurple())
        embed.set_image(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Utility(bot))
