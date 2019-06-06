import discord


class MyClient(discord.Client):
    async def log(self, message, channel=None):
        if channel is None:
            await self.logChannel.send(message)
        else:
            await channel.send(message)
        print(message)

    async def on_ready(self):
        print('logged on as', self.user)
        self.logChannel = self.get_channel(422054940295561229)
        print('found channel: ' + str(self.logChannel))

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content == 'ping':
            await self.log('pong back to ' + str(message.author), message.channel)
            lmessage = ('received ping from ' + str(message.author))
            await self.log(lmessage)

    async def on_guild_channel_create(self, channel):
        message = ('Channel ' + str(channel) + ' created')
        await self.log(message)

    async def on_guild_channel_delete(self, channel):
        message = ('Channel ' + str(channel) + ' deleted')
        await self.log(message)

    async def on_guild_channel_update(self, before, after):
        if (before.name != after.name):
            await self.log('Channel ' + before.name + ' was renamed to ' + after.name)
#        if (before.position != after.position):
#            await self.log('Channel ' + after.name + ' was moved')

        if (before.category is None and after.category is not None):
            await self.log('Channel ' + after.name + ' was moved to ' + after.category)
        elif (before.category is not None and after.category is None):
            await self.log('Channel ' + after.name + ' was removed from ' + before.category)
        if (before.category != after.category):
            await self.log('Channel ' + after.name + ' changed category from ' + before.category + ' to ' + after.category)

    async def on_member_join(self, member):
        message = ('Member ' + str(member) + ' joined')
        await self.log(message)

    async def on_member_remove(self, member):
        message = ('Member ' + str(member) + ' was removed or left')
        await self.log(message)

    async def on_member_update(self, before, after):
        if (before.display_name != after.display_name):
            await self.log(before.display_name + ' was renamed to: ' + after.display_name)

        if (set(before.roles) != set(after.roles)):
            removed = set(before.roles) - set(after.roles)
            added = set(after.roles) - set(before.roles)
            if any(removed):
                removed = [r.name for r in removed]
                await self.log('[' + ', '.join(removed) + '] roles were removed from ' + after.display_name)
            if any(added):
                added = [r.name for r in added]
                await self.log('[' + ', '.join(added) + '] roles were added to ' + after.display_name)

    async def on_guild_update(self, before, after):
        message = ('Server ' + str(before) + ' was changed from ' + str(before) + ' to ' + str(after))
        await self.log(message)

    async def on_guild_role_create(self, role):
        message = ('Role ' + str(role) + ' was created')
        await self.log(message)

    async def on_guild_role_delete(self, role):
        message = ('Role ' + str(role) + ' was deleted')
        await self.log(message)

    async def on_guild_role_update(self, before, after):
        message = ('Role ' + str(before) + ' was updated')
        await self.log(message)

    async def on_voice_state_update(self, member, before, after):
        if before.channel is None:
            await self.log(str(member) + ' has joined ' + after.channel.name)
        elif after.channel is None:
            await self.log(str(member) + ' has left ' + before.channel.name)
        elif before.channel.name != after.channel.name:
            await self.log(str(member) + ' has changed channel from "' + before.channel.name + '" to "' + after.channel.name + '"')

        if before.deaf != after.deaf:
            if (after.deaf):
                await self.log(str(member) + ' was deafened by the guild')
            else:
                await self.log(str(member) + ' was undeafened by the guild')
        if before.mute != after.mute:
            if (after.mute):
                await self.log(str(member) + ' was muted by the guild')
            else:
                await self.log(str(member) + ' was unmuted by the guild')
        if before.self_mute != after.self_mute:
            if (after.self_mute):
                await self.log(str(member) + ' has muted themself')
            else:
                await self.log(str(member) + ' has unmuted themself')
        if before.self_deaf != after.self_deaf:
            if (after.self_deaf):
                await self.log(str(member) + ' has deafened themself')
            else:
                await self.log(str(member) + ' has undeafened themself')
        if before.afk != after.afk:
            if (after.afk):
                await self.log(str(member) + ' went AFK')
            else:
                await self.log(str(member) + ' came back from AFK')

    async def on_member_ban(self, guild, user):
        message = ('Server ' + str(guild) + 'has banned ' + str(user))
        await self.log(message)

    async def on_member_unban(self, guild, user):
        message = ('Server ' + str(guild) + 'has unbanned ' + str(user))
        await self.log(message)

    async def on_group_join(self, channel, user):
        message = (str(user) + ' joined ' + str(channel))
        await self.log(message)

    async def on_group_remove(self, channel, user):
        message = (str(user) + ' left ' + str(channel))
        await self.log(message)

client = MyClient()
client.run('NTg2MTE3Mjg3MTQwOTE3MjYw.XPjW_Q.83TbJxOH_E9z6CEXmCxu7y8b-xk')
