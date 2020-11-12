import asyncio
import logging
import os
import discord
from discord.ext import commands

class Log(commands.Cog):
    def __init__(self, bot):
        bot.logger.info("Log cog initilizing")
        self.bot = bot
        bot.logger.info("Log cog initilized")

    async def log(self, message, guild):
        await self.bot.log(message, guild)

    async def logToChannel(self, message, channel):
        await self.bot.logToChannel(message, channel)

    async def logSpam(self, message, guild):
        await self.bot.logSpam(message, guild)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author != self.bot.user:
            self.bot.logger.info(f'{message.author.display_name}:{message.content}')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.log(f'Member **{str(member)}({member.display_name})** was removed or left', member.guild)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if (before.display_name != after.display_name):
            await self.log(f'**{before.display_name}** was renamed to: **{after.display_name}**', after.guild)

        if (set(before.roles) != set(after.roles)):
            removed = set(before.roles) - set(after.roles)
            added = set(after.roles) - set(before.roles)
            if any(removed):
                removed = ', '.join([r.name for r in removed])
                await self.log(f'[{removed}] roles were removed from **{after.display_name}**', after.guild)
            if any(added):
                added = ', '.join([r.name for r in added])
                await self.log(f'[{added}] roles were added to **{after.display_name}**', after.guild)

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        #TODO add more options. currently it only supports server name
        await self.log(f'Server **{str(before)}** was changed from **{str(before)}** to **{str(after)}**', after)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        await self.log(f'Role **{str(role)}** was created', role.guild)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        await self.log(f'Role **{str(role)}** was deleted', role.guild)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        pass
    #await self.log(f'Role **{str(before)}** was updated', after.guild)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is None:
            await self.logSpam(f'**{str(member)}({member.display_name})** has joined **{after.channel.name}**', member.guild)
        elif after.channel is None:
            await self.logSpam(f'**{str(member)}({member.display_name})** has left **{before.channel.name}**', member.guild)
        elif before.channel.name != after.channel.name:
            await self.logSpam(f'**{str(member)}({member.display_name})** has changed channel from "{before.channel.name}" to "{after.channel.name}"', member.guild)

        if before.deaf != after.deaf:
            if (after.deaf):
                await self.logSpam(f'**{str(member)}({member.display_name})** was deafened by the server', member.guild)
            else:
                await self.logSpam(f'**{str(member)}({member.display_name})** was undeafened by the server', member.guild)
        if before.mute != after.mute:
            if (after.mute):
                await self.logSpam(f'**{str(member)}({member.display_name})** was muted by the server', member.guild)
            else:
                await self.logSpam(f'**{str(member)}({member.display_name})** was unmuted by the server', member.guild)
        if before.self_mute != after.self_mute:
            if (after.self_mute):
                await self.logSpam(f'**{str(member)}({member.display_name})** has muted themself', member.guild)
            else:
                await self.logSpam(f'**{str(member)}({member.display_name})** has unmuted themself', member.guild)
        if before.self_deaf != after.self_deaf:
            if (after.self_deaf):
                await self.logSpam(f'**{str(member)}({member.display_name})** has deafened themself', member.guild)
            else:
                await self.logSpam(f'**{str(member)}({member.display_name})** has undeafened themself', member.guild)
        if before.afk != after.afk:
            if (after.afk):
                await self.logSpam(f'**{str(member)}({member.display_name})** went AFK', member.guild)
            else:
                await self.logSpam(f'**{str(member)}({member.display_name})** came back from AFK', member.guild)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        await self.log(f'Server **{str(guild)}has banned **{str(user)}**', guild)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        await self.log(f'Server **{str(guild)}has unbanned **{str(user)}**', guild)

    @commands.Cog.listener()
    async def on_group_join(self, channel, user):
        await self.logSpam(f'**{str(user)}** joined **{str(channel)}**', channel.guild)

    @commands.Cog.listener()
    async def on_group_remove(self, channel, user):
        await self.logSpam(f'**{str(user)}** left **{str(channel)}**', channel.guild)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.log(f'Member **{str(member)}({member.display_name})** joined', member.guild)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        await self.log(f'**Channel {str(channel)}** created', channel.guild)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        await self.log(f'**Channel {str(channel)}** deleted', channel.guild)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        if (before.name != after.name):
            await self.log(f'Channel **{before.name}** was renamed to **{after.name}**', after.guild)

        if (before.category is None and after.category is not None):
            await self.log(f'Channel **{after.name}** was moved to **{after.category.name}**', after.guild)
        elif (before.category is not None and after.category is None):
            await self.log(f'Channel **{after.name}** was removed from category **{before.category.name}**', after.guild)

        if (before.category != after.category):
            await self.log(f'Channel **{after.name}** changed category from **{before.category.name}** to **{after.category.name}**', after.guild)
