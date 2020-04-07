import re
import importlib
from discord.ext import commands

class Grip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def grip(self, ctx, message):
        if (ctx.author.voice is None or ctx.author.voice.channel is None):
            await ctx.send("Please connect to voice channel first")
            return
        if len(ctx.message.mentions) > 0:
            for m in ctx.message.mentions:
                if m.voice is None or m.voice.channel is None:
                    await ctx.send("Member needs to be connected first to be gripped")
                    return
                if m.voice.channel == ctx.channel:
                    await ctx.send("Member already connected")
                    return
                await m.move_to(ctx.author.voice.channel)

