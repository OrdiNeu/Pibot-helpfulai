# Shamelessly stolen from Rapptz's RoboDanny github because it's useful
# PREAMBLE ####################################################################
import os
import sys

import discord
import inspect

# to expose to the eval command
import datetime

from collections import Counter
from discord.ext import commands
from .utils import checks

# Exit code to let the force reloader know to reload from git
GIT_RELOAD_EXIT_CODE = 5

# File to store the channel id scavenge was called from
SCAVENGE_FILE_NAME = 'scavenge_channel.txt'

class Admin:
    """Admin-only commands that make the bot dynamic."""

    def __init__(self, bot):
        self.bot = bot
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.scavenge_check())
        loop.close()
    
    async def scavenge_check(self):
        # Check for the existance of the scavenge file
        if os.path.isfile(SCAVENGE_FILE_NAME):
            with open(SCAVENGE_FILE_NAME, 'r') as f:
                channel_id = self.bot.get_channel(f.read())
                await bot.send_message(channel_id, "Back")
            os.remove(SCAVENGE_FILE_NAME)

    @commands.command(hidden=True)
    @checks.is_admin()
    async def load(self, *, module: str):
        """Loads a module."""
        try:
            self.bot.load_extension(module)
        except Exception as e:
            await self.bot.say('\N{PISTOL}')
            await self.bot.say('{}: {}'.format(type(e).__name__, e))
        else:
            await self.bot.say('\N{OK HAND SIGN}')

    @commands.command(hidden=True)
    @checks.is_admin()
    async def unload(self, *, module: str):
        """Unloads a module."""
        try:
            self.bot.unload_extension(module)
        except Exception as e:
            await self.bot.say('\N{PISTOL}')
            await self.bot.say('{}: {}'.format(type(e).__name__, e))
        else:
            await self.bot.say('\N{OK HAND SIGN}')

    @commands.command(name='reload', hidden=True)
    @checks.is_admin()
    async def _reload(self, *, module: str):
        """Reloads a module."""
        try:
            self.bot.unload_extension(module)
            self.bot.load_extension(module)
        except Exception as e:
            await self.bot.say('\N{PISTOL}')
            await self.bot.say('{}: {}'.format(type(e).__name__, e))
        else:
            await self.bot.say('\N{OK HAND SIGN}')

    @commands.command(pass_context=True, hidden=True)
    @checks.is_admin()
    async def debug(self, ctx, *, code: str):
        """Evaluates code."""
        code = code.strip('` ')
        python = '```py\n{}\n```'
        result = None

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'message': ctx.message,
            'server': ctx.message.server,
            'channel': ctx.message.channel,
            'author': ctx.message.author
        }

        env.update(globals())

        try:
            result = eval(code, env)
            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            await self.bot.say(python.format(type(e).__name__ + ': ' + str(e)))
            return

        await self.bot.say(python.format(result))

    @commands.command(hidden=True, pass_context=True)
    @checks.is_admin()
    async def scavenge(self, ctx):
        """Restarts the bot, and tries to pull the latest version of itself from git"""
        await self.bot.say('brb')
        with open(SCAVENGE_FILE_NAME, 'w') as f
            f.write(ctx.message.channel.id)
        sys.exit(GIT_RELOAD_EXIT_CODE)  # Expect our helper script to do the git reloading

    @commands.command(hidden=True)
    @checks.is_admin()
    async def locate(self):
        """Grabs the local and global IP of the bot"""
        globalip = os.popen("dig +short myip.opendns.com @resolver1.opendns.com").read()
        localip = os.popen("ifconfig | grep -oP \"inet addr:192.168.\\\\d+.\\\\d+\"").read()
        await self.bot.say("Global IP: {}\nLocal IP: {}".format(globalip, localip))

    @commands.command(pass_context=True, hidden=True, aliases=['screenshot', 'wiretap'])
    @checks.is_admin()
    async def sc(self, ctx):
        """Take a screenshot and send it back"""
        os.system("import -window root screenshot.png")
        await self.bot.send_file(ctx.message.channel, "screenshot.png")

    @commands.command(pass_context=True, hidden=True)
    async def test_error(self, ctx):
        print("Test error")
        a = {}
        print(a['1'])

def setup(bot):
    bot.add_cog(Admin(bot))
