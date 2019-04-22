# Shamelessly stolen from Rapptz's RoboDanny github because it's useful
# PREAMBLE ####################################################################
import asyncio
import os
import random
import re
import sys

import discord
import inspect
import requests

# to expose to the eval command
import datetime
import html2text

from collections import Counter
from discord.ext import commands
from .utils import checks, scrollable

class Chan(commands.Cog):
    """Grabs a link to various chan threads"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def randchan(self, ctx):
        """"Prints the OP for a random thread
            Accepts a board name (default is /x/)"""
        board = "x"
        msg = ctx.message.content
        msg = msg.lower().split()
        if len(msg) > 1:
            board = msg[1].lower()
        # Find the given general
        pages = requests.get("http://a.4cdn.org/" + board + "/catalog.json").json()
        potential_responses = []
        for p in pages:
            for t in p["threads"]:
                if "com" in t:
                    potential_responses.append(html2text.html2text(t["com"]))
        if len(potential_responses) > 0:
            random_pos = random.randint(0, len(potential_responses)-1)
            response = scrollable.Scrollable(self.bot)
            await response.send(ctx.message.channel, potential_responses, random_pos)
        else:
            await self.bot.say("Can't find that board, boss.")

    @commands.command()
    async def chan(self, *, msg: str):
        """Finds a thread"""
        # Determine board/thread title
        keywords = msg.lower().split()
        board = "tg"
        message = keywords
        if len(keywords) > 1:
            message = keywords[1:]
            board = keywords[0]
            board = re.sub("/^\/?(.+)\/?$", "\\1", board)
        else:
            common_threads = {
                "elona": "jp",
                "agdg": "vg",
                "rlg": "vg"
            }
            if message[0] in common_threads:
                board = common_threads[message[0]]

        # Find the given general
        pages = requests.get("http://a.4cdn.org/" + board + "/catalog.json").json()
        response = ""
        for p in pages:
            for t in p["threads"]:
                if "sub" in t:
                    # Current alg: make sure every word appears in the general
                    matches = 0
                    for word in message:
                        if word in t["sub"].lower():
                            matches += 1
                    if matches == len(message):
                        response += "http://boards.4chan.org/" + board + "/thread/" + str(t["no"]) + "\n"
        if response != "":
            await self.bot.say(response)
        else:
            await self.bot.say("No thread found.")

def setup(bot):
    bot.add_cog(Chan(bot))