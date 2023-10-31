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
admin_id = os.environ['ADMIN_ID']


class MyBot(commands.Bot):
    def __init__(self, command_prefix, intent, logger):
        super().__init__(command_prefix, intents=intent)
        self.logger = logger
        self.logChannels = {}
        self.logSpamChannels = {}
        self.deleteChannels = {}
        self.role_cache = {}

    async def on_ready(self):
        cogs = Cogs(self)
        await client.add_cog(cogs)
        await cogs.reload_cogs()

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

        if (admin_id != ''):
            self.admin = self.get_user(int(admin_id))
            if (self.admin == None):
                self.logger.info("Found no admins, beware")
            else:
                self.logger.info(f"{self.admin.display_name} is the boss here!")

    def get_role(self, guild, role_name):
        if guild.id not in self.role_cache:
            self.role_cache[guild.id] = {}
        if role_name not in self.role_cache[guild.id]:
            for role in guild.roles:
                if role.name == role_name:
                    self.role_cache[guild.id][role_name] = role.id
        role_id = self.role_cache[guild.id][role_name]
        if role_id is None:
            return None

        return guild.get_role(role_id)

    async def log_error(self, ctx, embed, error):
        if (self.admin == None):
            pass
        if (embed != None):
            embed.add_field(name="server:", value=ctx.guild)
            embed.add_field(name="channel:", value=ctx.channel)
            embed.add_field(name="command:", value=ctx.command)
            embed.add_field(name="message:", value=ctx.message)
            embed.add_field(name="stacktrace:", value=error.original)
        await self.admin.send(content=None, embed=embed)

    async def log(self, message, guild):
        await self.logChannels[guild.id].send(message)
        self.logger.info(message)

    async def logToChannel(self, message, channel):
        await channel.send(message)
        self.logger.info(message)

    async def logSpam(self, message, guild):
        await self.logSpamChannels[guild.id].send(message)
        self.logger.info(message)


logger = Logger()
intents = discord.Intents.all()
client = MyBot(command_prefix='!', intent=intents, logger=logger)

client.run(secret)
