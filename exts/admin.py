# Shamelessly stolen from Rapptz's RoboDanny github because it's useful
# PREAMBLE ####################################################################
import asyncio
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


class Admin(commands.Cog):
    """Admin-only commands that make the bot dynamic."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @checks.is_admin()
    async def load(self, ctx, *, module: str):
        """Loads a module."""
        try:
            self.bot.load_extension(module)
        except Exception as e:
            await ctx.channel.send('\N{PISTOL}')
            await ctx.channel.send('{}: {}'.format(type(e).__name__, e))
        else:
            await ctx.channel.send('\N{OK HAND SIGN}')

    @commands.command(hidden=True)
    @checks.is_admin()
    async def unload(self, ctx, *, module: str):
        """Unloads a module."""
        try:
            self.bot.unload_extension(module)
        except Exception as e:
            await ctx.channel.send('\N{PISTOL}')
            await ctx.channel.send('{}: {}'.format(type(e).__name__, e))
        else:
            await ctx.channel.send('\N{OK HAND SIGN}')

    @commands.command(name='reload', hidden=True)
    @checks.is_admin()
    async def _reload(self, ctx, *, module: str):
        """Reloads a module."""
        try:
            self.bot.unload_extension(module)
            self.bot.load_extension(module)
        except Exception as e:
            await ctx.channel.send('\N{PISTOL}')
            await ctx.channel.send('{}: {}'.format(type(e).__name__, e))
        else:
            await ctx.channel.send('\N{OK HAND SIGN}')

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
            await ctx.channel.send(python.format(type(e).__name__ + ': ' + str(e)))
            return

        await ctx.channel.send(python.format(result))

    @commands.command(hidden=True, pass_context=True)
    @checks.is_admin()
    async def scavenge(self, ctx):
        """Restarts the bot, and tries to pull the latest version of itself from git"""
        await ctx.channel.send('Fire...')
        with open(SCAVENGE_FILE_NAME, 'w') as f:
            f.write(str(ctx.message.channel.id))
        sys.exit(GIT_RELOAD_EXIT_CODE)  # Expect our helper script to do the git reloading

    @commands.command(hidden=True, pass_context=True, aliases=['st'])
    @checks.is_admin()
    async def status(self, ctx):
        """Attempts to reload every module and tells us if the module loaded correctly"""
        status_msg = ""
        for extension in tuple(self.bot.extensions):
            try:
                status_msg += extension + ": "
                self.bot.unload_extension(extension)
                self.bot.load_extension(extension)
            except Exception as e:
                status_msg += '\N{PISTOL}'
                status_msg += '{}: {}'.format(type(e).__name__, e)
            else:
                status_msg += '\N{OK HAND SIGN}'
            status_msg += "\n"
        await ctx.channel.send(status_msg)

    @commands.command(hidden=True)
    @checks.is_admin()
    async def locate(self, ctx):
        """Grabs the local and global IP of the bot"""
        globalip = os.popen("curl https://ipinfo.io/ip").read()
        localip = os.popen("ifconfig | grep -oP \"inet (addr:)?192.168.\\\\d+.\\\\d+\"").read()
        await ctx.channel.send("Global IP: {}\nLocal IP: {}".format(globalip, localip))

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

    @commands.command(pass_context=True, hidden=True)
    @checks.is_trusted()
    async def set_game(self, ctx):
        """Sets the "Wyrm is playing" message"""
        msg = ctx.message.content
        msg = msg.split()
        if len(msg) > 1:
            game_name = " ".join(msg[1:])
            print("DEBUG: changing game name to ", game_name)
            await self.bot.change_presence(game=discord.Game(name=game_name))
        else:
            await self.bot.change_presence()


async def setup(bot):
    await bot.add_cog(Admin(bot))
