# Fortune-finding extension for pibot
### PREAMBLE ##################################################################
import re

import discord
import requests
from discord.ext import commands


class Fortune:
    """Fortune generating related commands"""

    def __init__(self, bot):
        self.bot = bot

    async def get_fortune(self, author_id, author_roles):
        """Grab today's fortune for the given user"""

    @commands.command(aliases=['OwO'], pass_context=True)
    async def waifu(self, ctx):
        try:
            waifu = requests.get(url="https://www.thiswaifudoesnotexist.net")
        except (requests.RequestException, requests.HTTPError, requests.ConnectionError) as connect_err:
            await self.bot.say("Unable to generate a waifu right now OwO")
            return
        image_regex = re.search("<img src=\"(https://www.thiswaifudoesnotexist.net/example-[0-9]*\.jpg)", waifu.content)
        snippet_regex = re.search("<div id=\"snippet-container\">(.*)</div>", waifu.content)
        e = discord.Embed(description="{}, your waifu is: \n{}".format(ctx.message.author.mention, snippet_regex))
        if image_regex is not None:
            e.set_image(url=image_regex.group(1))
        await self.bot.say(embed=e)


def setup(bot):
    bot.add_cog(Fortune(bot))


"""
fortune = {
    self.check_fortune(fort, 0, 5): "Wurst! Your luck is terrible",
    self.check_fortune(fort, 6, 15): "Awful! hopefully it won't be too bad",
    self.check_fortune(fort, 16, 35): "Bad!, stay at home and have some tea",
    self.check_fortune(fort, 36, 50): "Not too bad, but better stay home to be safe",
    self.check_fortune(fort, 51, 65): "Things could be better",
    self.check_fortune(fort, 66, 85): "Things are looking up, spend time with friends to make it even better",
    self.check_fortune(fort, 86, 95): "Great! Nothing could go wrong for you today",
    self.check_fortune(fort, 96, 100): "Perfect! Confess your love, Nothing could go wrong!"
}"""
