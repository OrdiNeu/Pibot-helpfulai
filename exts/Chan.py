# Shamelessly stolen from Rapptz's RoboDanny github because it's useful
# PREAMBLE ####################################################################
import asyncio
import os
import re
import sys

import discord
import inspect
import requests

# to expose to the eval command
import datetime

from collections import Counter
from discord.ext import commands
from .utils import checks

class Chan:
    """Grabs a link to various chan threads"""
    def __init__(self, bot):
        self.bot = bot

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
            await send_message(msg.channel, response)
        else:
            await send_message(msg.channel, "No thread found.")

def setup(bot):
    bot.add_cog(Chan(bot))