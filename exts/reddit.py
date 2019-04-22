# Reddit browser
# PREAMBLE ####################################################################
import asyncio
import html

import discord
import html2text
import requests

from discord.ext import commands
from .utils import scrollable

class Reddit(commands.Cog):
    """Reddit-related commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, aliases=["leddit"])
    async def reddit(self, ctx):
        """Grabs the top post from a particular subreddit"""
        sub = "netrunner"
        msg = ctx.message.content
        msg = msg.lower().split()
        if len(msg) > 1:
            sub = msg[1].lower()

        # Grab the correct json file
        url = "https://www.reddit.com/r/" + sub + ".json"
        pages = requests.get(url, headers={'User-agent': 'Draco v0.1'}).json()
        potential_responses = []
        if "data" in pages and "children" in pages["data"]:
            for post in pages["data"]["children"]:
                crafted_response = ""
                to_add = ["title", "url", "selftext_html"]
                for search_term in to_add:
                    if search_term in post["data"]:
                        if post["data"][search_term] is None:
                            continue
                        unescaped = html.unescape(post["data"][search_term])
                        crafted_response += html2text.html2text(unescaped) + "\n"
                if len(crafted_response) > 0:
                    potential_responses.append(crafted_response)
        if len(potential_responses) > 0:
            response = scrollable.Scrollable(self.bot)
            await response.send(ctx.message.channel, potential_responses, 0)
        else:
            await self.bot.say("Error in grabbing " + url + " boss.")

def setup(bot):
    bot.add_cog(Reddit(bot))
