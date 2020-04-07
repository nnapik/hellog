import re
import discord
from discord.ext import commands
from .youtube import YTDLSource

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        self.vclient = None
        if (discord.opus.is_loaded()):
            self.logger.info('Voice lib loaded')
        else:
            self.logger.info('Unable to load voice library')

    async def log(self, message, guild):
        await self.bot.log(message, guild)

    async def logToChannel(self, message, channel):
        await self.bot.logToChannel(message, channel)

    async def logSpam(self, message, guild):
        await self.bot.logSpam(message, guild)

    async def voiceAlone(self):
        if (self.vclient is None):
            return
        if len(self.vclient.channel.members) == 1:
            await self.disconnect_from_voice()

    async def disconnect_from_voice(self):
        if (self.vclient is None):
            return
        await self.vclient.disconnect()
        self.vclient = None

    async def connect_to_voice(self, channel):
        if self.vclient is None or not self.vclient.is_connected():
            self.vclient = await channel.connect()
        else:
            await self.vclient.move_to(channel)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        await self.voiceAlone()

    async def processVoice(self, ctx, message):
        urlRe = re.findall("(https://www.youtube.com/watch\\?v=.{11})$", message)
        if (len(urlRe) != 1):
            await self.logToChannel('Unable to parse youtube url', ctx.channel)
            return

        url = urlRe[0]

        self.logger.info('Request from '+str(ctx.author)+' to stream url: ' + url)

#         if not discord.opus.is_loaded():
#             await self.logToChannel('Unable to load voice library', ctx.channel)
#             return

        if not ctx.author.voice:
            await self.logToChannel('User not connected to voice channel', ctx.channel)
            return

#         blacklist = ['Dungeon', 'Raid', 'Arena', 'BG']
#         if any(map(ctx.author.voice.channel.name.startswith, blacklist)):
#             await self.logToChannel('Unable to broadcast in Dungeon, Raid, Arena or BG channel', ctx.channel)
#             return

        await self.connect_to_voice(ctx.author.voice.channel)
        if (self.vclient.is_playing()): self.vclient.stop()
        player = await YTDLSource.from_url(url, loop=self.vclient.loop, stream=False)
        self.vclient.play(player, after=lambda e: self.logger.error('Player error: %s' % e) if e else None)


    @commands.command()
    async def play(self, ctx, message):
        await self.processVoice(ctx, message)

    @commands.command()
    async def stop(self, ctx):
        await self.disconnect_from_voice()

#    @commands.Cog.listener()
#    async def on_voice_state_update(self, member, before, after):
#        if (after.channel is None and self.bot.id == member.id):
#            await disconnect_from_voice()

