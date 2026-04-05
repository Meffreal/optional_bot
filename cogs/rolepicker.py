import discord
from discord.ext import commands

CHANNEL_ID = 1490485785034621152

CLASS_ROLES = [
    ("Warrior",      1490485778411819145, "⚔️"),
    ("Paladin",      1490485778411819144, "🛡️"),
    ("Hunter",       1490485778411819143, "🏹"),
    ("Rogue",        1490485778411819142, "🗡️"),
    ("Priest",       1490485778411819141, "✨"),
    ("Shaman",       1490485778411819140, "⚡"),
    ("Mage",         1490485778411819139, "🔮"),
    ("Warlock",      1490485778411819138, "🌑"),
    ("Monk",         1490485778042585247, "👊"),
    ("Druid",        1490485778042585246, "🌿"),
    ("Demon Hunter", 1490485778042585245, "👁️"),
    ("Death Knight", 1490485778042585244, "❄️"),
]

SPEC_ROLES = [
    ("Tank",   1490485778042585240, "🛡️", discord.ButtonStyle.blurple),
    ("Healer", 1490485778042585241, "💚", discord.ButtonStyle.green),
    ("DPS",    1490485778042585242, "⚔️", discord.ButtonStyle.red),
]


class RoleToggleButton(discord.ui.Button):
    def __init__(self, label: str, role_id: int, emoji: str, custom_id: str,
                 style: discord.ButtonStyle = discord.ButtonStyle.secondary, row: int = 0):
        super().__init__(label=label, emoji=emoji, custom_id=custom_id, style=style, row=row)
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.role_id)
        if not role:
            return await interaction.response.send_message("Role not found.", ephemeral=True)

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"Removed **{role.name}**.", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"Assigned **{role.name}**.", ephemeral=True)


class ClassView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        for i, (name, role_id, emoji) in enumerate(CLASS_ROLES):
            self.add_item(RoleToggleButton(
                label=name,
                role_id=role_id,
                emoji=emoji,
                custom_id=f"rolepicker_class_{name.lower().replace(' ', '_')}",
                style=discord.ButtonStyle.secondary,
                row=i // 5,
            ))


class SpecView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        for name, role_id, emoji, style in SPEC_ROLES:
            self.add_item(RoleToggleButton(
                label=name,
                role_id=role_id,
                emoji=emoji,
                custom_id=f"rolepicker_spec_{name.lower()}",
                style=style,
                row=0,
            ))


class RolePicker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.add_view(ClassView())
        bot.add_view(SpecView())

    @commands.command(name="setuproles")
    @commands.is_owner()
    async def setuproles(self, ctx):
        channel = self.bot.get_channel(CHANNEL_ID)
        if not channel:
            return await ctx.send("Channel not found.")

        # Class embed
        class_embed = discord.Embed(
            title="Class Selection",
            description="Select your class below.\nYou can pick multiple (alts welcome).\nClick again to remove.",
            color=0xC69B3A,
        )
        class_embed.set_footer(text="Interrupt Optional")
        await channel.send(embed=class_embed, view=ClassView())

        # Spec embed
        spec_embed = discord.Embed(
            title="Role Selection",
            description="Select your role(s).\nClick again to remove.",
            color=0x0070DD,
        )
        spec_embed.set_footer(text="Interrupt Optional")
        await channel.send(embed=spec_embed, view=SpecView())

        await ctx.send("Role picker posted.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(RolePicker(bot))
