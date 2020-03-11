import asyncio
import logging
import os

import discord

from discord.ext import commands
from discord.ext.commands import when_mentioned_or

from logger import Logger
from cogs.cogs import Cogs
# from cogs.voice import Voice

secret = os.environ['BOT_SECRET']

logger = Logger()

class MyBot(commands.Bot):
    def __init__(self, command_prefix, logger):
        super().__init__(command_prefix)
        self.logger = logger
        self.logChannels = {}
        self.logSpamChannels = {}
        self.deleteChannels = {}
    async def on_ready(self):
        self.logger.info('logged on as ' + str(self.user))

        for c in self.get_all_channels():
            if (c.name == 'log'):
                self.logChannels[c.guild.id] = c
            if (c.name == 'log-spam'):
                self.logSpamChannels[c.guild.id] = c
            if (c.name == 'deleted'):
                self.deleteChannels[c.guild.id] = c

        self.logger.info('Found log channels on:')
        for l in self.logChannels:
            self.logger.info(self.logChannels[l].guild.name)

        self.logger.info('Found logSpam channels on:')
        for s in self.logSpamChannels:
            self.logger.info(self.logSpamChannels[s].guild.name)

        self.logger.info('Found delete channels on:')
        for d in self.deleteChannels:
            self.logger.info(self.deleteChannels[d].guild.name)


    async def log(self, message, guild):
        await self.logChannels[guild.id].send(message)
        self.logger.info(message)

    async def logToChannel(self, message, channel):
        await channel.send(message)
        self.logger.info(message)

    async def logSpam(self, message, guild):
        await self.logSpamChannels[guild.id].send(message)
        self.logger.info(message)


client = MyBot(command_prefix='!', logger=logger)
client.add_cog(Cogs(client))

client.run(secret)
