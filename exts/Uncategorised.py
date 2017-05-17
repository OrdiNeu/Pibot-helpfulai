# Uncategorised extension for pibot
### PREAMBLE ##################################################################
import re
import random

import discord
import requests
from discord.ext import commands

from .utils import twitter, scrollable, youtube

class Uncategorised:
    """Currently uncategorised commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def inspire(self):
        """Posts a random inspirational image"""
        digitA = random.randint(0, 2)
        digitB = random.randint(0, 9)
        numberA = str(digitA) + str(digitB)
        if numberA == "00":
            numberA = "30"
        number = random.randint(0, 9999)
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

        # turn into embed
        e = discord.Embed(title=name)
        # colour=?
        e.set_image(url=url)
        await self.bot.say(embed=e)

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
            desc = "*" + newdesc[1][3:] + "*"
            name = "{}**{}** -".format(newdesc[0], name)
        except:
            name = "Garfemon"
            desc = "Desc not found."
        desc = desc.replace("\\u2019", "'")
        desc = desc.replace("\\u201c", '"')
        desc = desc.replace("\\u201d", '"')
        desc = desc.replace("\\u2026", '...')
        desc = desc.replace("\\u202a", '')
        desc = desc.replace("\\u202c", '')
        desc = desc.replace("\\u2018", "'")

        # turn into embed
        e = discord.Embed(title=name, description=desc, colour=int("D68717", 16))
        e.set_image(url=img)
        await self.bot.say(embed=e)

    @commands.command(pass_context=True)
    async def pok(self, ctx):
        """Posts a random pokemon, randomly"""
        r = random.randint(1, 10)
        if r <= 7:
            await ctx.invoke(self.pokemon)
        else:
            await ctx.invoke(self.garfemon)

    @commands.command(aliases=['twatter'], pass_context=True)
    async def twitter(self, ctx):
        """Grabs the twitter feed of the given user, as a scrollable.
        Currently only grabs the latest 20 tweets"""
        if twitter.API is None:
            await self.bot.say("Twitter API not initialized")
            return

        # Parse out the timeline
        username = ctx.message.content.split()
        if len(username) > 1:
            username = " ".join(username[1:])
        if username.startswith("@"):
            username = username[1:]
        timeline = twitter.API.user_timeline(username)

        # Transform into a scrollable
        tweet_texts = []
        for tweet in timeline:
            tweet_texts.append(tweet.text)
        response = scrollable.Scrollable(self.bot)
        await response.send(ctx.message.channel, tweet_texts)
    
    @commands.command(aliases=['youtsube'], pass_context=True)
    async def youtube(self, ctx):
        """Grabs the YouTube upload list of the given user, as a scrollable."""
        if youtube.API is None:
            await self.bot.say("YouTube API not initialized")
            return
        
        # Parse out the username
        username = ctx.message.content.split()
        if len(username) > 1:
            username = " ".join(username[1:])
        uploads = youtube.grabUploads(username)
        if not type(uploads) is list:
            if uploads == youtube.ERROR_COULD_NOT_FIND_USER:
                await self.bot.say("Couldn't find the given user")
            elif uploads == youtube.ERROR_COULD_NOT_FIND_UPLOADS:
                await self.bot.say("Couldn't find uploads by the given user")
            return
        
        upload_urls = ["https://www.youtube.com/watch?v=" + s for s in uploads]
        response = scrollable.Scrollable(self.bot)
        await response.send(ctx.message.channel, upload_urls)

    @commands.command(aliases=['siivagunner', 'silvagunner'],pass_context=True)
    async def siiva(self, ctx):
        """Grabs the YouTube upload list of Siivagunner, an unregistered user."""
        if youtube.API is None:
            await self.bot.say("YouTube API not initialized")
            return

        uploads = youtube.grabUploadsByPlaylistId("UU9ecwl3FTG66jIKA9JRDtmg")
        
        upload_urls = ["https://www.youtube.com/watch?v=" + s for s in uploads]
        response = scrollable.Scrollable(self.bot)
        await response.send(ctx.message.channel, upload_urls)

def setup(bot):
    bot.add_cog(Uncategorised(bot))
