import re
from discord.embed import Embed
from discord.ext import commands
from discord import HTTPException


class Auto(commands.Cog):
    def __init__(self, bot):
        bot.logger.info("Auto cog initilizing")
        self.bot = bot
        self.channels = {}
        bot.logger.info("Auto cog initilized")

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        channel = self.bot.deleteChannels[message.guild.id]
        if (message.channel.id == channel.id):
            return
        embed = Embed()
        embed.title = "Deleted Message"
        embed.author = message.author.display_name
        embed.add_field(name='category', value=message.channel.category.name)
        embed.add_field(name='channel', value=message.channel.name)
        embed.add_field(name='message', value=message.content)

        # add embeds
        message_embeds = ""
        try:
            if (len(message.embeds) > 0):
                for e in message.embeds:
                    message_embeds = message_embeds + '\n' + str(e.url)
        except HTTPException as e:
            message_embeds += '\nUnable to load embeds: ' + str(e)
        finally:
            embed.add_field(name='embeds', value=message_embeds)

        # add reactions
        reactions = ""
        try:
            if (len(message.reactions) > 0):
                for reaction in message.reactions:
                    try:
                        users = [user async for user in reaction.users()]
                        for u in users:
                            reactions = reactions + '\nUser: ' + u.display_name + ', reaction: ' + str(reaction.emoji)
                    except HTTPException as e:
                        reactions = reactions + "\nUnable to load users: " + str(e)
                        reactions = reactions + "\nCount: " + str(reaction.count) + ', reaction: ' + str(reaction.emoji)
        except HTTPException as e:
            reactions += '\nUnable to load reactions: ' + str(e)
        finally:
            embed.add_field(name='reactions', value=reactions)

        await channel.send(embed=embed)

    async def getArchivChannels(self):
        for c in self.bot.get_all_channels():
            if c.name.endswith('-archiv'):
                self.channels[c.name[:-7]] = c
        self.bot.logger.info("Auto found " + str(len(self.channels)) + " archiv channels")
        self.bot.logger.info(str(self.channels))

    @commands.command()
    @commands.is_owner()
    async def purge(self, ctx):
        await ctx.message.delete()
        channel = ctx.channel
        messages = await channel.history(limit=123).flatten()
        for m in messages[::-1]:
            if (m.pinned):
                continue
            await m.delete()

    @commands.command()
    @commands.is_owner()
    async def move(self, ctx):
        await ctx.message.delete()
        channel = ctx.channel
        if channel.name not in self.channels.keys():
            # try to refresh channel list
            await self.getArchivChannels()
            if channel.name not in self.channels.keys():
                await ctx.send("Unable to find archiv channel")
                return

        a_channel = self.channels[channel.name]
        messages = await channel.history(limit=123).flatten()
        for m in messages[::-1]:
            if (m.pinned):
                continue

            message_escaped = await Auto.escape(m)
            msg = f'Moved message from **{m.author.display_name}** from channel **{m.channel.name}**\nTimestamp:{m.created_at}\nMessage:\n{message_escaped}'
            await a_channel.send(msg)
            await m.delete()

    async def escape(message):
        s = r"```?"
        r = r""
        # replace quotes
        message_escaped = '```' + re.sub(s, r, message.content) + '```'

        # try to add embeds
        try:
            if (len(message.embeds) > 0):
                message_escaped = message_escaped + '\nEmbeded links:'
                for e in message.embeds:
                    message_escaped = message_escaped + '\n' + str(e.url)
        except HTTPException as e:
            message_escaped += '\nUnable to load embeds: ' + str(e)

        # try to add reactions
        try:
            if (len(message.reactions) > 0):
                message_escaped = message_escaped + '\nReactions:'
                for reaction in message.reactions:
                    try:
                        users = [user async for user in reaction.users()]
                        for u in users:
                            message_escaped = message_escaped + '\nUser: ' + u.display_name + ', reaction: ' + str(reaction.emoji)
                    except HTTPException as e:
                        message_escaped = "\nCount: " + str(reaction.count) + ', reaction: ' + str(reaction.emoji)
        except HTTPException as e:
            message_escaped += '\nUnable to load reactions: ' + str(e)

        return message_escaped


