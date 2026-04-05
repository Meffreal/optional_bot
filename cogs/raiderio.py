import discord
from discord.ext import commands
from discord import app_commands
import aiohttp

RAIDERIO_API = "https://raider.io/api/v1/characters/profile"

IO_ROLES = [
    (3500, "Interrupt God",      "3500+"),
    (3000, "Interrupt Optional", "3000 - 3499"),
    (2500, "IO Enjoyer",         "2500 - 2999"),
    (2000, "Keystone Legend",    "2000 - 2499"),
    (1000, "Keystone Hero",      "1000 - 1999"),
    (0,    "Casual",             "0 - 999"),
]

IO_ROLE_NAMES = {name for _, name, _ in IO_ROLES}


def get_role_info(score: float) -> tuple[str, str]:
    for threshold, name, range_str in IO_ROLES:
        if score >= threshold:
            return name, range_str
    return "Casual", "0 - 999"


class RaiderIO(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def fetch_rio(self, character: str, realm: str) -> dict | None:
        params = {
            "region": "eu",
            "realm": realm.lower().replace(" ", "-"),
            "name": character,
            "fields": "mythic_plus_scores_by_season:current",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(RAIDERIO_API, params=params) as resp:
                if resp.status != 200:
                    return None
                return await resp.json()

    async def update_io_role(self, member: discord.Member, score: float) -> tuple[str, str]:
        role_name, range_str = get_role_info(score)

        # Remove all existing IO roles
        roles_to_remove = [r for r in member.roles if r.name in IO_ROLE_NAMES]
        if roles_to_remove:
            await member.remove_roles(*roles_to_remove)

        # Find or create the target role
        role = discord.utils.get(member.guild.roles, name=role_name)
        if not role:
            role = await member.guild.create_role(name=role_name, reason="Raider.IO role auto-assign")

        await member.add_roles(role)
        return role_name, range_str

    # ── PREFIX COMMAND ────────────────────────────────────────────────────────

    @commands.command(name="rio")
    async def rio(self, ctx, *, args: str):
        if "-" not in args:
            return await ctx.send("Usage: `.rio <character> - <realm>`")

        parts = args.split("-", 1)
        character = parts[0].strip()
        realm = parts[1].strip()

        if not character or not realm:
            return await ctx.send("Usage: `.rio <character> - <realm>`")

        async with ctx.typing():
            data = await self.fetch_rio(character, realm)

        if not data:
            return await ctx.send(f"Character **{character}-{realm}** not found on Raider.IO. Check the name and realm.")

        scores = data.get("mythic_plus_scores_by_season", [])
        score = scores[0]["scores"]["all"] if scores else 0.0

        role_name, range_str = await self.update_io_role(ctx.author, score)

        embed = discord.Embed(
            title=f"{data['name']} - {data['realm']}",
            url=data.get("profile_url", ""),
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(url=data.get("thumbnail_url", ""))
        embed.add_field(name="Class", value=data.get("class", "Unknown"), inline=True)
        embed.add_field(name="Spec", value=data.get("active_spec_name", "Unknown"), inline=True)
        embed.add_field(name="M+ Score", value=f"**{score:.0f}**", inline=True)
        embed.add_field(name="Role Assigned", value=f"`{role_name}` ({range_str})", inline=False)
        embed.set_footer(text="Data from Raider.IO")
        await ctx.send(embed=embed)

    # ── SLASH COMMAND ─────────────────────────────────────────────────────────

    @app_commands.command(name="rio", description="Fetch Raider.IO score and assign role")
    @app_commands.describe(character="Character name", realm="Realm name")
    async def rio_slash(self, interaction: discord.Interaction, character: str, realm: str):
        await interaction.response.defer()

        data = await self.fetch_rio(character, realm)

        if not data:
            return await interaction.followup.send(f"Character **{character}-{realm}** not found on Raider.IO. Check the name and realm.")

        scores = data.get("mythic_plus_scores_by_season", [])
        score = scores[0]["scores"]["all"] if scores else 0.0

        role_name, range_str = await self.update_io_role(interaction.user, score)

        embed = discord.Embed(
            title=f"{data['name']} - {data['realm']}",
            url=data.get("profile_url", ""),
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(url=data.get("thumbnail_url", ""))
        embed.add_field(name="Class", value=data.get("class", "Unknown"), inline=True)
        embed.add_field(name="Spec", value=data.get("active_spec_name", "Unknown"), inline=True)
        embed.add_field(name="M+ Score", value=f"**{score:.0f}**", inline=True)
        embed.add_field(name="Role Assigned", value=f"`{role_name}` ({range_str})", inline=False)
        embed.set_footer(text="Data from Raider.IO")
        await interaction.followup.send(embed=embed)

    # ── ERROR HANDLER ─────────────────────────────────────────────────────────

    @rio.error
    async def rio_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Usage: `.rio <character> - <realm>`")
        else:
            await ctx.send(f"Error: {error}")


async def setup(bot):
    await bot.add_cog(RaiderIO(bot))
