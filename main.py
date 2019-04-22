# Launch script for the Helpful AI running on OrdiNeu's RaspberryPi
# PREAMBLE ####################################################################
import datetime
import os
import sys
import traceback
import re

import discord
import json
from discord.ext import commands

import exts.utils.listener
import exts.utils.twitter
import exts.utils.youtube
import exts.utils.alarm

# CONSTANTS ###################################################################
COMMAND_PREFIX = ['?', '!']
COMMAND_REGEX = re.compile('((^[!?]\w*)(.*))|(\s([!?]\w*)(.*))')
DESCRIPTION = 'OrdiNeu\'s Discord bot for the Netrunner channel.'
HELP_ATTRS = {'hidden': True}
EXTENSIONS = [
    'exts.admin',
    'exts.Netrunner',
    'exts.Arkham',
    'exts.LOTR',
    'exts.Fortune',
    'exts.Chan',
    'exts.reddit',
    'exts.LFR',
    'exts.Uncategorised',
    "exts.waifu"
]

bot = commands.Bot(
    command_prefix=COMMAND_PREFIX,
    description=DESCRIPTION,
    pm_help=None,
    help_attrs=HELP_ATTRS
)

RESTART_EXIT_CODE = 4
ERR_EXIT_CODE = 1

# File to store the channel id scavenge was called from
SCAVENGE_FILE_NAME = 'scavenge_channel.txt'


# DISCORD CLIENT EVENT HANDLERS ###############################################
@bot.event
async def on_command_error(ctx, error):
    channel = ctx.message.channel
    if isinstance(error, commands.NoPrivateMessage):
        await channel.send(
            'This command cannot be used in private messages.'
            )
    elif isinstance(error, commands.DisabledCommand):
        await channel.send(
            'Sorry. This command is disabled and cannot be used.'
            )
    elif isinstance(error, commands.CommandInvokeError):
        msg = '```\n'
        msg += 'In {0.command.qualified_name}:'.format(ctx)
        # Traceback is acting strangely...
        tb_msg = traceback.format_tb(error.original.__traceback__)
        if isinstance(tb_msg, list):
            msg += " ".join(tb_msg)
        else:
            msg += tb_msg
        msg += '{0.__class__.__name__}: {0}'.format(error.original)
        msg += '\n```'
        await channel.send(msg)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.display_name)
    print(bot.user.id)
    print('------')
    # If we're debugging the main script we can exit now with successful
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        sys.exit(0)
    if not hasattr(bot, 'uptime'):
        bot.uptime = datetime.datetime.utcnow()
    # Check for the existance of the scavenge file
    if os.path.isfile(SCAVENGE_FILE_NAME):
        with open(SCAVENGE_FILE_NAME, 'r') as f:
            channel = bot.get_channel(f.read())
            await channel.send_message("... and ichor...")
        os.remove(SCAVENGE_FILE_NAME)
        status_msg = ""

        # Also get the status of our extensions
        for extension in EXTENSIONS:
            try:
                status_msg += extension + ": "
                bot.unload_extension(extension)
                bot.load_extension(extension)
            except Exception as e:
                status_msg += '\N{PISTOL}'
                status_msg += '{}: {}'.format(type(e).__name__, e)
            else:
                status_msg += '\N{OK HAND SIGN}'
            status_msg += "\n"
        await bot.send_message(channel_id, status_msg)

async def on_reaction(reaction, user, added):
    # Ignore reactions from bots
    if user.bot:
        return

    # Do we have a listener for this?
    if reaction.message.channel:
        channel = reaction.message.channel
        if channel.id in exts.utils.listener.reaction_listeners:
            for listener in exts.utils.listener.reaction_listeners[channel.id]:
                await listener._check_and_act(reaction, user, added)


@bot.event
async def on_reaction_add(reaction, user):
    await on_reaction(reaction, user, True)


@bot.event
async def on_reaction_remove(reaction, user):
    await on_reaction(reaction, user, False)


@bot.event
async def on_message(msg):
    # Ignore messages from bots
    if msg.author.bot:
        return

    # Log the message
    if not isinstance(msg.channel, discord.DMChannel):
        print(
            "<" + msg.channel.name + "> " + msg.author.name + ": "
            + msg.content)
    else:
        print("(PM) : " + msg.author.name + ": " + msg.content)

    # use our previously compiled regex search on the message
    re_search = COMMAND_REGEX.search(msg.content)
    # if the search matches, we'll parse out the command part
    if re_search is not None:
        # if the first group is not None, it's the classic start of string section
        if re_search.group(1) is not None:
            msg.content = re_search.group(2).lower() + re_search.group(3)
        # else it's specified later in the string, remove the prefix that's not a command, and continue
        elif re_search.group(4) is not None:
            msg.content = re_search.group(5).lower() + re_search.group(6)
    # lowercase the first word of the command (if it starts with the prefix)
    # if msg.content.startswith(tuple(COMMAND_PREFIX)):
    #    text = msg.content
    #    prefix_end = text.find(" ")
    #    if prefix_end > 0:  # I.e. there was a space
    #        msg.content = text[0:prefix_end].lower() + text[prefix_end:]
    #    else:
    #        msg.content = text.lower()

    # Handle listeners, if any are set:
    if msg.channel:
        if msg.channel.id in exts.utils.listener.msg_listeners:
            for listener in exts.utils.listener.msg_listeners[msg.channel.id]:
                await listener.on_message(msg)

    await bot.process_commands(msg)


# LOGIN AND RUN ###############################################################
def load_credentials():
    with open('../pibot-discord-cred.json') as f:
        return json.load(f)


def load_twitter():
    with open('../pibot-twitter-cred.json') as f:
        creds = json.load(f)
        exts.utils.twitter.init(
            creds['consumer_key'],
            creds['consumer_secret'],
            creds['access_token'],
            creds['access_token_secret']
            )

# Login and run
if __name__ == '__main__':
    #load_twitter()
    #exts.utils.youtube.init("../pibot-google-secret.json")
    credentials = load_credentials()
    token = credentials['token']

    bot.client_id = credentials['client_id']
    bot.loop.create_task(exts.utils.alarm._check_alarm(bot))
    for extension in EXTENSIONS:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(
                'Failed to load extension {}\n{}: {}'.format(
                    extension,
                    type(e).__name__,
                    e)
                )
    try:
        bot.run(token)
    except ConnectionResetError:
        # Likely kicked out for inactivity: tell shell script to restart
        # (Since discord.py doesn't really like rerunning bot.run)
        sys.exit(RESTART_EXIT_CODE)
    except Exception as e:
        print('Error {}: {}'.format(type(e).__name__, e))
        sys.exit(ERR_EXIT_CODE)

    # It shouldn't get to this point, so just try to restart
    sys.exit(RESTART_EXIT_CODE)
