# Shamelessly stolen from Rapptz's RoboDanny github because it's useful
# PREAMBLE ####################################################################
import discord
import inspect

# to expose to the eval command
import datetime

from collections import Counter
from discord.ext import commands
from .utils import checks

class Admin:
	"""Admin-only commands that make the bot dynamic."""

	def __init__(self, bot):
		self.bot = bot

	@commands.command(hidden=True)
	@checks.is_admin()
	async def load(self, *, module : str):
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
	async def unload(self, *, module : str):
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
	async def _reload(self, *, module : str):
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
	async def debug(self, ctx, *, code : str):
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
	
	@commands.command(hidden=True)
	@checks.is_admin()
	async def scavenge():
		"""Restarts the bot, and tries to pull the latest version of itself from git"""
		await bot.say('brb')
		sys.exit(GIT_RELOAD_EXIT_CODE)	# Expect our helper script to do the git reloading
	
	@commands.command(hidden=True)
	@checks.is_admin()
	async def locate():
		"""Grabs the local and global IP of the bot"""
		globalip = os.popen("dig +short myip.opendns.com @resolver1.opendns.com").read()
		localip = os.popen("ifconfig | grep -oP \"inet addr:192.168.\\\\d+.\\\\d+\"").read()
		await bot.say("Global IP: {}\nLocal IP: {}".format(globalip, localip))

def setup(bot):
	bot.add_cog(Admin(bot))