import importlib
from discord.ext import commands

class Cogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reload_cogs()

    async def reload(self, ctx=None):
        if ctx is not None:
            await ctx.send("Reloading plugins")
        self.reload_cogs()

    def reload_cogs(self):
        self.unload('Ping')
        from .ping import Ping
        self.bot.add_cog(Ping())

        self.unload('Die')
        from .die import Die
        self.bot.add_cog(Die(self.bot))

        self.unload('Log')
        from .log import Log
        self.bot.add_cog(Log(self.bot))

        self.unload('Voice')
        from .voice import Voice
        self.bot.add_cog(Voice(self.bot))

        self.unload('Auto')
        from .auto import Auto
        self.bot.add_cog(Auto(self.bot))

        self.unload('Grip')
        from .grip import Grip
        self.bot.add_cog(Grip(self.bot))

        self.unload('Prihlasky')
        from .prihlasky import Prihlasky
        self.bot.add_cog(Prihlasky(self.bot))

        self.unload('Dadgar')
        from .dadgar import Dadgar
        self.bot.add_cog(Dadgar(self.bot))

    def unload(self, name):
        if (name in self.bot.cogs):
            self.bot.remove_cog(name)
