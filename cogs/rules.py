import discord
from discord.ext import commands

RULES_CHANNEL_ID = 1490485785034621150
MEMBER_ROLE_NAME = "Member"

RULES_TEXT = """
**1. Respect everyone**
Treat all members with respect. Personal attacks, harassment, and targeted toxicity are not tolerated.

**2. Dark humor is allowed**
Dark humor is fine — but know the line between a joke and being genuinely awful.

**3. No spam**
Don't flood channels with spam, excessive pings, or repeated messages.

**4. No NSFW outside designated channels**
Keep explicit content where it belongs.

**5. Use common sense**
If you have to ask yourself "is this okay?" — it probably isn't.
"""


class RulesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Accept", emoji="✅", style=discord.ButtonStyle.green, custom_id="rules_accept")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, name=MEMBER_ROLE_NAME)
        if not role:
            return await interaction.response.send_message(
                "Member role not found. Please contact an admin.", ephemeral=True
            )

        if role in interaction.user.roles:
            return await interaction.response.send_message(
                "You already have access.", ephemeral=True
            )

        await interaction.user.add_roles(role)
        await interaction.response.send_message(
            "Welcome to the server! You now have full access.", ephemeral=True
        )

    @discord.ui.button(label="Decline", emoji="❌", style=discord.ButtonStyle.red, custom_id="rules_decline")
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "You must accept the rules to access the server.", ephemeral=True
        )


class Rules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.add_view(RulesView())

    @commands.command(name="setuprules")
    @commands.is_owner()
    async def setuprules(self, ctx):
        guild = ctx.guild
        channel = self.bot.get_channel(RULES_CHANNEL_ID)
        if not channel:
            return await ctx.send("Rules channel not found.")

        # Create Member role if it doesn't exist
        role = discord.utils.get(guild.roles, name=MEMBER_ROLE_NAME)
        if not role:
            role = await guild.create_role(
                name=MEMBER_ROLE_NAME,
                reason="Auto-created by Optional Bot for rule acceptance gate"
            )
            await ctx.send(f"Created role **{MEMBER_ROLE_NAME}** (`{role.id}`).\nMake sure to set up channel permissions so only this role can access the server.")

        embed = discord.Embed(
            title="Server Rules",
            description=RULES_TEXT,
            color=0x2B2D31,
        )
        embed.add_field(
            name="",
            value="By clicking **Accept** you agree to follow the rules above.\nIf you decline, you will not have access to the server.",
            inline=False
        )
        embed.set_footer(text="Interrupt Optional")

        await channel.send(embed=embed, view=RulesView())
        await ctx.send("Rules posted.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Rules(bot))
