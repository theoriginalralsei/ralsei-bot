import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv
from db.connection import get_database, init_database, close_database
import time
import aiosqlite
import requests

load_dotenv()
TOKEN = os.getenv("TOKEN")
github_token = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "theoriginalralsei"
REPO_NAME = "ralsei-bot"
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="r:", intents=intents)
starter_time = time.perf_counter()

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

def log(level, msg, color=None):
    ts = f"  {Colors.DIM}{time.strftime('%H:%M:%S')}{Colors.RESET}"
    prefix = f"{ts} [{level}]"
    if color:
        print(f"{prefix} {color}{msg}{Colors.RESET}")
    else:
        print(f"{prefix} {msg}")

setup_group = app_commands.Group(name="setup", description="Server setup commands")

async def setup_database():
    await init_database()

@bot.event
async def on_ready():
    sync = await bot.tree.sync()
    elapsed = time.perf_counter() - starter_time
    print()
    print(f"{Colors.CYAN}{Colors.BOLD}  ┌{'─' * 40}┐{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}  │  {'Logged in as':<38}│{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}  │  {Colors.WHITE}{Colors.BOLD}{bot.user}{Colors.RESET}{' ' * (38 - len(str(bot.user)))}│{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}  │{'─' * 40}│{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}  │{Colors.GREEN}  Synced {len(sync)} app commands{' ' * (18 - len(str(len(sync))))}│{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}  │{Colors.MAGENTA}  Started in {elapsed:.2f}s{' ' * (26 - len(f'{elapsed:.2f}'))}│{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}  └{'─' * 40}┘{Colors.RESET}")
    print()

@bot.event
async def on_shutdown():
    await close_database()
    log("CLOSE", "Database connection closed.", Colors.YELLOW)

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_best_count(self, guild_id):
        db = await get_database()
        async with db.execute("SELECT best_count FROM count_state WHERE guild_id = ?", (guild_id,)) as cursor:
            row = await cursor.fetchone()

        return row[0] if row else None


    async def get_current_count(self, guild_id):
        db = await get_database()
        async with db.execute("SELECT current_count FROM count_state WHERE guild_id = ?", (guild_id,)) as cursor:
            row = await cursor.fetchone()

        return row[0] if row else None


    async def get_most_user_exp(self, user_id):
        db = await get_database()
        async with db.execute("SELECT MAX(exp) FROM user WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()

        return row[0] if row else None

    async def get_most_currency(self, user_id):
        db = await get_database()
        async with db.execute("SELECT MAX(currency) FROM user WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()

        return row[0] if row else None

    def get_commits(self, owner=REPO_OWNER, repo=REPO_NAME, count=10):
        url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json"
            }

        response = requests.get(url, headers=headers, params={"per_page": count})

        if response.status_code == 200:
             commits = response.json()
             return [
                     {
                        "sha": c["sha"],
                        "author": c["commit"]["author"]["name"],
                        "message": c["commit"]["message"].split("\n")[0],
                        "date": c["commit"]["author"]["date"],
                        "url": c["html_url"],
                        }
                     for c in commits
                     ]
        return None


    @commands.command(name="ping")
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        await ctx.send((f"Aaaand pong! in {latency}ms"))

    @commands.command(name="uptime")
    async def uptime(self, ctx):
        current_time = time.perf_counter()
        uptime_seconds = int(current_time - starter_time)
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        await ctx.send(f"Uptime: {hours}h {minutes}m {seconds}s")

    @commands.command(name="serverinfo")
    async def server_info(self, ctx):
        guild = ctx.guild
        embed = discord.Embed(
            title=f"{guild.name} Information",
            color=discord.Color.blue(),
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)

        embed.add_field(name="User with nost exp", value=await self.get_most_user_exp(guild.id), inline=False)
        embed.add_field(name="User with most currency", value=await self.get_most_currency(guild.id), inline=False)
        embed.add_field(name="Best count", value=await self.get_best_count(guild.id), inline=False)
        embed.add_field(name="Current count", value=await self.get_current_count(guild.id), inline=False)

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="commits", aliases=["latest", "recent"])
    async def commits(self, ctx):
        commits = self.get_commits()
        if not commits:
            embed = discord.Embed(
                title="Error",
                description="Could not fetch commits",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title=f"Latest {len(commits)} Commits",
            description=f"Recent commits for [ralsei-bot](https://github.com/theoriginalralsei/ralsei-bot)",
            color=discord.Color.green(),
        )

        for c in commits:
            embed.add_field(
                name=f"{c['sha'][:7]} - {c['author']}",
                value=f"[{c['message']}]({c['url']})",
                inline=False,
            )

        await ctx.send(embed=embed)

    @setup_group.command(name="welcome", description="Setup your Welcome channel")
    @app_commands.default_permissions(administrator=True)
    async def setup_welcome(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.defer()

        db = await get_database()

        await db.execute(
            """
                INSERT INTO server (guild_id, welcome_channel)
                VALUES (?, ?)
                ON CONFLICT(guild_id) 
                DO UPDATE SET welcome_channel = excluded.welcome_channel 
            """,
            (interaction.guild.id, channel.id),
        )

        await db.commit()
        try:
            await interaction.followup.send(f"Welcome channel set to {channel.mention}")
        except Exception as e:
            await interaction.followup.send(f"Error: {e}", ephemeral=True)

    @setup_group.command(name="counting", description="Set up your counting channel")
    @app_commands.default_permissions(administrator=True)
    async def setup_counting(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.defer()

        db = await get_database()

        await db.execute(
            """
                INSERT INTO server (guild_id, counting_channel)
                VALUES (?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET counting_channel = excluded.counting_channel 
             """,
            (interaction.guild.id, channel.id),
        )

        await db.commit()
        try:
            await interaction.followup.send(f"Counting channel set to {channel.mention}. Set by {interaction.user.mention}")
        except Exception as e:
            await interaction.followup.send(f"Error: {e}", ephemeral=True)

    @setup_group.command(name="modlog", description="Set up your modlog channel")
    @app_commands.default_permissions(administrator=True)
    async def setup_modlog(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ):
        await interaction.response.defer()

        db = await get_database()

        await db.execute(
            """
                INSERT INTO server (guild_id, log_channel)
                VALUES (?, ?)
                ON CONFLICT(guild_id) 
                DO UPDATE SET log_channel = excluded.log_channel 
            """,
            (interaction.guild.id, channel.id),
        )

        await db.commit()

        try: 
            await interaction.followup.send(f"Log channel set to {channel.mention}")
        except Exception as e:
            await interaction.followup.send(f"Error: {e}", ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        db = await get_database()

        async with db.execute(
            "SELECT welcome_channel FROM server WHERE guild_id = ?", (member.guild.id,)
        ) as cursor:
            row = await cursor.fetchone()

        if row and row[0]:
            channel = member.guild.get_channel(int(row[0]))
            if channel:
                try:
                    await channel.send(
                        f"Welcome {member.mention} to {member.guild.name}!"
                    )
                except discord.Forbidden:
                    log("WARN", f"Missing permissions for welcome message in {channel}", Colors.YELLOW)

    @commands.hybrid_command(name="commands", description="Displays the Commands for RB")
    async def show_commands(self, ctx: commands.Context):
        user_icon = ctx.author.avatar.url if ctx.author.avatar else None
        embed = discord.Embed(
            title="Commands",
            description="All available commands for Ralsei Bot.",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=user_icon)

        for cog_name, cog in self.bot.cogs.items():
            commands_list = cog.get_commands()
            slash_commands = cog.get_app_commands()

            if commands_list or slash_commands:
                commands_info = " ".join([f"`r:{cmd.name}`" for cmd in commands_list])
                app_info = " ".join([f"`/{cmd.name}`" for cmd in slash_commands])


                embed.add_field(
                    name=f"{cog_name}",
                    value=f"{commands_info} {app_info}",
                    inline=False,
                )

        await ctx.send(embed=embed)


async def main():
    print()
    print(f"{Colors.CYAN}{Colors.BOLD}   ╔{'═' * 43}╗{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}   ║{' ' * 43}║{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}   ║{Colors.WHITE}{'  Ralsei Bot Initializing...' : ^43}{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}   ║{' ' * 43}║{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}   ╚{'═' * 43}╝{Colors.RESET}")
    print()

    await setup_database()
    log("DB", "Database initialized", Colors.GREEN)

    bot.tree.add_command(setup_group)
    extensions = [
        "cogs.fun",
        "cogs.actions",
        "cogs.count",
        # NOTE: cogs.ai is VERY slow if you don't have a CUDA GPU ( and could slow down your CPU ). If you want, unncoment the next line
        # "cogs.ai",
        "cogs.inventory",
        "cogs.logs",
        "cogs.exp",
        "cogs.currency",
        "cogs.stats",
        "cogs.ai",
        "cogs.admin"]

    print()
    print(f"{Colors.DIM}  {'─' * 43}{Colors.RESET}")
    loaded_count = 0
    failed_count = 0

    for ex in extensions:
        try:
            await bot.load_extension(ex)
            print(f"  {Colors.GREEN}✓{Colors.RESET} {Colors.WHITE}{ex}{Colors.RESET}")
            loaded_count += 1
        except Exception as e:
            print(f"  {Colors.RED}✗{Colors.RESET} {Colors.DIM}{ex}{Colors.RESET} {Colors.DIM}~ {e}{Colors.RESET}")
            failed_count += 1

    print(f"{Colors.DIM}  {'─' * 43}{Colors.RESET}")
    print(f"  {Colors.CYAN}{Colors.BOLD}{loaded_count}/{len(extensions)} cogs loaded{Colors.RESET}")
    print()

    await bot.add_cog(Utility(bot))
    await bot.start(TOKEN)


asyncio.run(main())
