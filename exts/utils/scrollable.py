# Creates a comment that can scroll through a list, controllable via buttons
# PREAMBLE ####################################################################
import discord
import asyncio
import random

from discord.ext import commands
from . import listener

class Scrollable(listener.RctListener):
    """Creates a comment that can scroll through a list, controllable via buttons"""
    def __init__(self, bot):
        # Create the message
        self.bot = bot
        self.msg_list = None
        self.cur_pos = 0
        self.msg = None
        self.locked_to = None
        super().__init__(None)    # TODO: I screwed up somewhere with designing this

    async def send(self, channel, msg_list, cur_pos=0, locked_to=None):
        """Send the given message list, scrolled to the given position
        cur_pos lets you configure where in the list you start at
        locked_to lets you lock the controls to a particular user"""
        self.msg = await self.bot.send_message(channel, msg_list[cur_pos])
        await self.bot.add_reaction(self.msg, u"\u2B06")  # Up arrow
        await self.bot.add_reaction(self.msg, u"\u2B07")  # Down arrow
        await self.bot.add_reaction(self.msg, u"\U0001F3B2")  # Game die
        if locked_to:
            await self.bot.add_reaction(self.msg, u"\U0001F512")  # Padlock

        self.msg_list = msg_list
        self.cur_pos = cur_pos
        self.attach(channel.id)
        self.locked_to = locked_to

    async def on_reaction(self, rct, user, added):
        """Handle the scroll reaction"""
        if self.locked_to and self.locked_to != user:
            return
        if str(rct.emoji) == u"\u2B06":    # Up arrow
            # Move position safely, and remove this reaction
            self.cur_pos += 1
            if self.cur_pos >= len(self.msg_list):
                self.cur_pos = 0
            if added:
                self.bot.remove_reaction(self.msg, rct.emoji, user)
        elif str(rct.emoji) == u"\u2B07":   # Down arrow
            self.cur_pos -= 1
            if self.cur_pos < 0:
                self.cur_pos = len(self.msg_list)-1
            if added:
                self.bot.remove_reaction(self.msg, rct.emoji, user)
        elif str(rct.emoji) == u"\U0001F3B2":  # Game die
            self.cur_pos = random.randint(0, len(self.msg_list)-1)
            if added:
                self.bot.remove_reaction(self.msg, rct.emoji, user)
        await self.bot.edit_message(self.msg, self.msg_list[self.cur_pos])
