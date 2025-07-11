import re
from discord import Embed
from discord.ext import commands
from discord import HTTPException


class Auto(commands.Cog):
    def __init__(self, bot):
        bot.logger.info("Auto cog initilizing")
        self.bot = bot
        self.channels = {}
        bot.logger.info("Auto cog initilized")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        # add Raider role when someone gets X or E group role
        raider = self.bot.get_role(before.guild, 'Raider')
        if raider is None:
            return

        x_group = self.bot.get_role(before.guild, 'X group')
        if x_group is None:
            return

        e_mythic = self.bot.get_role(before.guild, 'Early Mythic')
        if e_mythic is None:
            return

        e_hc = self.bot.get_role(before.guild, 'Early HC')
        if e_hc is None:
            return

        if x_group not in before.roles and x_group in after.roles:
            await after.add_roles(raider)

        if e_mythic not in before.roles and e_mythic in after.roles:
            await after.add_roles(raider)

        if e_hc not in before.roles and e_hc in after.roles:
            await after.add_roles(raider)


    @commands.Cog.listener()
    async def on_message_delete(self, message):
        self.bot.logger.info(f'deleting #{str(message)}')
        channel = self.bot.deleteChannels[message.guild.id]
        if (message.channel.id == channel.id):
            return
        embed = Embed()
        embed.title = "Deleted Message"
        embed.add_field(name='author', value=message.author.display_name, inline=False)
        embed.add_field(name='category', value=message.channel.category.name, inline=False)
        embed.add_field(name='channel', value=message.channel.name, inline=False)
        if len(message.content) < 1024:
            embed.add_field(name='message', value=message.content, inline=False)
        else:
            parts = int(len(message.content) / 1024) + 1
            for p in range(parts):
                embed.add_field(name="message_part_" + str(p), value=message.content[p * 1024:(p + 1) * 1024])

        # add embeds
        message_embeds = ""
        try:
            if (len(message.embeds) > 0):
                for e in message.embeds:
                    message_embeds = message_embeds + '\n' + str(e.url)
                embed.add_field(name='embeds', value=message_embeds, inline=False)
        except HTTPException as e:
            embed.add_field(name='embeds', value="Unable to load embeds: " + str(e))

        # add reactions
        try:
            if (len(message.reactions) > 0):
                reactions = ''
                for reaction in message.reactions:
                    reactions = reactions + "\nCount: " + str(reaction.count) + ', reaction: ' + str(reaction.emoji)
                embed.add_field(name='reactions', value=reactions, inline=False)
        except HTTPException as e:
            embed.add_field(name='reactions', value="Unable to load reactions: " + str(e))

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
        async for m in channel.history():
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


