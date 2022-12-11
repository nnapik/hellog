import os
import json
from discord.ext import commands
import discord
import boto3
from botocore.client import Config

class log:
    def __init__(self, m):
        self.id = m.id
        self.server = m.channel.guild.name
        self.timestamp = m.created_at.isoformat()
        self.channel = m.channel.name
        self.channel_id = m.channel.id
        self.category = m.channel.category.name
        self.category_id = m.channel.category.id
        self.author_id = m.author.id
        self.author_nick = m.author.display_name
        self.author_disc = m.author.discriminator
        self.author = m.author.name
        self.message = m.content
    def __lt__(self, other):
        return self.id < other.id

def obj_dict(obj):
    return obj.__dict__

class Download(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = boto3.Session()
        self.client = self.session.client('s3',
                        region_name='fra1',
                        endpoint_url='https://fra1.digitaloceanspaces.com',
                        aws_access_key_id=os.getenv('SPACES_KEY'),
                        aws_secret_access_key=os.getenv('SPACES_SECRET'),
                        config=Config(s3={'addressing_style': 'virtual'}))
        self.bucket = os.getenv('SPACES_BUCKET')

    def upload(self, fname, guild, path):
        self.client.upload_file(fname, self.bucket, f'{guild}/{path}/'+fname)


    @commands.command(name='download')
    @commands.is_owner()
    async def download(self, ctx, **attrs):
        author = ctx.message.author
        await ctx.message.delete()
        content = await self.dw_channel(ctx.channel)
        fname = ctx.channel.name + '.json'
        self.dump(content, fname)
        self.upload(fname, ctx.channel.guild.name, ctx.channel.category.name)

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
    async def backup_category(self, ctx, **attrs):
        author = ctx.message.author
        await ctx.message.delete()
        for c in ctx.channel.category.channels:
            content = await self.dw_channel(c)
            fname = c.name + '.json'
            self.dump(content, fname)
            self.upload(fname, c.guild.name, c.category.name)

    @commands.command(name='delete_category')
    @commands.is_owner()
    async def delete_category(self, ctx, **attrs):
        author = ctx.message.author
        await ctx.message.delete()
        for c in ctx.channel.category.channels:
            await c.delete(reason="backup and cleanup")

