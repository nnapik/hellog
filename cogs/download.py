import json
from discord.ext import commands

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
        await ctx.message.delete()
        content = []
        async for m in ctx.channel.history():
            l = log(m)
            content.append(l)

        print(json.dumps(sorted(content), default=obj_dict))


