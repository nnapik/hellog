import asyncio
import discord
import logging
import os
import re
import youtube_dl


# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class MyClient(discord.Client):
    async def connect_to_voice(self, channel):
        if self.vclient is None:
            self.vclient = await channel.connect()
        else:
            await self.vclient.move_to(channel)

    async def log(self, message, guild):
        await self.logChannels[guild.id].send(message)
        self.logger.info(message)

    async def logToChannel(self, message, channel):
        await channel.send(message)
        self.logger.info(message)

    async def logSpam(self, message, guild):
        await self.logSpamChannels[guild.id].send(message)
        self.logger.info(message)

    async def on_ready(self):
        self.vclient = None
        self.logger = logging.getLogger('Discord.bot')
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler('Discord.log')
        fh.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

        self.logChannels = {}
        self.logSpamChannels = {}
        self.deleteChannel = {}
        self.logger.info('logged on as ' + str(self.user))
        for c in self.get_all_channels():
            if c.name == 'log':
                self.logChannels[c.guild.id] = c
            elif c.name == 'log-spam':
                self.logSpamChannels[c.guild.id] = c
            elif c.name == 'deleted':
                self.deleteChannel[c.guild.id] = c
        for c in self.logChannels:
            self.logger.info(f'found channel: {self.logChannels[c].name} on server: **{self.logChannels[c].guild.name}**')
        for c in self.logSpamChannels:
            self.logger.info(f'found spam channel: {self.logSpamChannels[c].name} on server: **{self.logSpamChannels[c].guild.name}**')
        for c in self.deleteChannel:
            self.logger.info(f'found channel: {self.deleteChannel[c].name} on server: **{self.deleteChannel[c].guild.name}**')
        if (discord.opus.is_loaded()):
            self.logger.info('Voice lib loaded')
        else:
            self.logger.info('Unable to load voice library')

    async def processVoice(self, message):
        url = message.content[7:]
        self.logger.info('Request to stream url: ' + url)

        if not discord.opus.is_loaded():
            await self.logToChannel('Unable to load voice library', message.channel)
            return

        if not message.author.voice:
            await self.logToChannel('User not connected to voice channel', message.channel)
            return

        blacklist = ['Dungeon', 'Raid', 'Arena', 'BG']
        if any(map(message.author.voice.channel.name.startswith, blacklist)):
            await self.logToChannel('Unable to broadcast in Dungeon, Raid, Arena or BG channel', message.channel)
            return

        await self.connect_to_voice(message.author.voice.channel)
        if (self.vclient.is_playing()):
            self.vclient.stop()
        player = await YTDLSource.from_url(url, loop=self.loop)
        self.vclient.play(player, after=lambda e: self.logger.error('Player error: %s' % e) if e else None)

    async def on_message(self, message):
        if message.author == self.user:
            return
        async with message.channel.typing():
            if message.content == 'ping':
                msg = 'Pong back to ' + message.author.mention
                await message.channel.send(msg)
                self.logger.info(msg)
            if message.content == '!novoice' and self.vclient is not None:
                await self.vclient.disconnect()
                self.vclient = None
            if message.content.startswith('!voice'):
                await self.processVoice(message)

    async def on_message_delete(self, message):
        channel = self.deleteChannel[message.guild.id]
        if message.channel.id == channel.id:
            return
        s = r"```?"
        r = r""
        message_escaped = '```' + re.sub(s, r, message.content) + '```'

        if len(message.embeds) > 0:
            message_escaped = message_escaped + '\nEmbeded links:'
        for e in message.embeds:
            message_escaped = message_escaped + '\n' + e.url

        msg = f'deleted message from: **{message.author.display_name}** in channel **{message.channel.name}**\nMessage:\n{message_escaped}'
        await channel.send(content=msg)

    async def on_guild_channel_create(self, channel):
        await self.log(f'**Channel {str(channel)}** created', channel.guild)

    async def on_guild_channel_delete(self, channel):
        await self.log(f'**Channel {str(channel)}** deleted', channel.guild)

    async def on_guild_channel_update(self, before, after):
        if (before.name != after.name):
            await self.log(f'Channel **{before.name}** was renamed to **{after.name}**', after.guild)

        if (before.category is None and after.category is not None):
            await self.log(f'Channel **{after.name}** was moved to **{after.category.name}**', after.guild)
        elif (before.category is not None and after.category is None):
            await self.log(f'Channel **{after.name}** was removed from category **{before.category.name}**', after.guild)

        if (before.category != after.category):
            await self.log(f'Channel **{after.name}** changed category from **{before.category.name}** to **{after.category.name}**', after.guild)

    async def on_member_join(self, member):
        await self.log(f'Member **{str(member)}** joined', member.guild)
        for role in member.guild.roles:
            if (role.name == 'Outsider'):
                await member.add_roles(role)

    async def on_member_remove(self, member):
        await self.log(f'Member **{str(member)}** was removed or left', member.guild)

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

    async def on_guild_update(self, before, after):
        await self.log(f'Server **{str(before)}** was changed from **{str(before)}** to **{str(after)}**', after.guild)

    async def on_guild_role_create(self, role):
        await self.log(f'Role **{str(role)}** was created', role.guild)

    async def on_guild_role_delete(self, role):
        await self.log(f'Role **{str(role)}** was deleted', role.guild)

    async def on_guild_role_update(self, before, after):
        pass
        await self.log(f'Role **{str(before)}** was updated', after.guild)

    async def on_voice_state_update(self, member, before, after):
        if before.channel is None:
            await self.logSpam(f'**{str(member)}** has joined **{after.channel.name}**', member.guild)
        elif after.channel is None:
            await self.logSpam(f'**{str(member)}** has left **{before.channel.name}**', member.guild)
        elif before.channel.name != after.channel.name:
            await self.logSpam(f'**{str(member)}** has changed channel from "{before.channel.name}" to "{after.channel.name}"', member.guild)

        if before.deaf != after.deaf:
            if (after.deaf):
                await self.logSpam(f'**{str(member)}** was deafened by the server', member.guild)
            else:
                await self.logSpam(f'**{str(member)}** was undeafened by the server', member.guild)
        if before.mute != after.mute:
            if (after.mute):
                await self.logSpam(f'**{str(member)}** was muted by the server', member.guild)
            else:
                await self.logSpam(f'**{str(member)}** was unmuted by the server', member.guild)
        if before.self_mute != after.self_mute:
            if (after.self_mute):
                await self.logSpam(f'**{str(member)}** has muted themself', member.guild)
            else:
                await self.logSpam(f'**{str(member)}** has unmuted themself', member.guild)
        if before.self_deaf != after.self_deaf:
            if (after.self_deaf):
                await self.logSpam(f'**{str(member)}** has deafened themself', member.guild)
            else:
                await self.logSpam(f'**{str(member)}** has undeafened themself', member.guild)
        if before.afk != after.afk:
            if (after.afk):
                await self.logSpam(f'**{str(member)}** went AFK', member.guild)
            else:
                await self.logSpam(f'**{str(member)}** came back from AFK', member.guild)

    async def on_member_ban(self, guild, user):
        await self.log(f'Server **{str(guild)}has banned **{str(user)}**', guild)

    async def on_member_unban(self, guild, user):
        await self.log(f'Server **{str(guild)}has unbanned **{str(user)}**', guild)

    async def on_group_join(self, channel, user):
        await self.logSpam(f'**{str(user)}** joined **{str(channel)}**', channel.guild)

    async def on_group_remove(self, channel, user):
        await self.logSpam(f'**{str(user)}** left **{str(channel)}**', channel.guild)


client = MyClient()
secret = os.environ['BOT_SECRET']
client.run(secret)
