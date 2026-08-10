import asyncio
import logging
import os
import traceback

import discord

from discord.ext import commands
from discord.ext.commands import when_mentioned_or

from logger import Logger
from cogs.cogs import Cogs
# from cogs.voice import Voice
from dotenv import load_dotenv

load_dotenv()

secret = os.environ['BOT_SECRET']
prihlasky_secret = os.environ['PRIHLASKY_ADMIN_TOKEN']
prihlasky_url = os.environ['PRIHLASKY_URL']


class MyBot(commands.Bot):
    def __init__(self, command_prefix, intent, logger):
        super().__init__(command_prefix, intents=intent)
        self.logger = logger
        self.logChannels = {}
        self.logSpamChannels = {}
        self.deleteChannels = {}
        self.role_cache = {}
        self.role_channels = {}
        self.prihlasky_secret = prihlasky_secret
        self.prihlasky_url = prihlasky_url

    # Global error handler for all events
    async def on_error(self, event_method, *args, **kwargs):
        tb = traceback.format_exc()
        print(tb)
        embed = discord.Embed(title=f"Error in event: {event_method}", color=discord.Color.red())
        embed.add_field(name="Stacktrace", value=f"```{tb[:1000]}```", inline=False)
        await self.send_to_admin(embed=embed)

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("This command does not exist.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("A required argument is missing.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Command is on cooldown. Try again in {round(error.retry_after, 2)} seconds.")
        else:
            await self.send_error_to_admin(ctx.message.content, error)

    async def on_ready(self):
        if 'Cogs' not in self.cogs:
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
            if (c.name == 'dej-mi-roli'):
                self.role_channels[c.guild.id] = c

        self.logger.info('Found log channels on:')
        for l in self.logChannels:
            self.logger.info(self.logChannels[l].guild.name)

        self.logger.info('Found logSpam channels on:')
        for s in self.logSpamChannels:
            self.logger.info(self.logSpamChannels[s].guild.name)

        self.logger.info('Found delete channels on:')
        for d in self.deleteChannels:
            self.logger.info(self.deleteChannels[d].guild.name)

        self.logger.info('Found role channels on:')
        for d in self.role_channels:
            self.logger.info(self.role_channels[d].guild.name)

        self.admin = self.application.owner

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

    async def send_to_admin(self, message=None, embed=None):
        if not hasattr(self, 'admin') or self.admin is None:
            return
        await self.admin.send(message, embed=embed)

    async def send_error_to_admin(self, title, error):
        tb = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        embed = discord.Embed(title=title, color=discord.Color.red())
        embed.add_field(name="Error", value=str(error), inline=False)
        # Discord field value limit is 1024 chars
        embed.add_field(name="Stacktrace", value=f"```{tb[:1000]}```", inline=False)
        await self.send_to_admin(embed=embed)

    async def log_error(self, ctx, embed, error):
        if (embed != None):
            embed.add_field(name="server:", value=ctx.guild)
            embed.add_field(name="channel:", value=ctx.channel)
            embed.add_field(name="command:", value=ctx.command)
            embed.add_field(name="message:", value=ctx.message)
            embed.add_field(name="stacktrace:", value=error.original)
            await self.send_to_admin(content=None, embed=embed)

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
