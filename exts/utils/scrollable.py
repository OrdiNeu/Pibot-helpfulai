# Creates a comment that can scroll through a list, controllable via buttons
# PREAMBLE ####################################################################
import discord
import asyncio

from discord.ext import commands
from . import listener

class Scrollable(listener.RctListener):
    """Creates a comment that can scroll through a list, controllable via buttons"""
    def __init__(self, bot):
        # Create the message
        self.bot = bot
        self.msg_list = None
        self.cur_pos = 0
        self.msg = None # TODO: aghh pylint stop it
        super().__init__(None)    # TODO: I screwed up somewhere with designing this

    async def send(self, channel, msg_list, cur_pos=0):
        """Send the given message list, scrolled to the given position"""
        self.msg = await self.bot.send_message(channel, msg_list[cur_pos])
        await self.bot.add_reaction(self.msg, u"\u2B06") # Up arrow
        await self.bot.add_reaction(self.msg, u"\u2B07") # Down arrow
        self.msg_list = msg_list
        self.cur_pos = cur_pos
        self.attach(channel.id)

    async def on_reaction(self, rct, user, added):
        """Handle the scroll reaction"""
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
        print("reaction: " + str(rct.emoji))   # Debugging code
        await self.bot.edit_message(self.msg, self.msg_list[self.cur_pos])
