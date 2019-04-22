# Fortune-finding extension for pibot
### PREAMBLE ##################################################################
import random
import requests

import discord

from discord.ext import commands



class waifu(commands.Cog):
    """Fortune generating related commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['OwO'], pass_context=True)
    async def waifu(self, ctx):
        # Obtain a random image and summary text
        totalImages = 100000
        totalTexts = totalImages
        image_url = "https://www.thiswaifudoesnotexist.net/example-{}.jpg".format(random.randint(0, totalImages))
        snippet_url = "https://www.thiswaifudoesnotexist.net/snippet-{}.txt".format(random.randint(0, totalTexts))

        # Read the summary text
        snippet = requests.get(text_url).text
        snippet = snippet.encode('latin-1').decode('utf-8')  # Ungarble the text

        # Formulate the response
        e = discord.Embed(
            description="{}, your waifu is: \n{}".format(ctx.message.author.mention, snippet_text))
        e.set_thumbnail(url=image_url)
        await ctx.channel.say(embed=e)


def setup(bot):
    bot.add_cog(waifu(bot))


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
