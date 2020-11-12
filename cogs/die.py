from discord.ext import commands
class Die(commands.Cog):
    def __init__(self, bot):
        bot.logger.info("die cog initializing")
        self.bot = bot
        bot.logger.info("die cog initialized")

    @commands.command()
    async def die(self, ctx):
        await ctx.send("dying as requested")
        await self.bot.close()
