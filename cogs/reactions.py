import discord
from discord import Embed
import re
from discord.ext import commands

class Reactions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.react_messages = {}

    @commands.is_owner()
    @commands.command(name='sync_raider')
    async def sync_raider(self, ctx):
        g = ctx.message.guild
        await ctx.message.delete()
        raider = self.bot.get_role(g, 'Raider')
        if raider is None:
            return
        x_group = self.bot.get_role(g, 'X group')
        if x_group is None:
            return
        e_group = self.bot.get_role(g, 'Early group')
        if e_group is None:
            return

        for m in g.members:
            if raider in m.roles:
                continue
            if x_group in m.roles or e_group in m.roles:
                await m.add_roles(raider)
                

    @commands.has_any_role('Personalni oddeleni (HR)', 'Guild Officir', 'Admin', 'Raid Leader')
    @commands.command(name='add_role')
    async def add_role(self, ctx, **attrs):
        regex = r'^!add_role\s+(.*?)\s+(.*?)$'
        values = re.findall(regex, ctx.message.content)
        emoji, role_name = values[0]

        role_to_add = self.bot.get_role(ctx.message.guild, role_name)
        author_max_role = max(ctx.author.roles)
        if role_to_add > author_max_role:
            await self.bot.admin.send(f'{ctx.author} tried to add_role for higher role than he can {ctx.message.jump_url}')
            return
        

        embed = Embed()
        embed.title = f"Reakci {emoji} na tuto zpravu ziskate/ztratite roli {role_name}"
        embed.add_field(name='emote', value=emoji)
        embed.add_field(name='role', value=role_name)
        await ctx.message.delete()
        response = await ctx.send(embed=embed)
        await response.add_reaction(emoji)
        

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        # <RawReactionActionEvent 
        # message_id=126 
        # user_id=176 
        # channel_id=586 
        # guild_id=58 
        # emoji=<PartialEmoji animated=False name='🥳' id=None> 
        # event_type='REACTION_ADD' 
        # member=<Member id=176 name='admin' global_name='admin' bot=False nick='admin' guild=<Guild id=586 name='admin_test' shard_id=0 chunked=True member_count=5>> 
        # message_author_id=176 
        # burst=False 
        # burst_colours=[] 
        # type=<ReactionType.normal: 0>>

        if self.bot.user.id == payload.user_id:
            # ignore events from the owner (bot)
            return
        if (payload.channel_id != self.bot.role_channels[payload.guild_id].id):
            # not a dej-mi-roli channel
            return
        if (payload.message_author_id != self.bot.user.id):
            # not a message from the bot
            return
        channel = self.bot.get_channel(payload.channel_id)

        message = await channel.fetch_message(payload.message_id)
        await message.remove_reaction(payload.emoji, payload.member)

        if not message.embeds:
            await self.bot.admin.send('No embeds found')
            return

        emoji = None
        role_name = None
        for embed in message.embeds:
            for f in embed.fields:
                if f.name == 'emote':
                    emoji = f.value
                if f.name == 'role':
                    role_name = f.value

        if emoji is None or role_name is None:
            await self.bot.admin.send('embeds not parsable, ', message)
            return


        if emoji != payload.emoji.name:
            await self.bot.admin.send(f'Invalid Emoji, expected: {emoji}, received: {payload.emoji.name}')
            return

        role = self.bot.get_role(payload.member.guild, role_name)
        if role is None:
            await self.bot.admin.send('Unable to get role')
            return
        if (role in payload.member.roles):
            await payload.member.remove_roles(role)
        else:
            await payload.member.add_roles(role)




        

