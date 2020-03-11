from discord.ext import commands
class Ping(commands.Cog):
    def __init__(self):
        pass

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong " + ctx.author.mention)
