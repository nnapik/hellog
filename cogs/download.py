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
        s3_path = f'{guild}/{path}/'+fname
        self.bot.logger.info(f'uploading file: {s3_path}')
        self.client.upload_file(fname, self.bucket, s3_path)
        self.bot.logger.info(f'uploaded file: {s3_path}')

    async def dw_channel(self, channel):
        content = []
        async for m in channel.history():
            l = log(m)
            content.append(l)
        return content

    def get_fname(self, channel):
        return f'{channel.id}-{channel.name}.json'

    def dump(self, content, fname):
        with open(fname, 'w') as f:
            json.dump(sorted(content), f, default=obj_dict, indent=4)

    async def backup_channel(self, channel):
        content = await self.dw_channel(channel)
        fname = self.get_fname(channel)
        self.dump(content, fname)
        self.upload(fname, channel.guild.name, channel.category.name)

    async def backup_category(self, category):
        for c in category.channels:
            await self.backup_channel(c)

    @commands.command(name='dw_cat')
    @commands.is_owner()
    async def download_category_command(self, ctx, **attrs):
        await ctx.message.delete()
        await self.backup_category(ctx.channel.category)

    @commands.command(name='delete_category')
    @commands.is_owner()
    async def delete_category_command(self, ctx, **attrs):
        category = ctx.channel.category
        reason = 'backup and cleanup'
        await ctx.message.delete()
        for c in ctx.channel.category.channels:
            await self.backup_channel(c)
            await c.delete(reason=reason)
        await category.delete(reason=reason)

    @commands.command(name='dw')
    @commands.is_owner()
    async def download_channel_command(self, ctx, **attrs):
        await ctx.message.delete()
        await self.backup_channel(ctx.channel)
