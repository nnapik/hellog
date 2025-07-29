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

    @commands.command(name='khadgar', aliases=['dadgar', 'khadgar,', 'dadgar,', 'hellbot', 'hellbot,'])
    async def khadgar(self, ctx, **attrs):
        await ctx.send(ctx.author.mention + ': ' + random.choice(self.lines))

    @commands.command(name='roll')
    async def roll(self, ctx, *attrs):
        if len(attrs) != 1:
            ctx.send('invalid parameters, expecting 1 positive integer')
            return
        try:
            num = int(attrs[0], 10)
            if num < 0:
                await ctx.send('invalid parameters, expecting 1 positive integer')
                return
            rnum = random.randint(1, num)
            await ctx.send(f'{ctx.author.mention} rolls {rnum} (1-{num})')
        except ValueError:
            await ctx.send('invalid parameters, expecting 1 positive integer')
            return
