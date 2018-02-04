# Fortune-finding extension for pibot
### PREAMBLE ##################################################################
import datetime
import re
from unidecode import unidecode

import discord
from discord.ext import commands
import requests
import random

class Fortune:
    """Fortune generating related commands"""

    def __init__(self, bot):
        self.bot = bot
        self.fortuned_users = {}
        self.last_check = datetime.date.today().day
        self.banned_roles = ["the tree of woe", "the cubes", "the tesseract"]

    @staticmethod
    def check_fortune(val, minum, maxum):
        if val in range(minum, maxum):
            return True
        else:
            return False

    async def get_fortune(self, author_id, author_roles):
        """Grab today's fortune for the given user"""
        for role in author_roles:
            if role in self.banned_roles:
                await self.bot.say(":classical_building:")
        # Refresh the fortunes if the day changes
        if datetime.date.today().day != self.last_check:
            self.fortuned_users = {}
            self.last_check = datetime.date.today().day
        # Assign this user a fortune if they don't have one yet
        if author_id not in self.fortuned_users.keys():
            # set the seed to the author id + the day of the month + day of the year
            random.seed(int(author_id) + datetime.date.today().day +
                        datetime.date.today().month + datetime.date.today().year)
            rand_val = random.randrange(0, 100)
            if self.last_check == 13:
                rand_val = int(rand_val / 2)
            for role in author_roles:
                if role.name.lower().strip() in self.banned_roles:
                    # await self.bot.say(":classical_building:")
                    rand_val = int((rand_val * 2) / 3)
            self.fortuned_users[author_id] = rand_val
        return self.fortuned_users[author_id]

    @commands.command(aliases=['fortuna', 'bib'], pass_context=True)
    async def fortune(self, ctx):
        """Grabs your fortune for the day!"""
        fort = await self.get_fortune(ctx.message.author.id, ctx.message.author.roles)
        fortune = {
            self.check_fortune(fort, 99, 100): {
                "text": "**PERFECT!**\nGo confess your love! Go ace that test! Today is your day!\nＹＡＨ♪☆0(＾＾0)＾＾(0＾＾)0☆♪ＹＡＨ",
                "colour": "0000FF",
                "img": "http://pre07.deviantart.net/dbbd/th/pre/f/2012/088/8/1/8163929b0b4b6b6b50835471c6a293b0-d4ubdtl.jpg"
            },
            self.check_fortune(fort, 95, 99): {
                "text": "**Amazing!**\nGo out and have fun! Nothing can go wrong today!\nルンルン♪~♪ d(⌒o⌒)b ♪~♪ルンルン",
                "colour": "0080FF",
                "img": "https://mightyjabba.files.wordpress.com/2010/12/bib_fortuna_mug1.jpg?w=600"
            },
            self.check_fortune(fort, 87, 95): {
                "text": "**Excellent!**\nMake the best of the day, it'll be wonderful!\no(＾∇＾)oﾜｰｲ♪",
                "colour": "00FFFF",
                "img": "http://vignette2.wikia.nocookie.net/starwars/images/8/8d/Bib_Fortuna_-_SWGTCG.jpg/revision/latest?cb=20090820151047"
            },
            self.check_fortune(fort, 73, 87): {
                "text": "**Great!**\nDo something difficult! You'll be successful!\n(v^ー°) ヤッタネ",
                "colour": "00FF00",
                "img": "http://img.lum.dolimg.com/v1/images/databank_bibfortuna_01_169_01aef5b7.jpeg?region=0%2C0%2C1560%2C878&width=768"
            },
            self.check_fortune(fort, 50, 73): {
                "text": "**Good!**\nSpend some time with your friends to make it even better!\n(*^-ﾟ)vｨｪｨ♪ ",
                "colour": "80FF00",
                "img": "http://vignette2.wikia.nocookie.net/starwars/images/3/33/BibFortunaHS-ROTJ.png/revision/latest?cb=20130326042806"
            },
            self.check_fortune(fort, 27, 50): {
                "text": "**Bad!**\nI hope it's not too bad. You'll make it through just fine!\n（´ノω・。）",
                "colour": "FFFF00",
                "img": "http://vignette3.wikia.nocookie.net/jedipedia/images/a/ac/Bib_fortuna.jpg/revision/latest?cb=20130504080306&path-prefix=de"
            },
            self.check_fortune(fort, 13, 27): {
                "text": "**Awful!**\nPlease don't do anything dangerous today! You could get hurt!\nｪﾝ（ｐ´；ω；`ｑ）ｪﾝ",
                "colour": "FF8000",
                "img": "https://s-media-cache-ak0.pinimg.com/236x/18/46/28/184628eb0b478b2b908e2763f5bf888c.jpg"
            },
            self.check_fortune(fort, 5, 13): {
                "text": "**Terrible!**\nJust take it easy and stay home! Today is just scary!\n｡゜:(つд⊂):゜。ｳえーﾝ；；",
                "colour": "FF0000",
                "img": "http://vignette3.wikia.nocookie.net/starwars/images/6/67/Bib_Fortuna_Force_Collection.png/revision/latest?cb=20150912064204"
            },
            self.check_fortune(fort, 1, 5): {
                "text": "**Abysmal!**\nMaybe you should just go to sleep until today is over!\nｩゎ━｡ﾟ(ﾟ´Д｀*ﾟ)ﾟ｡━ﾝ!!!",
                "colour": "800000",
                "img": "http://i.imgur.com/4Lcf07S.png"
            },
            self.check_fortune(fort, 0, 1): {
                "text": "**WURST!**\nI suppose your life hasn't been too bad!\n｡ﾟ(●ﾟ´Д)ﾉ｡ﾟヽ(　　)ﾉﾟ｡ヽ(Д｀ﾟ●)ﾉﾟ｡｡ﾟヽ(●ﾟ´Д｀ﾟ●)ﾉﾟ｡ｳﾜｧｧｧﾝ!!",
                "colour": "000000",
                "img": "http://68.media.tumblr.com/938a2d4fb94cae500839d9dccd3881be/tumblr_mn9j2tU3YU1s3kvg9o1_500.gif"
            }
        }
        e = discord.Embed(
            description="{}, your fortune is: {}".format(ctx.message.author.mention, fortune[True]["text"]),
            colour=int(fortune[True]["colour"], 16))
        if ctx.invoked_with == "fortuna" or ctx.invoked_with == "bib":
            e.set_image(url=fortune[True]["img"])
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
