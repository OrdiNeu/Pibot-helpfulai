# Netrunner extension for pibot
### PREAMBLE ##################################################################
import re
from unidecode import unidecode

import discord
import requests

from discord.ext import commands




class Netrunner:
    """Netrunner related commands"""

    def __init__(self, bot):
        self.bot = bot
        self.nr_api = [{}]
        self.init_api = False

    def search_text(self, criteria):
        m_response = ""
        for s_card in sorted(self.nr_api, key=lambda card: card['title']):
            if 'text' in s_card.keys():
                if criteria in s_card['text']:
                    m_response += "http://netrunnerdb.com/card_image/" + s_card['code'] + ".png\n"
        return m_response

    def refresh_nr_api(self):
        self.nr_api = [c for c in requests.get('https://netrunnerdb.com/api/2.0/public/cards').json()['data']]
        self.init_api = True

    @commands.command(aliases=['netrunner'])
    async def nr(self, *, cardname: str):
        """Netrunner card lookup"""
        m_query = unidecode(cardname.lower())

        # Auto-correct some card names (and inside jokes)
        query_corrections = {
            "smc": "self-modifying code",
            "jesus": "jackson howard",
            "nyan": "noise",
            "neh": "near earth hub",
            "sot": "same old thing",
            "tilde": "blackat",
            "neko": "blackat",
            "ordineu": "exile"
        }
        if m_query in query_corrections.keys():
            m_query = query_corrections[m_query]

        # Auto-link some images instead of other users' names
        query_redirects = {
            "triffids": "http://run4games.com/wp-content/gallery/altcard_runner_id_shaper/Nasir-by-stentorr-001.jpg"
        }
        m_response = ""
        if m_query in query_redirects.keys():
            m_response = query_redirects[m_query]
        else:
            if not self.init_api:
                self.refresh_nr_api()
            # Otherwise find and handle card names
            m_cards = [c for c in self.nr_api if unidecode(c['title'].lower()).__contains__(m_query)]
            for x in range(0, len(m_cards)):
                if m_query == m_cards[x]['title'].lower():
                    m_response = "http://netrunnerdb.com/card_image/" + m_cards[x]['code'] + ".png"
            if len(m_cards) == 1:
                m_response = "http://netrunnerdb.com/card_image/" + m_cards[0]['code'] + ".png"
            elif len(m_cards) == 0:
                m_response = "Sorry, I cannot seem to find any card with these parameters."
            else:
                m_response = "http://netrunnerdb.com/find/?q=" + m_query.replace(" ", "+")
        await self.bot.say(m_response)

    @commands.command(aliases=['legnetrunner'])
    async def lnr(self, cardname: str):
        """Leg's experimental Netrunner card lookup"""
        m_query = unidecode(cardname.lower())
        m_query.rsplit()
        if not self.init_api:
            self.refresh_nr_api()


def setup(bot):
    bot.add_cog(Netrunner(bot))
