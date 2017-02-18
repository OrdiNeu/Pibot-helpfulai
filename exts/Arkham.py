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
        self.init_api = False

    def refresh_ah_api(self):
        self.ah_api = sorted([c for c in requests.get('https://arkhamdb.com/api/public/cards').json()],
                             key=lambda card: card['name'])
        self.init_api = True


    @commands.command(aliases=['arkham','arkhamhorror'])
    async def ah(self, *, cardname : str):
        """Arkham Horror card lookup"""
        m_query = cardname.lower()

        # Auto-correct some card names (and inside jokes)
        query_corrections = {
            }
        if m_query in query_corrections.keys():
            m_query = query_corrections[m_query]

        # Auto-link some images instead of other users' names
        query_redirects = {
            }
        m_response = ""
        if m_query in query_redirects.keys():
            m_response = query_redirects[m_query]
        else:
            # Otherwise find and handle card names
            if not self.init_api:
                self.refresh_ah_api()
            m_cards = [c for c in self.ah_api if c['name'].lower().__contains__(m_query)]
            if len(m_cards) == 1:
                m_response = "http://arkhamdb.com" + m_cards[0]['imagesrc']
            elif len(m_cards) == 0:
                m_response += "Sorry, I cannot seem to find any card with these parameters:\n"
                m_response += "http://arkhamdb.com/find/?q=" + m_query.replace(" ", "+")
            else:
                for i, card in enumerate(m_cards)[:5]:
                    m_response = "http://arkhamdb.com{0}\n".format(card['imagesrc'])
                m_response += "[{0}/{1}]".format(i + 1, len(m_cards))
        await self.bot.say(m_response)


def setup(bot):
    bot.add_cog(Arkham(bot))
