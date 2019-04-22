# Fortune-finding extension for pibot
### PREAMBLE ##################################################################
import discord

from discord.ext import commands
import selenium.webdriver
import selenium.common.exceptions


class waifu(commands.Cog):
    """Fortune generating related commands"""

    def __init__(self, bot):
        self.bot = bot

    async def get_fortune(self, author_id, author_roles):
        """Grab today's fortune for the given user"""

    @commands.command(aliases=['OwO'], pass_context=True)
    async def waifu(self, ctx):
        driver = selenium.webdriver.Firefox()
        try:
            driver.get(url="https://www.thiswaifudoesnotexist.net")
        except selenium.common.exceptions.WebDriverException as connect_err:
            await ctx.channel.say("Unable to generate a waifu right now OwO")
            return
        image_xpath = "/html/body/div[1]/div/div[1]/img"
        image_url = driver.find_element_by_xpath(image_xpath).get_attribute("src")
        snippet_xpath = """//*[@id="snippet-container"]"""
        snippet_text = driver.find_element_by_xpath(snippet_xpath).text
        driver.close()
        e = discord.Embed(
            description="{}, your waifu \n{}".format(ctx.message.author.mention, snippet_text))
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
