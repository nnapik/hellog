import importlib
from discord.ext import commands

class Cogs(commands.Cog):
    def __init__(self, bot):
        bot.logger.info("Initializing cog Cogs")
        self.bot = bot
        bot.logger.info("Cogs cog initialized")

    async def reload(self, ctx=None):
        if ctx is not None:
            await ctx.send("Reloading plugins")
        self.reload_cogs()

    async def reload_cogs(self):
        await self.unload('Ping')
        from .ping import Ping
        await self.bot.add_cog(Ping())

        await self.unload('Die')
        from .die import Die
        await self.bot.add_cog(Die(self.bot))

        await self.unload('Log')
        from .log import Log
        await self.bot.add_cog(Log(self.bot))

        await self.unload('Voice')
        from .voice import Voice
        await self.bot.add_cog(Voice(self.bot))

        await self.unload('Auto')
        from .auto import Auto
        await self.bot.add_cog(Auto(self.bot))

        await self.unload('Grip')
        from .grip import Grip
        await self.bot.add_cog(Grip(self.bot))

        await self.unload('Prihlasky')
        from .prihlasky import Prihlasky
        await self.bot.add_cog(Prihlasky(self.bot))

        await self.unload('Dadgar')
        from .dadgar import Dadgar
        await self.bot.add_cog(Dadgar(self.bot))

        await self.unload('Download')
        from .download import Download
        await self.bot.add_cog(Download(self.bot))

    async def unload(self, name):
        if (name in self.bot.cogs):
            await self.bot.remove_cog(name)
