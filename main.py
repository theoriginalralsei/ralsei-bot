import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv
from db.connection import get_database
import time

load_dotenv()
TOKEN = os.getenv("TOKEN")
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="r:", intents=intents)


@bot.event
async def on_ready():
    try:
        sync = await bot.tree.sync()
        print(f"Synced {len(sync)} app commands!")
        print(f"Logged in as {bot.user}!")
    except Exception as e:
        print(f"Failed to load commands: {e}")


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.starter_time = time.perf_counter()

    @commands.command(name="ping")
    async def ping(self, ctx):
        self.end_time = time.perf_counter()
        self.duration = self.end_time - self.starter_time
        await ctx.send((f"Aaaand pong! in {int(self.duration)}MS"))

    @app_commands.command(name="welcome", description="Setup your Welcome channel")
    @app_commands.default_permissions(administrator=True)
    async def set_welcome(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ):
        await interaction.response.defer()

        db = await get_database()

        await db.execute(
            """
                INSERT INTO server (guild_id, welcome_channel)
                VALUES (?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET welcome_channel = excluded.welcome_channel 
            """,
            (
                interaction.guild.id,
                channel.id,
            ),
        )

        await db.commit()

        await interaction.followup.send(f"Welcome channel set to {channel.mention}")

    @app_commands.command(name="counting", description="Set up your counting channel")
    @app_commands.default_permissions(administrator=True)
    async def set_counting(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ):
        await interaction.response.defer()

        db = await get_database()

        await db.execute(
            """
                INSERT INTO server (guild_id, counting_channel)
                VALUES (?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET counting_channel = excluded.counting_channel 
        """,
            (
                interaction.guild.id,
                channel.id,
            ),
        )

        await db.commit()

        await interaction.followup.send(f"Counting channel set to {channel.mention}")

    @app_commands.command(name="modlog", description="Set up your modlog channel")
    @app_commands.default_permissions(administrator=True)
    async def set_modlog(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ):
        await interaction.response.defer()

        db = await get_database()

        await db.execute(
            """
                INSERT INTO server (guild_id, log_channel)
                VALUES (?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET log_channel = excluded.log_channel 
        """,
            (
                interaction.guild.id,
                channel.id,
            ),
        )

        await db.commit()

        await interaction.followup.send(f"Log channel set to {channel.mention}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        db = await get_database()

        cursor = await db.execute(
            "SELECT welcome_channel FROM server WHERE guild_id = ? ", (member.guild.id,)
        )

        result = await cursor.fetchone()

        if result and result[0]:
            channel_id = int(result[0])
            channel = member.guild.get_channel(channel_id)
            try:
                if channel:
                    await channel.send(
                        f"Welcome {member.mention} to {member.guild.name}!"
                    )
            except discord.Forbidden:
                print(f"Missing permissions to welcome message in {channel}")

    @app_commands.command(name="commands", description="Shows all available commands")
    async def show_commands(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Commands", description=None, color=discord.Color.green()
        )

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

        await interaction.response.send_message(embed=embed)


async def main():
    extensions = ["cogs.fun", "cogs.actions", "cogs.count", "cogs.ai", "cogs.admin"]

    for ex in extensions:
        try:
            await bot.load_extension(ex)
            print(f"Loaded {ex}!")
        except Exception as e:
            print(f"Failed to load {ex}, reason {e}")
    await bot.add_cog(Utility(bot))
    await bot.start(TOKEN)


asyncio.run(main())
