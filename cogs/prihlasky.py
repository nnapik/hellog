import re
import importlib
from discord.ext import commands

class Prihlasky(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        for role in member.guild.roles:
            if (role.name == 'Outsider'):
                await member.add_roles(role)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.name == 'prihlaska-prazdna':
            nick = re.findall(r'Jméno postavy:?\s*(\w*)', message.content)
            if nick is not None:
                nickname = nick[0]
                await message.channel.edit(name='prihlaska-' + nickname)
                await message.channel.category.create_text_channel("prihlaska-prazdna")

    @commands.command()
    async def archiv(self, ctx):
        channel = ctx.channel
        if channel.name.startswith('prihlaska-'):
            for category in ctx.guild.categories:
                if (category.name == 'archiv-prihlasek'):
                    await channel.edit(category=category)
                    await channel.edit(sync_permissions=True)
                    await channel.edit(position=0)
                    break
