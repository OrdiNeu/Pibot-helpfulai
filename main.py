# Launch script for the Helpful AI running on OrdiNeu's RaspberryPi
### PREAMBLE ##################################################################
import asyncio
import random
import time

import discord
from discord.ext import commands
import requests

### CONSTANTS #################################################################
COMMAND_PREFIX = ['?', '!']
DISCRIPTION = 'OrdiNeu\'s Discord bot for the Netrunner channel'
HELP_ATTRS = {'hidden'=True}
EXTENSIONS = []
	
bot = commands.Bot(
	command_prefix=COMMAND_PREFIX, 
	description=description, 
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
		
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.display_name)
    print(client.user.id)
    print('------')
    if not hasattr(bot, 'uptime'):
        bot.uptime = datetime.datetime.utcnow()

@client.event
async def on_message(msg):
	# Ignore messages from bots
    if msg.author.bot:
		return
	await bot.process_commands(message)

### LOGIN AND RUN #############################################################
def load_credentials():
    with open('../pibot-discord-cred.json') as f:
        return json.load(f)

# Login and run
if __name__ == '__main__':
    credentials = load_credentials()
	token = credentials['token']

    bot.client_id = credentials['client_id']
    bot.bots_key = credentials['bots_key']
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

    bot.run(token)