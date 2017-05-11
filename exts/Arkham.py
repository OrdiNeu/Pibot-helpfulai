# Netrunner extension for pibot
### PREAMBLE ##################################################################
import re

import discord
import requests

from discord.ext import commands

class Arkham:
    """Arkham Horror related commands"""

    def __init__(self, bot):
        self.bot = bot
        self.ah_api = [{}]
        self.ah_api_p = [{}]
        self.init_api = False

    def refresh_ah_api(self):
        self.ah_api = sorted([c for c in requests.get('https://arkhamdb.com/api/public/cards?encounter=1').json()],
                             key=lambda card: card['name'])
        # only player cards
        self.ah_api_p = [c for c in self.ah_api if not "spoiler" in c]
        self.init_api = True


    @commands.command(aliases=['arkham','arkhamhorror', 'ahe', 'ahb', 'ah1', 'ah2', 'ah3', 'ah4', 'ah5', 'aha'], pass_context=True)
    async def ah(self, ctx):
    #async def ah(self, ctx, *, cardname: str):
        """Arkham Horror card lookup"""
        m_query = ctx.message.content.split(" ", 1)[1].lower()
        #m_query = cardname.lower()
        img = 'imagesrc'

        # Auto-correct some card names (and inside jokes)
        query_corrections = {
            "mississippi manatee": "leo de luca",
            "manatee": "leo de luca",
            "ordineu": "scavenging"
            }
        if m_query in query_corrections.keys():
            m_query = query_corrections[m_query]

        # Auto-link some images instead of other users' names
        query_redirects = {
            }
        m_response = ""
        if m_query in query_redirects.keys():
            m_response = query_redirects[m_query]
        elif not m_query:
            # post help text if no query
            m_response = "!ah [name] - Player card search\n"
            m_response += "!ahe [name] - Encounter card search\n"
            m_response += "!ahb [name] - Search for card backsides\n"
            m_response += "!ahX [name] - Player card search with level X\n"
            m_response += "!aha [name] - Search through all cards and post up to 5"
        else:
            # Otherwise find and handle card names
            if not self.init_api:
                self.refresh_ah_api()

            if ctx.invoked_with == "ahe":
                # search encounter cards
                m_cards = [c for c in self.ah_api if c['name'].lower().__contains__(m_query) and "spoiler" in c]
                if not m_cards:
                    # search back side names of agendas/ acts
                    m_cards = [c for c in self.ah_api if
                               "back_name" in c and c["back_name"].lower().__contains__(m_query)]
                    img = 'backimagesrc'
            elif ctx.invoked_with[-1] in ["0", "1", "2", "3", "4", "5"]:
                # search for player cards with specific level
                n = int(ctx.invoked_with[-1])
                m_cards = [c for c in self.ah_api_p if c['name'].lower().__contains__(m_query) and c['xp'] == n]
            elif ctx.invoked_with == "ahb":
                # search card back sides
                m_cards = [c for c in self.ah_api if
                           (c['name'].lower().__contains__(m_query) and 'backimagesrc' in c) or (
                           "back_name" in c and c["back_name"].lower().__contains__(m_query))]
                img = 'backimagesrc'
            elif ctx.invoked_with == "aha":
                # search all cards
                m_cards = [c for c in self.ah_api if c['name'].lower().__contains__(m_query)]
            else:
                # search player cards
                m_cards = [c for c in self.ah_api_p if c['name'].lower().__contains__(m_query)]

            for c in m_cards:
                if m_query == c['name'].lower():
                    # if exact name match, post only the one card
                    m_cards = [c]
                    break
            if len(m_cards) == 1:
                try:
                    m_response += "http://arkhamdb.com" + m_cards[0][img]
                except KeyError as e:
                    if e.args[0] == "imagesrc":
                        # if no image on ArkhamDB
                        m_response = "'{}' has no image on ArkhamDB:\n".format(m_cards[0]['name'])
                        m_response += "https://arkhamdb.com/card/" + m_cards[0]["code"]
            elif len(m_cards) == 0:
                m_response += "Sorry, I cannot seem to find any card with these parameters:\n"
                m_response += "http://arkhamdb.com/find/?q=" + m_query.replace(" ", "+")
            else:
                if ctx.invoked_with == "aha":
                    # post up to 5 images with !aha command
                    for i, card in enumerate(m_cards[:5]):
                        m_response += "http://arkhamdb.com{0}\n".format(card[img])
                    if len(m_cards) > 5:
                        m_response += "[{0}/{1}]".format(5, len(m_cards))
                else:
                    # else just post a link
                    m_response = "'{}' matching cards found:\n".format(len(m_cards))
                    m_response += "https://arkhamdb.com/find?q=" + m_query.replace(" ", "+")
        await self.bot.say(m_response[:2000])


def setup(bot):
    bot.add_cog(Arkham(bot))
