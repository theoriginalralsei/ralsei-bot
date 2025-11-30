import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
from database.connection import get_database

class Count(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.counter = 0

    @commands.Cog.listener()
    async def on_message(self,ctx: discord.Interaction ,message):

        connection = await get_database()
        cursor = await connection.cursor()

        await cursor.execute("""
                       SELECT counting_channel FROM server
                       WHERE guild_id = ?
                       """, (message.author.guild.id,))

        result = await cursor.fetchone() 
        await connection.close()
        await cursor.close()

        if not result:
            return  

        channel = message.guild.get_channel(result)
        channel_id = result[0]

        if not channel:
            return

        if message.channel.id != channel_id:
            return

        try:
            number = int(message.content)

            if number == self.counter + 1 and message.channel == channel:
                self.counter = number
                await message.add_reaction("✅")
            else:
                await message.add_reaction("❌")
                self.counter = 0
                await ctx.send(f"{message.author.mention} Has failed to count... Just how")

        except ValueError:
            pass


async def setup(bot):
    await bot.add_cog(Count(bot))
