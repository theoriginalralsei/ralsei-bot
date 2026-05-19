import discord
from discord.ext import commands
from discord import app_commands
import random
import aiohttp
import sys

API_BASE = "https://api.truthordarebot.xyz/v1"

arr_truth = [
    "When was ya' first kiss?",
    "What's the most Femboy thing you've ever done?",
    "If you had a first date (if so then why are you here-), what was it like?",
    "Weirdest moment?",
    "How much of a nerd are you on a scale of 1-10?",
    "Have you ever had a crush on someone here?",
    "Be honest. You Meowed at a cat once, right?",
    "You like kissing boys, don't you~?"
]

arr_dare = [
    "DM someone here a kiss and say nothing",
    "Show off your thighs to one person",
    "Show off your thighs to EVERYONE",
    "Share a recent shower thought you had",
    "Recreate this bot, now.",
    "Contribute to an Open Source project :3",
    "Find a cat and record yourself meowing at em :3",
    "Kiss a guy~ I know you wanna~"
]


async def fetch_tod(session, endpoint, rating="pg"):
    try:
        async with session.get(f"{API_BASE}/{endpoint}?rating={rating}") as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("question")
    except Exception as e:
       print(e) 
    return None

class TODView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Truth", style=discord.ButtonStyle.green)
    async def truth_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with aiohttp.ClientSession() as session:
            question = await fetch_tod(session, "truth", "pg")
        question = question if random.random() > 0.7 else random.choice(arr_truth)
        embed = discord.Embed(
            title="Truth", description=f"**{question} {' ' * 10}**", color=discord.Color.green()
        )

        embed.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, view=self)

    @discord.ui.button(label="Dare", style=discord.ButtonStyle.red)
    async def dare_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with aiohttp.ClientSession() as session:
            dare = await fetch_tod(session, "dare", "pg")
        dare = dare if random.random() > 0.7 else random.choice(arr_dare) 
        embed = discord.Embed(
            title="Dare", description=f"**{dare} {' ' * 10}**", color=discord.Color.red()
        )
        embed.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, view=self)

    @discord.ui.button(label="Random", style=discord.ButtonStyle.secondary)
    async def random_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with aiohttp.ClientSession() as session:
            if random.random() < 0.5:
                random_tod = await fetch_tod(session, "truth", "pg") if random.random() > 0.7 else random.choice(arr_truth)
                color = discord.Color.green()
                title = "Truth"
            else:
                random_tod = await fetch_tod(session, "dare", "pg") if random.random() > 0.7 else random.choice(arr_dare)
                color = discord.Color.red()
                title = "Dare"
        
        embed = discord.Embed(
            title=title, description=f"**{random_tod} {' ' * 10}**", color=color
        )
        embed.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, view=self)

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_ship_bar(self, percent: int, width=20):
        length = int(width * percent // 100)
        bar = '█' * length + '░' * (width - length)
        return f"{bar}"

    @commands.command(name="Scream", aliases=["scream", "s"])
    async def Scream(self, ctx):
        embed = discord.Embed(
            title=None,
            description="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
            color=discord.Color.green(),
        )

        await ctx.send(embed=embed)

    @commands.command(name="Speak", aliases=["speak", "sp"])
    async def Speak(self, ctx, *msg):
        embed = discord.Embed(
            title=None,
            description=f"**{ctx.author}: {' '.join(msg)}**",
            color=discord.Color.green(),
        )

        await ctx.send(embed=embed)

    @app_commands.command(name="8ball", description="Talk with Ralsei of True Wisdom and Knowledge")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def ball(self, interaction: discord.Interaction, message: str):
        user_icon = interaction.user.avatar.url if interaction.user.avatar else None
        embed = discord.Embed(
            title="8ball",
            description=f"Question: {message}",
            color=discord.Color.green(),
        )
        embed.set_footer(text=f"Asked by {interaction.user}", icon_url=user_icon)

        embed.add_field(
            name="Ralsei says...",
            value=f"{'─' * 49}",
            inline=True,
        )

        responses = [
            "https://demirramon-media.s3.us-east-2.amazonaws.com/undertale/textbox/generated/13865663.png",
            "https://demirramon-media.s3.us-east-2.amazonaws.com/undertale/textbox/generated/13865670.png",
            "https://demirramon-media.s3.us-east-2.amazonaws.com/undertale/textbox/generated/13865682.png",
            "https://demirramon-media.s3.us-east-2.amazonaws.com/undertale/textbox/generated/13865689.png",
            "https://demirramon-media.s3.us-east-2.amazonaws.com/undertale/textbox/generated/13865705.png",
            "https://demirramon-media.s3.us-east-2.amazonaws.com/undertale/textbox/generated/13865709.png",
            "https://demirramon-media.s3.us-east-2.amazonaws.com/undertale/textbox/generated/13865724.png",
            "https://demirramon-media.s3.us-east-2.amazonaws.com/undertale/textbox/generated/13865734.png",
            "https://demirramon-media.s3.us-east-2.amazonaws.com/undertale/textbox/generated/13865744.png",
            "https://demirramon-media.s3.us-east-2.amazonaws.com/undertale/textbox/generated/13865776.png",
            "https://demirramon-media.s3.us-east-2.amazonaws.com/undertale/textbox/generated/13865786.png",
            "https://demirramon-media.s3.us-east-2.amazonaws.com/undertale/textbox/generated/13865808.png",
            "https://demirramon-media.s3.us-east-2.amazonaws.com/undertale/textbox/generated/13865816.png",
            "https://demirramon-media.s3.us-east-2.amazonaws.com/undertale/textbox/generated/13865825.png",
            "https://demirramon-media.s3.us-east-2.amazonaws.com/undertale/textbox/generated/13865832.png",
            "https://demirramon-media.s3.us-east-2.amazonaws.com/undertale/textbox/generated/13865840.png",
            "https://demirramon-media.s3.us-east-2.amazonaws.com/undertale/textbox/generated/13865867.png",
            "https://demirramon-media.s3.us-east-2.amazonaws.com/undertale/textbox/generated/13865876.png",
            "https://demirramon-media.s3.us-east-2.amazonaws.com/undertale/textbox/generated/13865901.png",
            "https://demirramon-media.s3.us-east-2.amazonaws.com/undertale/textbox/generated/13865910.png",
            "https://demirramon-media.s3.us-east-2.amazonaws.com/undertale/textbox/generated/13865956.png",
            "https://demirramon-media.s3.us-east-2.amazonaws.com/undertale/textbox/generated/13865959.png",
        ]

        embed.set_image(url=random.choice(responses))

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tod", description="Play some TOD with Ralsei bot!")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def tod(self, interaction: discord.Interaction):
        view = TODView()
        embed = discord.Embed(
                title="Truth Or Dare",
                description="-# why did i make this",
                color=discord.Color.blue(),
                )
        await interaction.response.send_message(embed=embed, view=view)

    @commands.hybrid_command(name="ship", description="Ship Someoone with Someone else :3")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def ship(self, ctx: commands.Context, user_1: discord.Member, user_2: discord.Member):
        ship_number = random.randint(1, 100)
        ship_meter = self.load_ship_bar(ship_number) 

        ship_message = f"{ship_number}% - " 

        if ship_number in range(1, 25):
            ship_message = f"{ship_number}% - Mehhh I can't see it."
        elif ship_number in range(26, 50):
            ship_message = f"{ship_number}% - Ok I could see it"
        elif ship_number in range(51, 60):
            ship_message = f"{ship_number}% - They should date"
        elif ship_number in range(61, 100):
            ship_message = f"{ship_number}% - Match made in Heavem."

        embed = discord.Embed(
                title="Ship",
                description=f"{user_1.mention} X {user_2.mention}",
                color=discord.Color.green()
        )

        embed.add_field(name="Compatibility", value=ship_message, inline=False)
        embed.add_field(name="Ship Meter", value=ship_meter, inline=False)
        embed.set_footer(text=f"Used by {ctx.author.name}", icon_url=ctx.author.avatar)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Fun(bot))
