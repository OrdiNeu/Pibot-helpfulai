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

    """
    criteria should be list of str.key:str.value tuples to be checked for exist in for each card
    """
    def search_text(self, criteria):
        m_response = ""
        card_match = True
        for s_card in sorted(self.nr_api, key=lambda card: card['title']):
            card_match = True
            for c_key, c_value in criteria:
                if c_key in s_card.keys():
                    try:
                        if isinstance(s_card[c_key], int):
                            if not int(c_value) == s_card[c_key]:
                                card_match = False
                                break
                        elif s_card[c_key] is None:
                            break
                            # print("None value from search for on " + s_card['code'])
                        else:
                            if not c_value in unidecode(s_card[c_key]).lower():
                                card_match = False
                                break
                                # print("match on " + c_value)
                    except ValueError:
                        m_response += "Value error parsing search!" + s_card['code'] + "\n"
                        return m_response
                        # print("ValueError on value from search " +
                        #  c_key + " for " + c_value + " on " + s_card['code'])
                else:
                    card_match = False
                    break
            if card_match:
                m_response += "http://netrunnerdb.com/card_image/" + s_card['code'] + ".png\n"
        return m_response

    def refresh_nr_api(self):
        self.nr_api = [c for c in requests.get('https://netrunnerdb.com/api/2.0/public/cards').json()['data']]
        self.init_api = True

    """
    Experimental section to test string parsing
    I want to turn
    !nr "title:deja influence:"
    title:value|text:value|influence:number
    by default?
    but also still support
    !nr <title>
    <card image link>
    """
    @commands.command(name="legnr", aliases=['nets'])
    async def leg(self, *, cardname: str):
        m_response = ""
        m_criteria_list = []
        #if not self.init_api:
        #    self.refresh_nr_api()
        """This should give me a list of key:str.value to search by"""

        f_crit = cardname.split("\"", 2)[1].split(" ")
        for key_val in f_crit:
            split_val = key_val.split(":")
            m_criteria_list.append((split_val[0], split_val[1]))
        m_response += self.search_text(m_criteria_list)
        await self.bot.say(m_response)

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
            "ordineu": "exile",
            "<:stoned:259424190111678464>": "blackstone"
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
            if len(m_cards) == 0:
                m_response += "Sorry, I cannot seem to find any card with these parameters:\n"
                m_response += "http://netrunnerdb.com/find/?q=" + m_query.replace(" ", "+")
            else:
                for card in m_cards[:10]:
                    m_response += "http://netrunnerdb.com/card_image/" + card['code'] + ".png\n"
        await self.bot.say(m_response)


def setup(bot):
    bot.add_cog(Netrunner(bot))
