# Enables you to create listeners to capture all input
# PREAMBLE ####################################################################
import discord
import asyncio

from discord.ext import commands

# Keys: channel. Value: list of listeners
attached = {}

class Listener:
    def __init__(self):
        pass
    
    def attach(self, channel):
        global attached
        if channel in attached:
            attached.append(self)
        else:
            attached[channel] = [self]

    def detach(self, channel):
        global attached
        attached[channel].remove(self)

    # Overwrite this function for messages
    # Note that msg is of type discord.Message
    async def on_message(self, msg):
        pass