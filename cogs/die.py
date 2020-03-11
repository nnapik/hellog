from discord.ext import commands
class Die(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def die(self, ctx):
        await ctx.send("dying as requested")
        await self.bot.close()
