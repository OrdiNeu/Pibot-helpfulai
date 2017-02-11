# Netrunner extension for pibot
### PREAMBLE ##################################################################
import re
from unidecode import unidecode

import discord
import requests
import random

from discord.ext import commands


class Fortune:
    """Frtune generating related commands"""

    def __init__(self, bot):
        self.bot = bot
        self.fortuned_users = {}

    @staticmethod
    def check_fortune(val, minum, maxum):
        if val in range(minum, maxum):
            return True
        else:
            return False

    @commands.command(pass_context = True)
    async def fortune(self, ctx):
        """Grabs your fortune for the day!"""
        author_id = ctx.message.author.id
        if not author_id in self.fortuned_users.keys():
            self.fortuned_users[author_id] = random.randrange(0, 100)
        fort = self.fortuned_users[author_id]
        fortune = {
            self.check_fortune(fort, 0,  5): "Wurst! Your luck is terrible",
            self.check_fortune(fort, 6,  15): "Awful! hopefully it won't be too bad",
            self.check_fortune(fort, 16, 35): "Bad!, stay at hope and have some tea",
            self.check_fortune(fort, 36, 50): "Not too bad, but better stay home to be safe",
            self.check_fortune(fort, 51, 65): "Things could be better",
            self.check_fortune(fort, 66, 85): "Things are looking up, spend time with friends to make it even better",
            self.check_fortune(fort, 86, 95): "Great! Nothing could go wrong for you today",
            self.check_fortune(fort, 96, 100): "Perfect! Confess your love, Nothing could go wrong!"
        }
        await self.bot.say(fortune[True])


def setup(bot):
    bot.add_cog(Fortune(bot))
