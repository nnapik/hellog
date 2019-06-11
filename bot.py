import discord


class MyClient(discord.Client):
    async def log(self, message, guild):
        await self.logChannels[guild.id].send(message)
        print(message)

    async def logToChannel(self, message, channel):
        await channel.send(message)
        print(message)

    async def logSpam(self, message, guild):
        await self.logSpamChannels[guild.id].send(message)
        print(message)

    async def on_ready(self):
        self.logChannels = {}
        self.logSpamChannels = {}
        print('logged on as', self.user)
        for c in self.get_all_channels():
            if c.name == 'log':
                self.logChannels[c.guild.id] = c
            elif c.name == 'log-spam':
                self.logSpamChannels[c.guild.id] = c
        for c in self.logChannels:
            print(f'found channel: {self.logChannels[c].name} on server: **{self.logChannels[c].guild.name}**')
        for c in self.logSpamChannels:
            print(f'found spam channel: {self.logSpamChannels[c].name} on server: **{self.logSpamChannels[c].guild.name}**')

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content == 'ping':
            await self.logToChannel(f'pong back to **{str(message.author)}**', message.channel)
            await self.logSpam(f'received ping from **{str(message.author)}**', message.guild)

    async def on_guild_channel_create(self, channel):
        await self.log(f'**{str(channel)}** created', channel.guild)

    async def on_guild_channel_delete(self, channel):
        await self.log(f'**{str(channel)}** deleted', channel.guild)

    async def on_guild_channel_update(self, before, after):
        if (before.name != after.name):
            await self.log(f'Channel **{before.name}** was renamed to **{after.name}**', after.guild)

        if (before.category is None and after.category is not None):
            await self.log(f'Channel **{after.name}** was moved to **{after.category.name}**', after.guild)
        elif (before.category is not None and after.category is None):
            await self.log(f'Channel **{after.name}** was removed from category **{before.category.name}**', after.guild)

        if (before.category != after.category):
            await self.log(f'Channel **{after.name}** changed category from **{before.category.name}** to **{after.category.name}**', after.guild)

    async def on_member_join(self, member):
        await self.log(f'Member **{str(member)}** joined', member.guild)

    async def on_member_remove(self, member):
        await self.log(f'Member **{str(member)}** was removed or left', member.guild)

    async def on_member_update(self, before, after):
        if (before.display_name != after.display_name):
            await self.log(f'**{before.display_name}** was renamed to: **{after.display_name}**', after.guild)

        if (set(before.roles) != set(after.roles)):
            removed = set(before.roles) - set(after.roles)
            added = set(after.roles) - set(before.roles)
            if any(removed):
                removed = ', '.join([r.name for r in removed])
                await self.log(f'[{removed}] roles were removed from **{after.display_name}**', after.guild)
            if any(added):
                added = ', '.join([r.name for r in added])
                await self.log(f'[{added}] roles were added to **{after.display_name}**', after.guild)

    async def on_guild_update(self, before, after):
        await self.log(f'Server **{str(before)}** was changed from **{str(before)}** to **{str(after)}**', after.guild)

    async def on_guild_role_create(self, role):
        await self.log(f'Role **{str(role)}** was created', role.guild)

    async def on_guild_role_delete(self, role):
        await self.log(f'Role **{str(role)}** was deleted', role.guild)

    async def on_guild_role_update(self, before, after):
        pass
        await self.log(f'Role **{str(before)}** was updated', after.guild)

    async def on_voice_state_update(self, member, before, after):
        if before.channel is None:
            await self.logSpam(f'**{str(member)}** has joined **{after.channel.name}**', member.guild)
        elif after.channel is None:
            await self.logSpam(f'**{str(member)}** has left **{before.channel.name}**', member.guild)
        elif before.channel.name != after.channel.name:
            await self.logSpam(f'**{str(member)}** has changed channel from "{before.channel.name}" to "{after.channel.name}"', member.guild)

        if before.deaf != after.deaf:
            if (after.deaf):
                await self.logSpam(f'**{str(member)}** was deafened by the server', member.guild)
            else:
                await self.logSpam(f'**{str(member)}** was undeafened by the server', member.guild)
        if before.mute != after.mute:
            if (after.mute):
                await self.logSpam(f'**{str(member)}** was muted by the server', member.guild)
            else:
                await self.logSpam(f'**{str(member)}** was unmuted by the server', member.guild)
        if before.self_mute != after.self_mute:
            if (after.self_mute):
                await self.logSpam(f'**{str(member)}** has muted themself', member.guild)
            else:
                await self.logSpam(f'**{str(member)}** has unmuted themself', member.guild)
        if before.self_deaf != after.self_deaf:
            if (after.self_deaf):
                await self.logSpam(f'**{str(member)}** has deafened themself', member.guild)
            else:
                await self.logSpam(f'**{str(member)}** has undeafened themself', member.guild)
        if before.afk != after.afk:
            if (after.afk):
                await self.logSpam(f'**{str(member)}** went AFK', member.guild)
            else:
                await self.logSpam(f'**{str(member)}** came back from AFK', member.guild)

    async def on_member_ban(self, guild, user):
        await self.log(f'Server **{str(guild)}has banned **{str(user)}**', guild)

    async def on_member_unban(self, guild, user):
        await self.log(f'Server **{str(guild)}has unbanned **{str(user)}**', guild)

    async def on_group_join(self, channel, user):
        await self.logSpam(f'**{str(user)}** joined **{str(channel)}**', channel.guild)

    async def on_group_remove(self, channel, user):
        await self.logSpam(f'**{str(user)}** left **{str(channel)}**', channel.guild)


client = MyClient()
client.run('NTg2MTE3Mjg3MTQwOTE3MjYw.XPjW_Q.83TbJxOH_E9z6CEXmCxu7y8b-xk')
