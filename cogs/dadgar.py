import random
from discord.ext import commands
class Dadgar(commands.Cog):
    def __init__(self, bot):
        bot.logger.info("Dadgar cog initializing")
        self.lines = []
        self.lines.append('Reply...hazy... Try again?')
        self.lines.append('Nooooo... yes, actually.')
        self.lines.append('Outlook is certain. Certain death!')
        self.lines.append('Outlook unclear, gather 4289 more apexis crystals and ask again.')
        self.lines.append('Let me confer with my sources... yes.')
        self.lines.append('Let me confer with my sources... no.')
        self.lines.append('You will likely survive. Most likely.')
        self.lines.append('Not likely... in this timeline.')
        self.lines.append('Your sound card works perfectly.')
        self.lines.append('Defeat is assured.')
        bot.logger.info("Dadgar cog initialized")

    @commands.command()
    async def khadgar(self, ctx):
        await ctx.send(ctx.author.mention + ': ' + random.choice(self.lines))

