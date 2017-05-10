# Uncategorised extension for pibot
### PREAMBLE ##################################################################
import discord
from discord.ext import commands
import requests
import re
import random

class Uncategorised:
    """Currently uncategorised commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def inspire(self):
        """Posts a random inspirational image"""
        digitA = random.randint(0,2)
        digitB = random.randint(0,9)
        numberA = str(digitA) + str(digitB)
        if numberA == "00": numberA = "30"
        number = random.randint(0,9999)
        response = "http://generated.inspirobot.me/0" + numberA + "/aXm" + str(number) + "xjU.jpg"
        await self.bot.say(response)

    @commands.command()
    async def pokemon(self):
        """Posts a randomly fused Pokemon"""
        site = "http://pokemon.alexonsager.net/"
        text = requests.get(site).text

        # <span id="pk_name">Oncute</span>
        # <img id="pk_img" height=160 width=160 src=http://images.alexonsager.net/pokemon/fused/102/102.95.png /><br />

        m = re.search('<span id="pk_name">(.*?)<', text)
        name = "**" + m.group(1) + "**"

        n = re.search('<img id="pk_img" height=160 width=160 src=(.*?)/><br', text)
        url = n.group(1)

        await self.bot.say(url + "\n" + name)

    @commands.command()
    async def garfemon(self):
        """Posts a random Garfemon"""
        number = random.randint(1, 11)
        site = "http://garfemon.tumblr.com/page/" + str(number)
        text = requests.get(site).text

        m = re.findall('http://garfemon.tumblr.com/post/(.*?)"', text)
        foundA = random.choice(m)
        garf = requests.get("http://garfemon.tumblr.com/post/" + foundA).text
        n = re.search('<img src="(.*?)" alt="', garf)
        img = n.group(1)

        # find description and name
        # http://68.media.tumblr.com/
        # d = re.search('"entry-content inner"><p>(.*?)&nbsp;</p>', garf)
        try:
            d = re.search(r'"articleBody":"(.*?)\\n', garf)
            desc = d.group(1)
        except:
            # garfmeleon and others seem to have different structure here
            d = re.search(r'"articleBody":"(.*?)"', garf)
            desc = d.group(1)
        try:
            # formatting
            # 042 - GOLGARF - This Garfemon loves to drink the blood of LIVING THINGS or the sauce from DEAD LASAGNA.
            u = re.search("- (.*?) -", desc)
            name = u.group(1)
            newdesc = desc.split(name, 1)
            name = "**" + name + "**"
            newnewdesc = "*" + newdesc[1][3:] + "*"
            desc = newdesc[0] + name + " - " + newnewdesc
        except:
            desc = "Desc not found."
        desc = desc.replace("\\u2019", "'")
        desc = desc.replace("\\u201c", '"')
        desc = desc.replace("\\u201d", '"')
        desc = desc.replace("\\u2026", '...')
        desc = desc.replace("\\u202a", '')
        desc = desc.replace("\\u202c", '')
        desc = desc.replace("\\u2018", "'")

        await self.bot.say(img + "\n" + desc)

    @commands.command(pass_context=True)
    async def pok(self, ctx):
        """Posts a random pokemon, randomly"""
        r = random.randint(1,10)
        if r <= 7:
            await ctx.invoke(self.pokemon)
        else:
            await ctx.invoke(self.garfemon)

def setup(bot):
    bot.add_cog(Uncategorised(bot))