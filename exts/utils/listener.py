# Enables you to create listeners to capture all input
# PREAMBLE ####################################################################
import discord
import asyncio

from discord.ext import commands

# Keys: channel. Value: list of listeners
msg_listeners = {}
reaction_listeners = {}

class Listener:
    """Abstract class for listeners"""
    def __init__(self):
        self.listener_list = {}

    def attach(self, channel):
        """Attach this listener to the given channel"""
        if channel in self.listener_list:
            self.listener_list[channel].append(self)
        else:
            self.listener_list[channel] = [self]

    def detach(self, channel):
        """Detach this listener from the given channel"""
        self.listener_list[channel].remove(self)

class MsgListener(Listener):
    """Virtual class for a listener that scans messages on a channel"""
    def __init__(self):
        super().__init__()
        self.listener_list = msg_listeners

    async def on_message(self, msg):
        """Virtual function, called whenever a message arrives at the attached channel
        Overwrite this function to use.
        Note that msg is of type discord.Message"""
        pass

class RctListener(Listener):
    """Virtual class for a listener that scans reactions on a message"""
    def __init__(self, msg):
        super().__init__()
        self.listener_list = reaction_listeners
        self.msg = msg

    async def _check_and_act(self, rct, user, added):
        """Used internally"""
        if rct.message.id == self.msg.id:
            await self.on_reaction(rct, user, added)

    async def on_reaction(self, rct, user, added):
        """Virtual function, called whenever a reaction is placed on the attached message
        Overwrite this function to use.
        Note that rct is of type discord.Reaction
        Added is True if a reaction was added, False otherwise"""
        pass
