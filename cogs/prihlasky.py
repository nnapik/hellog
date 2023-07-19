import re
import importlib
from discord.ext import commands
from discord import TextChannel

class Prihlasky(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_role_name = 'Navsteva'
        self.member_role_name = 'Member'

    @commands.Cog.listener()
    async def on_member_join(self, member):
        init_role = self.bot.get_role(member.guild, self.init_role_name)
        if (init_role is not None):
            await member.add_roles(init_role)

    @staticmethod
    def try_get_char(texts):
        regexes = [
            r'[nN]ick\s*:\s*([\w]*)(?:-[\w\' -]*)?',
            r'Jm[ée]no postavy\s*:\s*([\w]*)(?:-[\w\' -]*)?',
            r'https://raider.io/characters/eu/[\w\']+/(\w+)\??',
            r'https://worldofwarcraft.com/en-gb/character/eu/[\w\']+/(\w+)',
            r'https://worldofwarcraft.blizzard.com/en-gb/character/eu/[\w\']+/(\w+)'
        ]
        for text in texts:
            for r in regexes:
                nick = re.findall(r, text)
                if nick is not None and len(nick) != 0:
                    return nick[0]

        return None

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id: #filter out own messages
            return
        if not hasattr(message.channel, 'name') or message.channel.name != 'prihlaska-prazdna':
            return
        test_texts = []
        for e in message.embeds:
            test_texts.append(str(e.url))
        test_texts.append(message.content)

        nick = self.try_get_char(test_texts)
        print (nick)
        if nick is None:
            nickname = 'null'
        else:
            nickname = nick

        print (nickname)
        await message.channel.edit(name='prihlaska-' + nickname)
        await message.channel.category.create_text_channel("prihlaska-prazdna")

    async def fix_full_archiv(self, category):
        if len(category.channels) >= 50:
            await category.edit(name = 'archiv-prihlasek-' + str(category.id))
            await category.clone(name = 'archiv-prihlasek')
            dw = self.bot.get_cog('Download')
            await dw.backup_category(category)

    @commands.command()
    async def archiv(self, ctx):
        channel = ctx.channel
        if channel.name.startswith('prihlaska-'):
            for category in ctx.guild.categories:
                if (category.name == 'archiv-prihlasek'):
                    await channel.move(beginning=True, category=category, sync_permissions=True)
                    await self.fix_full_archiv(category)
                    break

    @commands.has_any_role('Personalni oddeleni (HR)', 'Guild Officir', 'Admin')
    @commands.command()
    async def inv(self, ctx):
        await self.archiv(ctx)
        channel = ctx.channel
        if channel.name.startswith('prihlaska-'):
            nick = re.match(r'prihlaska-(.*)', channel.name)[1].title()
            messages = [h async for h in channel.history(limit=123)]
            first = messages[-1]
            author = first.author
            init_role = self.bot.get_role(ctx.guild, self.init_role_name)
            member_role = self.bot.get_role(ctx.guild, self.member_role_name)
            if (member_role is None or init_role is None):
                raise GuildApplicationException("Couldn't identify roles")
            await author.add_roles(member_role)
            if ((author.get_role(init_role.id)) is not None):
                await author.remove_roles(init_role, reason="invited")
            await author.edit(nick=nick)

class GuildApplicationException(Exception):
    def __init__(message):
        super(message)
