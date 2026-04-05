import discord
from discord.ext import commands
from discord import app_commands
import random


ROASTS = [
    "Tvůj IQ je nižší než teplota v lednici.",
    "Vypadáš jako bys byl vygenerovaný ChatGPT, ale levnou verzí.",
    "Jsi tak nudný, že i tvůj stín tě opustil.",
    "Kdybys byl pizzou, byl bys bez sýra, bez omáčky a studená.",
    "Tvoje nápady jsou jako Wi-Fi ve sklepě - žádné.",
    "Jsi důkaz, že evoluce někdy jde pozpátku.",
    "Tvoje přítomnost je jako CAPTCHA - nikdo to nechce řešit.",
]

JOKES = [
    "Proč programátoři nesnáší přírodu? Příliš mnoho bugů.",
    "Co řekl nula jedničce? Hezky oblečená!",
    "Jak se jmenuje Eskymák bez domova? Homeless sapiens.",
    "Proč jsou ryby tak chytré? Protože žijí ve školách.",
    "Co dělá hacker ráno? Hashuje snídani.",
    "Proč byl matematik smutný? Protože měl příliš mnoho problémů.",
    "Jak voláš lenivouna který si dělá legraci? Slow-mo comedian.",
]


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── 8BALL ─────────────────────────────────────────────────────────────────

    BALL_RESPONSES = [
        "Určitě ano.", "Bez pochyb.", "Ano, rozhodně.", "Pravděpodobně.",
        "Vyhlídky jsou dobré.", "Ano.", "Spíše ano.", "Nejasné, zkus znovu.",
        "Zeptej se později.", "Raději neříkám.", "Nedá se nyní předpovědět.",
        "Soustřeď se a zeptej se znovu.", "Nespoléhej na to.", "Moje odpověď je ne.",
        "Vyhlídky nejsou dobré.", "Velmi pochybné."
    ]

    @commands.command(name="8ball")
    async def ball(self, ctx, *, question: str):
        embed = discord.Embed(title="Magic 8-Ball", color=discord.Color.dark_purple())
        embed.add_field(name="Otázka", value=question, inline=False)
        embed.add_field(name="Odpověď", value=random.choice(self.BALL_RESPONSES), inline=False)
        await ctx.send(embed=embed)

    @app_commands.command(name="8ball", description="Zeptej se magické koule")
    @app_commands.describe(question="Tvoje otázka")
    async def ball_slash(self, interaction: discord.Interaction, question: str):
        embed = discord.Embed(title="Magic 8-Ball", color=discord.Color.dark_purple())
        embed.add_field(name="Otázka", value=question, inline=False)
        embed.add_field(name="Odpověď", value=random.choice(self.BALL_RESPONSES), inline=False)
        await interaction.response.send_message(embed=embed)

    # ── ROLL ──────────────────────────────────────────────────────────────────

    @commands.command(name="roll")
    async def roll(self, ctx, sides: int = 6):
        if sides < 2:
            return await ctx.send("Kostka musí mít alespoň 2 strany.")
        result = random.randint(1, sides)
        await ctx.send(f"Hodil jsi **d{sides}** a padlo: **{result}**")

    @app_commands.command(name="roll", description="Hodí kostkou")
    @app_commands.describe(sides="Počet stran kostky (výchozí: 6)")
    async def roll_slash(self, interaction: discord.Interaction, sides: int = 6):
        if sides < 2:
            return await interaction.response.send_message("Kostka musí mít alespoň 2 strany.", ephemeral=True)
        result = random.randint(1, sides)
        await interaction.response.send_message(f"Hodil jsi **d{sides}** a padlo: **{result}**")

    # ── COINFLIP ──────────────────────────────────────────────────────────────

    @commands.command(name="coinflip", aliases=["flip"])
    async def coinflip(self, ctx):
        result = random.choice(["Panna", "Orel"])
        await ctx.send(f"Mince padla na: **{result}**")

    @app_commands.command(name="coinflip", description="Hodí mincí")
    async def coinflip_slash(self, interaction: discord.Interaction):
        result = random.choice(["Panna", "Orel"])
        await interaction.response.send_message(f"Mince padla na: **{result}**")

    # ── RPS ───────────────────────────────────────────────────────────────────

    RPS_CHOICES = ["nuzky", "kamen", "papir"]
    RPS_WINS = {"nuzky": "papir", "kamen": "nuzky", "papir": "kamen"}

    @commands.command(name="rps")
    async def rps(self, ctx, choice: str):
        choice = choice.lower()
        if choice not in self.RPS_CHOICES:
            return await ctx.send("Vyber: `nuzky`, `kamen` nebo `papir`.")
        bot_choice = random.choice(self.RPS_CHOICES)
        if choice == bot_choice:
            result = "Remiza!"
        elif self.RPS_WINS[choice] == bot_choice:
            result = "Vyhral jsi!"
        else:
            result = "Prohral jsi!"
        await ctx.send(f"Ty: **{choice}** | Já: **{bot_choice}** -> {result}")

    @app_commands.command(name="rps", description="Kámen nůžky papír")
    @app_commands.describe(choice="Tvůj výběr")
    @app_commands.choices(choice=[
        app_commands.Choice(name="Nůžky", value="nuzky"),
        app_commands.Choice(name="Kámen", value="kamen"),
        app_commands.Choice(name="Papír", value="papir"),
    ])
    async def rps_slash(self, interaction: discord.Interaction, choice: str):
        bot_choice = random.choice(self.RPS_CHOICES)
        if choice == bot_choice:
            result = "Remiza!"
        elif self.RPS_WINS[choice] == bot_choice:
            result = "Vyhral jsi!"
        else:
            result = "Prohral jsi!"
        await interaction.response.send_message(f"Ty: **{choice}** | Já: **{bot_choice}** -> {result}")

    # ── ROAST ─────────────────────────────────────────────────────────────────

    @commands.command(name="roast")
    async def roast(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        await ctx.send(f"{target.mention} {random.choice(ROASTS)}")

    @app_commands.command(name="roast", description="Roastne člena")
    @app_commands.describe(member="Koho roastnout (výchozí: ty)")
    async def roast_slash(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        await interaction.response.send_message(f"{target.mention} {random.choice(ROASTS)}")

    # ── JOKE ──────────────────────────────────────────────────────────────────

    @commands.command(name="joke")
    async def joke(self, ctx):
        await ctx.send(random.choice(JOKES))

    @app_commands.command(name="joke", description="Řekne vtip")
    async def joke_slash(self, interaction: discord.Interaction):
        await interaction.response.send_message(random.choice(JOKES))

    # ── RATE ──────────────────────────────────────────────────────────────────

    @commands.command(name="rate")
    async def rate(self, ctx, *, thing: str):
        score = random.randint(0, 10)
        bar = "█" * score + "░" * (10 - score)
        await ctx.send(f"**{thing}**: `{bar}` **{score}/10**")

    @app_commands.command(name="rate", description="Ohodnotí cokoliv")
    @app_commands.describe(thing="Co ohodnotit")
    async def rate_slash(self, interaction: discord.Interaction, thing: str):
        score = random.randint(0, 10)
        bar = "█" * score + "░" * (10 - score)
        await interaction.response.send_message(f"**{thing}**: `{bar}` **{score}/10**")


async def setup(bot):
    await bot.add_cog(Fun(bot))
