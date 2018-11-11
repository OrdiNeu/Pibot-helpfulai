# Uncategorised extension for pibot
### PREAMBLE ##################################################################
import re
import random
import time

import discord
import requests
from discord.ext import commands

from .utils import twitter, scrollable, youtube, alarm


class Uncategorised:
    """Currently uncategorised commands"""

    def __init__(self, bot):
        self.bot = bot
        self.max_supported_pok2 = 494
        self.burd_nums = [
            6, 16, 17, 18, 21, 22, 41, 42, 54, 55, 83, 84, 85, 137, 142, 144, 145, 146, 149, 163, 164, 169, 176, 177,
            178, 198, 207, 225, 227, 233, 249, 250, 255, 256, 257, 276, 277, 278, 279, 333, 334, 344, 357, 373, 380,
            381, 393, 394, 395, 396, 397, 398, 430, 441, 468, 474, 488,
        ]
        self.rat_nums = [
            19, 20, 25, 26, 27, 172, 311, 312, 494
        ]

    async def pokemon2_request(self, rand_face, rand_body, rand_color=0):
        """Posts a randomly fused Pokemon"""
        # name URL section looks like:
        # <div style="z-index: 10;  position: relative; left: -95px;top: 105px;" align="center"><b>Swamturn</b>
        nameurl = "http://pokefusion.japeal.com/PKMColourV5.php?ver=3.2&p1={}&p2={}&c={}&&e=noone"
        "http://pokefusion.japeal.com/PKMColourV5.php?ver=3.2&p1=12&p2=148&c=0&&e=noone"
        requests_url = "http://pokefusion.japeal.com/{}/{}/{}"
        imgurl = "http://pokefusion.japeal.com/upload/{}X{}X{}.png"
        regex = re.compile("<div style=\"z-index: 10;  position: relative; left: -95px;top: 105px;"
                           "\" align=\"center\"><b>([A-Za-z0-9.♂♀'\-\s]*)</b>")
        name = ""
        # generate the random numbers Gen 1-5 pok numbers
        # randface = random.randrange(1, 494)
        # randbod = random.randrange(1, 494)
        # request the url with image to try to avoid the broken image problem
        try:
            status_code = requests.get(requests_url.format(rand_face, rand_body, rand_color)).status_code
            if status_code != 200:
                await self.bot.say("Bad Pok img, try again")
                return
            # leave third option (color) at default for now it seems buggy
            name_text = requests.get(nameurl.format(rand_face, rand_body, rand_color)).text
            name_search = regex.search(name_text)
            if name_search is not None:
                name = name_search.group(1)
            # turn into embed
            e = discord.Embed(title=name)
            # print(imgurl.format(randface, randbod, rand_color))
            e.set_image(url=imgurl.format(rand_face, rand_body, rand_color))
            time.sleep(0.2)
            await self.bot.say(embed=e)
        except ConnectionError:
            await self.bot.say("unable to generate pokemon right now, try later")

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

    @commands.command(aliases=['pokfusion'])
    async def pok2(self):
        """
        Posts a randomly fused Pokemon
        """
        # generate the random numbers Gen 1-5 pok numbers
        rand_face = random.randrange(1, self.max_supported_pok2)
        rand_body = random.randrange(1, self.max_supported_pok2)
        await self.pokemon2_request(rand_face=rand_face, rand_body=rand_body, rand_color=0)

    @commands.command()
    async def burd(self):
        """
        post a random "burd" pokemon
        at least either the head or the body has to be a "burd"
        :return:
        """
        use_head_or_body = False
        # random.choice([True, False])
        if use_head_or_body:
            rand_face = random.choice(self.burd_nums)
            rand_body = random.randrange(1, self.max_supported_pok2)
        else:
            rand_face = random.randrange(1, self.max_supported_pok2)
            rand_body = random.choice(self.burd_nums)
        await self.pokemon2_request(rand_face=rand_face, rand_body=rand_body)

    @commands.command()
    async def burd2(self):
        """
        post a random "burd" pokemon
        both must be "burd"
        :return:
        """
        rand_body = random.randrange(1, self.max_supported_pok2)
        rand_face = random.randrange(1, self.max_supported_pok2)
        await self.pokemon2_request(rand_face=rand_face, rand_body=rand_body)

    @commands.command()
    async def rat(self):
        """
        post a random "burd" pokemon
        at least either the head or the body has to be a "burd"
        :return:
        """
        use_head_or_body = random.choice([True, False])
        if use_head_or_body:
            rand_face = random.choice(self.rat_nums)
            rand_body = random.randrange(1, self.max_supported_pok2)
        else:
            rand_face = random.randrange(1, self.max_supported_pok2)
            rand_body = random.choice(self.rat_nums)
        await self.pokemon2_request(rand_face=rand_face, rand_body=rand_body)

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

    @commands.command(aliases=['siivagunner', 'silvagunner'], pass_context=True)
    async def siiva(self, ctx):
        """Grabs the YouTube upload list of Siivagunner, an unregistered user."""
        if youtube.API is None:
            await self.bot.say("YouTube API not initialized")
            return

        uploads = youtube.grabUploadsByPlaylistId("UU9ecwl3FTG66jIKA9JRDtmg")

        upload_urls = ["https://www.youtube.com/watch?v=" + s for s in uploads]
        response = scrollable.Scrollable(self.bot)
        await response.send(ctx.message.channel, upload_urls, locked_to=ctx.message.author)

    @commands.command(aliases=['flintstones'], pass_context=True)
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
        role_search = re.compile("(.*?[!?]role_up\s)(.*)")
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
        role_search = re.compile("(.*?[!?]role_tide\s)(.*)")
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

    @commands.command(aliases=["clan"], pass_context=True)
    async def swap_role(self, ctx):
        role_search = re.compile("(.*?[!?]clan\s)(.*)")
        search_role = role_search.search(ctx.message.content)
        valid_clans = ["crab", "crane", "dragon", "lion", "mantis", "phoenix", "scorpion", "unicorn", "spider", "ronin"]
        clan_emojii = [":crab:"]
        valid_roles = list()
        new_valid_role = None
        user_roles = ctx.message.author.roles
        if role_search is not None:
            target_role = search_role.group(2).lower()
            if target_role in valid_clans:
                # find list of role objects
                server_roles = ctx.message.server.roles
                try:
                    for role in server_roles:
                        if role.name.lower() in valid_clans:
                            valid_roles.append(role)
                        # while we're searching, save the target role
                        if role.name.lower() in target_role:
                            new_valid_role = role
                    # remove any current clans from current user's list
                    for role in valid_roles:
                        await self.bot.remove_roles(ctx.message.author, role)
                    # Add the new role
                    if new_valid_role is not None:
                        await self.bot.add_roles(ctx.message.author, new_valid_role)
                        await self.bot.say(":ok_hand:")
                        if new_valid_role in valid_roles:
                            valid_roles.remove(new_valid_role)
                        # remove any current clans from current user's list
                        for role in valid_roles:
                            await self.bot.remove_roles(ctx.message.author, role)
                except discord.Forbidden as df:
                    await self.bot.say("I lack sufficient permissions to do that: '{}".format(df.text))
            else:
                await self.bot.say("I couldn't find the role '{}' to assign you to".format(target_role))


def setup(bot):
    bot.add_cog(Uncategorised(bot))
