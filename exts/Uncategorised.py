# Uncategorised extension for pibot
### PREAMBLE ##################################################################
import re
import random

import discord
import requests
from discord.ext import commands

from .utils import twitter, scrollable, youtube, alarm

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

    @commands.command(aliases=['rat'])
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
        await response.send(ctx.message.channel, upload_urls, locked_to=ctx.message.author)

    @commands.command(aliases=['siivagunner', 'silvagunner'],pass_context=True)
    async def siiva(self, ctx):
        """Grabs the YouTube upload list of Siivagunner, an unregistered user."""
        if youtube.API is None:
            await self.bot.say("YouTube API not initialized")
            return

        uploads = youtube.grabUploadsByPlaylistId("UU9ecwl3FTG66jIKA9JRDtmg")
        
        upload_urls = ["https://www.youtube.com/watch?v=" + s for s in uploads]
        response = scrollable.Scrollable(self.bot)
        await response.send(ctx.message.channel, upload_urls, locked_to=ctx.message.author)

    @commands.command(aliases=['flintstones'],pass_context=True)
    async def flint(self, ctx):
        """Grabs the YouTube upload list of Siivagunner, an unregistered user."""
        if youtube.API is None:
            await self.bot.say("YouTube API not initialized")
            return

        uploads = youtube.grabUploadsByPlaylistId("PLzDaKOnENQJ98YMmY5vrvzkm0Sc68IPa3")
        upload_urls = ["https://www.youtube.com/watch?v=" + s for s in uploads]
        response = scrollable.Scrollable(self.bot)
        await response.send(ctx.message.channel, upload_urls, locked_to=ctx.message.author)

    class YouTubeAlarm(alarm.Alarm):
        """Waits for a new upload by the given YouTube channel, then tells everyone"""
        def __init__(self, bot, channel, playlistID):
            self.bot = bot
            self.playlistID = playlistID
            self.channel = channel
            self.last_known_siiva_upload = ""
            self._initialized = False
            super().__init__()

        async def initialize(self):
            self._initialized = True
            self.last_known_siiva_upload = await self.get_latest_upload()

        async def get_latest_upload(self):
            """Grabs the latest upload by Siivagunner"""
            if youtube.API is None:
                await self.bot.send_message(
                    self.channel,
                    'YouTube API not initialized'
                    )
                return

            uploads = youtube.grabUploadsByPlaylistId(self.playlistID)
            return uploads[0]
    
        async def run(self):
            """Auto-run via alarm: check for a new upload"""
            newest_upload = await self.get_latest_upload
            if self.last_known_siiva_upload != newest_upload:
                self.last_known_siiva_upload = newest_upload
                await self.bot.send_message(
                    self.channel,
                    "https://www.youtube.com/watch?v=" + newest_upload
                    )
            self.attach(3600)

    @commands.command(pass_context=True)
    async def waitforsiiva(self, ctx):
        """Checks every hour a new upload by Siivagunner.
        Yeah I know this is a bit hard to use right now. Bear with me"""
        new_alarm = Uncategorised.YouTubeAlarm(
            self.bot,
            ctx.message.channel,
            "UU9ecwl3FTG66jIKA9JRDtmg"
            )
        await new_alarm.initialize()
        new_alarm.attach(3600)
        await self.bot.say("Ok, I will let you know when the next Siivagunner upload happens")
    
    class BugMe(alarm.Alarm):
        """Temporary testing rig for alarms"""
        def __init__(self, bot, channel):
            self.bot = bot
            self.channel = channel
            super().__init__()
        
        async def run(self):
            await self.bot.send_message(
                self.channel,
                'Test'
                )
            self.attach(5)
    
    @commands.command(pass_context=True)
    async def bugme(self, ctx):
        """Temporary testing rig for alarms"""
        new_alarm = Uncategorised.BugMe(self.bot, ctx.message.channel)
        new_alarm.attach(5)

    @commands.command(aliases=['role_up'], pass_context=True)
    async def add_role(self, ctx):
        role_search = re.compile("([!?]role_up\s)(.*)")
        server_roles = ctx.message.server.roles
        user_roles = ctx.message.author.roles
        search_role = role_search.search(ctx.message.content)
        try:
            if search_role is not None:
                target_role = search_role.group(2)
                for role in server_roles:
                    if target_role in role.name:
                        if role not in user_roles:
                            await self.bot.add_roles(ctx.message.author, role)
                            await self.bot.say(":ok_hand:")
        except discord.Forbidden as df:
            await self.bot.say("I lack sufficient permissions to do that: '{}".format(df.text))

    @commands.command(aliases=['role_tide'], pass_context=True)
    async def remove_role(self, ctx):
        role_search = re.compile("([!?]role_tide\s)(.*)")
        user_roles = ctx.message.author.roles
        search_role = role_search.search(ctx.message.content)
        try:
            if role_search is not None:
                target_role = search_role.group(2)
                for role in user_roles:
                    if target_role in role.name:
                        await self.bot.remove_roles(ctx.message.author, role)
                        await self.bot.say(":ok_hand:")

        except discord.Forbidden as df:
            await self.bot.say("I lack sufficient permissions to do that: '{}".format(df.text))

def setup(bot):
    bot.add_cog(Uncategorised(bot))
