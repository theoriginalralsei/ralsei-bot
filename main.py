import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv
from db.connection import get_database

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

class Main(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="set_welcome", description="Setup your Welcome channel")
    async def set_welcome(self, ctx: discord.Interaction, channel: discord.TextChannel):
        connection = get_database()
        cursor = connection.cursor()

        cursor.execute("""
                    INSERT INTO server (guild_id, welcome_channel)
                    VALUES (?, ?)
                    ON CONFLICT(guild_id) DO UPDATE SET welcome_channel = ? """, 
                    (ctx.guild.id ,channel.id))

        connection.commit()
        cursor.close()
        connection.close()

        await ctx.send(f"Welcome channel set to {channel.mention}")

    @app_commands.command(name="set_counting", description="Set up your counting channel")
    async def set_counting(self, ctx: discord.Interaction, channel: discord.TextChannel):
        connection = get_database()
        cursor = connection.cursor()

        cursor.execute("""
                    INSERT INTO server (guild_id, log_channel)
                    VALUES (?, ?)
                    ON CONFLICT(guild_id) DO UPDATE SET log_channel = ? """, 
                    (ctx.guild.id ,channel.id))

        connection.commit()
        cursor.close()
        connection.close()

        await ctx.send(f"Counting channel set to {channel.mention}")

    
    @app_commands.command(name="set_modlog", description="Set up your modlog channel")
    async def set_modlog(self, ctx: discord.Interaction, channel: discord.TextChannel):
        connection = get_database()
        cursor = connection.cursor()

        cursor.execute("""
                    INSERT INTO server (guild_id, counting_channel)
                    VALUES (?, ?)
                    ON CONFLICT(guild_id) DO UPDATE SET counting_channel_channel = ? """, 
                    (ctx.guild.id ,channel.id))

        connection.commit()
        cursor.close()
        connection.close()

        await ctx.send(f"Log channel set to {channel.mention}")

    @commands.Cog.listener()
    async def on_member_join(self,member):
        connection = get_database()
        cursor = connection.cursor()

        cursor.execute("""
                    SELECT welcome_channel FROM server
                    WHERE guild_id = ?
                    """, (member.guild.id)

        result = cursor.fetchone()
        connection.close()
        cursor.close()

        if result and result[0]:
            channel = member.guild.get_channel(result[0])
            await channel.send(f"Welcome {member.mention} to {member.guild.name}!")


    @commands.Cog.listener()
    async def on_command_error(self, ctx,error):
        await ctx.send(f"Error: {error}")

    @app_commands.command(name="commands", description="Shows all available commands")
    async def show_commands(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Commands",
            description=None,
            color=discord.Color.green()
            )

        for cog_name, cog in bot.cogs.items():
            commands_list = cog.get_commands()
            app_command_list = cog.get_app_commands()

            if commands_list:

                commands_info = "\n".join([f"r:{cmd.name}" for cmd in commands_list])
                embed.add_field(
                    name=f"{cog_name} Commands",
                    value=commands_info,
                    inline=False
            ) 
        
            if app_command_list:

                app_command_info = "\n".join([f"/{cmd.name} - {cmd.description}" for cmd in app_command_list])
                embed.add_field(
                        name=f"{cog_name} Commands",
                        value=app_command_info,
                        inline=False
                    )

        await interaction.response.send_message(embed=embed)  

async def main():
    await bot.add_cog(Main(bot))
    extensions = ["cogs.fun", "cogs.actions", "cogs.logs", "cogs.count", "cogs.admin"]

    for ex in extensions:
        try:
            await bot.load_extension(ex)
            print(f"Loaded {ex}!")
        except Exception as e:
            print(f"Failed to load {ex}, reason {e}")
    await bot.start(TOKEN)

asyncio.run(main())
