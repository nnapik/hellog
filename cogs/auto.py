import re
import importlib
from discord.ext import commands

class Auto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        channel = self.bot.deleteChannels[message.guild.id]
        if (message.channel.id == channel.id):
            return
        s = r"```?"
        r = r""
        message_escaped = '```' + re.sub(s, r, message.content) + '```'

        if (len (message.embeds) > 0):
            message_escaped = message_escaped + '\nEmbeded links:'
            for e in message.embeds:
                message_escaped = message_escaped + '\n' + e.url

        msg = f'deleted message from: **{message.author.display_name}** in channel **{message.channel.name}**\nMessage:\n{message_escaped}'
        await channel.send(content=msg)

