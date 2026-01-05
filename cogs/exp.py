from db.connection import get_database
import time
import math
import discord
from discord.ext import commands, tasks
import aiosqlite

save_interval_seconds = 60
flush_interval = 60

class UserEXP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.buffer: dict[int, int] = {}
        self.last_message_time: dict[int, float] = {}

        self.flush_exp.start()

    def cog_unload(self):
        self.flush_exp.cancel()

    def caclculate_exp(self, message: discord.Message) -> int:
        base_exp = 10
        lemgth_bonus = min(len(message.content) // 20, 5)
        attachment_bonus = len(message.attachments) * 5 if message.attachments else 0
        return base_exp + lemgth_bonus + attachment_bonus


    def get_level(self, exp: int) -> int:
        return int(math.sqrt(exp // 10))

    def can_gain_exp(self, user_id: int, current_time: float) -> bool:
        now = time.monotonic()
        last = self.last_message_time.get(user_id, 0)
        if now - last < save_interval_seconds:
            return False

        self.last_message_time[user_id] = now
        return True

    def add_exp_to_buffer(self, user_id: int, exp: int):
        self.buffer[user_id] = self.buffer.get(user_id, 0) + exp

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild or message.content.startswith(self.bot.command_prefix):
            return

        if not self.can_gain_exp(message.author.id, time.monotonic()):
            return

        exp = self.caclculate_exp(message)
        self.add_exp_to_buffer(message.author.id, exp)

        await self.bot.process_commands(message)

        print(f"{message.author} gained {exp} EXP.")

    @tasks.loop(seconds=flush_interval)
    async def flush_exp(self):
        if not self.buffer:
            return

        db = await get_database()

        async with db.execute("BEGIN"):
            for user_id, exp in self.buffer.items():
                await db.execute(
                    """
                    INSERT INTO user (user_id, exp)
                    VALUES (?, ?)
                    ON CONFLICT(user_id) DO UPDATE SET exp = exp + excluded.exp
                    """,
                    (user_id, exp)
                )

        await db.commit()
        self.buffer.clear()

    @flush_exp.before_loop
    async def before_flush_exp(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(UserEXP(bot))
