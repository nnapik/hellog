import json
from discord.ext import commands
import discord

class log:
    def __init__(self, m):
        self.id = m.id
        self.server = m.channel.guild.name
        self.timestamp = m.created_at.isoformat()
        self.channel = m.channel.name
        self.channel_id = m.channel.id
        self.category = m.channel.category.name
        self.category_id = m.channel.category.id
        self.author = m.author.name
        self.message = m.content
    def __lt__(self, other):
        return self.id < other.id

def obj_dict(obj):
    return obj.__dict__

class Download(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='download')
    @commands.is_owner()
    async def download(self, ctx, **attrs):
        author = ctx.message.author
        await ctx.message.delete()
        content = await self.dw_channel(ctx.channel)
        fname = ctx.channel.name + '.json'
        self.dump(content, fname)
        await author.send(f'{ctx.guild.name}-{ctx.channel.category.name}-{ctx.channel.name}', file=discord.File(fname))

    async def dw_channel(self, channel):
        content = []
        async for m in channel.history():
            l = log(m)
            content.append(l)
        return content
    def dump(self, content, fname):
        with open(fname, 'w') as f:
            json.dump(sorted(content), f, default=obj_dict, indent=4)

    @commands.command(name='dw_cat')
    @commands.is_owner()
    async def dw_category(self, ctx, **attrs):
        author = ctx.message.author
        await ctx.message.delete()
        for c in ctx.channel.category.channels:
            content = await self.dw_channel(c)
            fname = c.name + '.json'
            self.dump(content, fname)
            await author.send(f'{ctx.guild.name}-{ctx.channel.category.name}-{c.name}', file=discord.File(fname))

