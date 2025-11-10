import discord
from discord.ext import commands
from datetime import datetime, timezone
import asyncio

CONFIG = {
    "guild_id": 1435577464507334688,
    "log_channel_id": 1437001255191838742
}

class ModLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = CONFIG

    def get_log_channel(self, guild: discord.Guild):
        return guild.get_channel(self.config['log_channel_id'])

    async def fetch_audit_entry(self, guild, action, target_id, delay_attempts=(0.5, 1.0, 2.0)):
        for delay in delay_attempts:
            await asyncio.sleep(delay)
            async for entry in guild.audit_logs(action=action, limit=3):
                if entry.target and entry.target.id == target_id:
                    time_diff = (datetime.now(timezone.utc) - entry.created_at).total_seconds()
                    if time_diff < 10:
                        return entry
        return None

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        if guild.id != self.config["guild_id"]:
            return

        log_channel = self.get_log_channel(guild)
        if not log_channel:
            return

        try:
            entry = await self.fetch_audit_entry(guild, discord.AuditLogAction.ban, user.id)
            if not entry:
                return

            embed = discord.Embed(
                title="Member Banned",
                color=discord.Color.red(),
                timestamp=datetime.now(timezone.utc)
            )
            embed.add_field(name="User", value=f"{user} ({user.id})", inline=True)
            embed.add_field(name="Moderator", value=f"{entry.user}", inline=True)
            embed.add_field(name="Reason", value=entry.reason or "No reason provided", inline=False)

            await log_channel.send(embed=embed)
        except Exception as e:
            print(f"[ERROR] Error logging ban: {e}")

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        if guild.id != self.config["guild_id"]:
            return

        log_channel = self.get_log_channel(guild)
        if not log_channel:
            return

        try:
            entry = await self.fetch_audit_entry(guild, discord.AuditLogAction.unban, user.id)
            if not entry:
                return

            embed = discord.Embed(
                title="Member Unbanned",
                color=discord.Color.green(),
                timestamp=datetime.now(timezone.utc)
            )
            embed.add_field(name="User", value=f"{user} ({user.id})", inline=True)
            embed.add_field(name="Moderator", value=f"{entry.user}", inline=True)
            embed.add_field(name="Reason", value=entry.reason or "No reason provided", inline=False)

            await log_channel.send(embed=embed)
        except Exception as e:
            print(f"[ERROR] Error logging unban: {e}")

    # --- Kicks ---
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.guild.id != self.config["guild_id"]:
            return

        log_channel = self.get_log_channel(member.guild)
        if not log_channel:
            return

        try:
            entry = await self.fetch_audit_entry(member.guild, discord.AuditLogAction.kick, member.id)
            if not entry:
                return

            embed = discord.Embed(
                title="Member Kicked",
                color=discord.Color.orange(),
                timestamp=datetime.now(timezone.utc)
            )
            embed.add_field(name="User", value=f"{member} ({member.id})", inline=True)
            embed.add_field(name="Moderator", value=f"{entry.user}", inline=True)
            embed.add_field(name="Reason", value=entry.reason or "No reason provided", inline=False)

            await log_channel.send(embed=embed)
        except Exception as e:
            print(f"[ERROR] Error logging kick: {e}")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if after.guild.id != self.config["guild_id"]:
            return

        log_channel = self.get_log_channel(after.guild)
        if not log_channel:
            return

        try:
            # --- Timeout Added ---
            if not before.timed_out_until and after.timed_out_until:
                entry = await self.fetch_audit_entry(after.guild, discord.AuditLogAction.member_update, after.id)
                if entry:
                    until_ts = int(after.timed_out_until.timestamp())
                    embed = discord.Embed(
                        title="⏰ Member Timed Out",
                        color=discord.Color.orange(),
                        timestamp=datetime.now(timezone.utc)
                    )
                    embed.add_field(name="User", value=f"{after} ({after.id})", inline=True)
                    embed.add_field(name="Moderator", value=f"{entry.user}", inline=True)
                    embed.add_field(name="Duration", value=f"Until <t:{until_ts}:R>", inline=False)
                    embed.add_field(name="Reason", value=entry.reason or "No reason provided", inline=False)
                    await log_channel.send(embed=embed)

            # --- Timeout Removed ---
            elif before.timed_out_until and not after.timed_out_until:
                entry = await self.fetch_audit_entry(after.guild, discord.AuditLogAction.member_update, after.id)
                moderator = entry.user if entry else "Automatic (timeout expired)"

                embed = discord.Embed(
                    title="✅ Timeout Removed",
                    color=discord.Color.green(),
                    timestamp=datetime.now(timezone.utc)
                )
                embed.add_field(name="User", value=f"{after} ({after.id})", inline=True)
                embed.add_field(name="Removed By", value=str(moderator), inline=True)
                await log_channel.send(embed=embed)

            added_roles = [r for r in after.roles if r not in before.roles]
            removed_roles = [r for r in before.roles if r not in after.roles]
            if added_roles or removed_roles:
                entry = await self.fetch_audit_entry(after.guild, discord.AuditLogAction.member_role_update, after.id)
                if entry:
                    embed = discord.Embed(
                        title="Roles Updated",
                        color=discord.Color.blurple(),
                        timestamp=datetime.now(timezone.utc)
                    )
                    embed.add_field(name="User", value=f"{after} ({after.id})", inline=True)
                    embed.add_field(name="Moderator", value=f"{entry.user}", inline=True)

                    if added_roles:
                        embed.add_field(name="Added", value=", ".join([r.mention for r in added_roles]), inline=False)
                    if removed_roles:
                        embed.add_field(name="Removed", value=", ".join([r.mention for r in removed_roles]), inline=False)

                    await log_channel.send(embed=embed)

            # --- Nickname Changes ---
            if before.nick != after.nick:
                entry = await self.fetch_audit_entry(after.guild, discord.AuditLogAction.member_update, after.id)
                moderator = entry.user if entry and entry.user.id != after.id else after

                embed = discord.Embed(
                    title="Nickname Changed",
                    color=discord.Color.light_gray(),
                    timestamp=datetime.now(timezone.utc)
                )
                embed.add_field(name="User", value=f"{after} ({after.id})", inline=True)
                embed.add_field(name="Changed By", value=f"{moderator}", inline=True)
                embed.add_field(name="Before", value=before.nick or "*None*", inline=False)
                embed.add_field(name="After", value=after.nick or "*None*", inline=False)
                await log_channel.send(embed=embed)

        except Exception as e:
            print(f"[ERROR] Error logging member update: {e}")

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.guild or message.guild.id != self.config["guild_id"] or message.author.bot:
            return

        log_channel = self.get_log_channel(message.guild)
        if not log_channel:
            return

        try:
            entry = await self.fetch_audit_entry(message.guild, discord.AuditLogAction.message_delete, message.author.id)
            moderator = entry.user if entry else "User (self-delete)"

            content = message.content or "*No text content*"
            if len(content) > 1000:
                content = content[:1000] + "..."

            embed = discord.Embed(
                title="Message Deleted",
                color=discord.Color.red(),
                timestamp=datetime.now(timezone.utc)
            )
            embed.add_field(name="Author", value=f"{message.author} ({message.author.id})", inline=True)
            embed.add_field(name="Channel", value=message.channel.mention, inline=True)
            embed.add_field(name="Deleted By", value=str(moderator), inline=True)
            embed.add_field(name="Content", value=f"```{content}```", inline=False)

            if message.attachments:
                attachments = "\n".join([f"[{a.filename}]({a.url})" for a in message.attachments])
                embed.add_field(name="Attachments", value=attachments, inline=False)

            await log_channel.send(embed=embed)

        except Exception as e:
            print(f"[ERROR] Error logging message delete: {e}")

    # --- Message Edits ---
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not after.guild or after.guild.id != self.config["guild_id"] or after.author.bot:
            return
        if before.content == after.content:
            return

        log_channel = self.get_log_channel(after.guild)
        if not log_channel:
            return

        try:
            before_content = before.content or "*No text content*"
            after_content = after.content or "*No text content*"

            if len(before_content) > 1000:
                before_content = before_content[:1000] + "..."
            if len(after_content) > 1000:
                after_content = after_content[:1000] + "..."

            embed = discord.Embed(
                title="Message Edited",
                color=discord.Color.blue(),
                timestamp=datetime.now(timezone.utc)
            )
            embed.add_field(name="Author", value=f"{after.author} ({after.author.id})", inline=True)
            embed.add_field(name="Channel", value=after.channel.mention, inline=True)
            embed.add_field(name="Message", value=f"[Jump to Message]({after.jump_url})", inline=True)
            embed.add_field(name="Before", value=f"```{before_content}```", inline=False)
            embed.add_field(name="After", value=f"```{after_content}```", inline=False)

            await log_channel.send(embed=embed)
        except Exception as e:
            print(f"[ERROR] Error logging message edit: {e}")

    # --- Bulk Delete ---
    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        if not messages:
            return

        first = list(messages)[0]
        if not first.guild or first.guild.id != self.config["guild_id"]:
            return

        log_channel = self.get_log_channel(first.guild)
        if not log_channel:
            return

        try:
            entry = await self.fetch_audit_entry(first.guild, discord.AuditLogAction.message_bulk_delete, first.author.id)
            moderator = entry.user if entry else "Unknown"

            embed = discord.Embed(
                title="🧹 Bulk Messages Deleted",
                color=discord.Color.red(),
                timestamp=datetime.now(timezone.utc)
            )
            embed.add_field(name="Amount", value=f"{len(messages)} messages", inline=True)
            embed.add_field(name="Channel", value=first.channel.mention, inline=True)
            embed.add_field(name="Deleted By", value=str(moderator), inline=True)

            await log_channel.send(embed=embed)
        except Exception as e:
            print(f"[ERROR] Error logging bulk delete: {e}")


async def setup(bot):
    await bot.add_cog(ModLog(bot))
