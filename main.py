# Launch script for the Helpful AI running on OrdiNeu's RaspberryPi
### PREAMBLE ##################################################################
import asyncio
import datetime
import random
import sys
import time
import traceback

import discord
from discord.ext import commands
import json
import requests

### CONSTANTS #################################################################
GIT_RELOAD_EXIT_CODE = 5
COMMAND_PREFIX = ['?', '!']
DESCRIPTION = 'OrdiNeu\'s Discord bot for the Netrunner channel.'
HELP_ATTRS = {'hidden': True}
EXTENSIONS = [
	'exts.Netrunner',
	'exts.Arkham',
	'exts.LOTR'
	]

bot = commands.Bot(
	command_prefix=COMMAND_PREFIX, 
	description=DESCRIPTION, 
	pm_help=None, 
	help_attrs=HELP_ATTRS
	)
	
### DISCORD CLIENT EVENT HANDLERS #############################################
@bot.event
async def on_command_error(error, ctx):
	if isinstance(error, commands.NoPrivateMessage):
		await bot.send_message(ctx.message.author, 'This command cannot be used in private messages.')
	elif isinstance(error, commands.DisabledCommand):
		await bot.send_message(ctx.message.author, 'Sorry. This command is disabled and cannot be used.')
	elif isinstance(error, commands.CommandInvokeError):
		print('In {0.command.qualified_name}:'.format(ctx), file=sys.stderr)
		traceback.print_tb(error.original.__traceback__)
		print('{0.__class__.__name__}: {0}'.format(error.original), file=sys.stderr)
		
@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.display_name)
	print(bot.user.id)
	print('------')
	# Login successful: if we're debugging the main script we can exit now with successful
	if len(sys.argv) > 1 and sys.argv[1] == 'debug':
		sys.exit(0)
	if not hasattr(bot, 'uptime'):
		bot.uptime = datetime.datetime.utcnow()

@bot.event
async def on_message(msg):
	# Ignore messages from bots
	if msg.author.bot:
		return

	# Log the message
	if msg.channel.name != None:
		print("<" + msg.channel.name + "> : " + msg.author.name + ": " + msg.content)
	else:
		print("(PM) : "  + msg.author.name + ": " + msg.content)
	await bot.process_commands(msg)

### BOT DEFAULT COMMAND #######################################################
@bot.command()
async def scavenge():
	"""Restarts the bot, and tries to pull the latest version of itself from git"""
	await bot.say('brb')
	sys.exit(GIT_RELOAD_EXIT_CODE)	# Expect our helper script to do the git reloading
	
### LOGIN AND RUN #############################################################
def load_credentials():
	with open('../pibot-discord-cred.json') as f:
		return json.load(f)

# Login and run
if __name__ == '__main__':
	credentials = load_credentials()
	token = credentials['token']

	bot.client_id = credentials['client_id']
	for extension in EXTENSIONS:
		try:
			bot.load_extension(extension)
		except Exception as e:
			print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

	bot.run(token)
