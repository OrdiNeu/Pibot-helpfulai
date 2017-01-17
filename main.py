# Launchpad for the Helpful AI running on OrdiNeu's RaspberryPi

import asyncio
import random
import time

import discord
import requests

### CONSTANTS #################################################################
COMMAND_PREFIX = "!"

### PARSE TEXT COMMAND ########################################################
async def exec_command(client, msg):
    pass

### DISCORD CLIENT EVENT HANDLERS #############################################
@client.event
async def on_ready():
    print('Logged in as')
    print('Helpful AI') #original: client.user.name
    print(client.user.id)

@client.event
async def on_message(msg):
    global g_frequency
	
	# Ignore messages from ourself
    if msg.author.name == client.user.name:
		return

	# Capture commands
	if msg.content.startswith(COMMAND_PREFIX):
		msg.content = msg.content.lower()
		await exec_command(client, msg)

### LOGIN AND RUN #############################################################
# Login and run
client = discord.Client()
client.run('haas@mt2015.com', 'welovemush')