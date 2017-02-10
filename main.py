# Launch script for the Helpful AI running on OrdiNeu's RaspberryPi
### PREAMBLE ##################################################################
import asyncio
import datetime
import os
import random
import sys
import time
import traceback

import discord
from discord.ext import commands
import json
import requests

### CONSTANTS #################################################################
COMMAND_PREFIX = ['?', '!']
DESCRIPTION = 'OrdiNeu\'s Discord bot for the Netrunner channel.'
HELP_ATTRS = {'hidden': True}
EXTENSIONS = [
    'exts.admin',
    'exts.Netrunner',
    'exts.Arkham',
    'exts.LOTR',
    'exts.SkullsNRoses',
    'exts.Fortune'
]

bot = commands.Bot(
    command_prefix=COMMAND_PREFIX,
    description=DESCRIPTION,
    pm_help=None,
    help_attrs=HELP_ATTRS
)

RESTART_EXIT_CODE = 4
ERR_EXIT_CODE = 1


### DISCORD CLIENT EVENT HANDLERS #############################################
@bot.event
async def on_command_error(error, ctx):
    author = ctx.message.author
    if isinstance(error, commands.NoPrivateMessage):
        await bot.send_message(author, 'This command cannot be used in private messages.')
    elif isinstance(error, commands.DisabledCommand):
        await bot.send_message(author, 'Sorry. This command is disabled and cannot be used.')
    elif isinstance(error, commands.CommandInvokeError):
        await bot.send_message(author, 'In {0.command.qualified_name}:'.format(ctx), file=sys.stderr)
        tb_msg = "\n".join(traceback.extract_tb(error.original.__traceback__))
        await bot.send_message(author, tb_msg)
        await bot.send_message(author, '{0.__class__.__name__}: {0}'.format(error.original), file=sys.stderr)


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
        print("(PM) : " + msg.author.name + ": " + msg.content)

    # lowercase the first word of the command (if it starts with the prefix)
    if msg.content.startswith(tuple(COMMAND_PREFIX)):
        text = msg.content
        command_breakpoint = text.find(" ")
        if command_breakpoint > 0:  # I.e. there was a space
            msg.content = text[0:command_breakpoint].lower() + text[command_breakpoint:]
    await bot.process_commands(msg)


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
    try:
        bot.run(token)
    except ConnectionResetError:
        # Likely kicked out for inactivity: tell shell script to restart everything
        # (Since discord.py doesn't really like rerunning bot.run)
        sys.exit(RESTART_EXIT_CODE)
    except Exception as e:
        print('Error {}: {}'.format(type(e).__name__, e))
        sys.exit(ERR_EXIT_CODE)
