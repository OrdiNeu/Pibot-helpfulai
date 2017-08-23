# Legend of the five rings extension for pibot
### PREAMBLE ##################################################################
import asyncio
import re
import time
from unidecode import unidecode

import discord
import requests
from discord.ext import commands

from .utils.DiscordArgParse import DiscordArgparseParseError, DiscordArgParse


class LFR:
    def __init__(self, bot):
        self.bot = bot
        self.api_cards = [{}]
        self.api_size = 0
        self.api_success = False
        self.api_last_updated = ""
        self.init_api = False
        self.l5r_help = "!l5r command syntax:!l5r --help or -h for flags listing\n"
        self.api_keys = "list of keys: (not all cards have all keys!)\n```clan, cost, deck_limit, id, " \
                        "influence_cost, military_bonus,\nname, name_canonical, pack_cards, political_bonus, " \
                        "side," \
                        " text,\ntext_canonical, traits, type, unicity, quantity, \n" \
                        "base_link, influence_limit, deck_limit, minimum_deck_size,  flavor, illustrator, code```"
        self.api_pack_cards_keys = "list of sub-category illustrator, pack, position, quantity"
        self.max_message_len = 1990

    def refresh_l5r_api(self):
        # api will respond with these keys: ['records', 'size', 'success', 'last_updated']
        api_response = requests.get('https://fiveringsdb.com/cards').json()
        self.api_cards = sorted([c for c in api_response['records']], key=lambda card: card['name_canonical'])
        self.api_success = api_response['success']
        self.api_last_updated = api_response['last_updated']
        self.api_size = api_response['size']
        self.init_api = True

    def flag_parse(self, string_to_parse):
        m_response = ""
        m_criteria_list = []
        default_print_fields = ['name', 'text', 'cost', 'type', 'unicity', 'side', 'clan']
        search_fields_appends = []
        type_fields_appends = []
        l5r_parser = DiscordArgParse(prog='flag_nets')
        # These first flags capture multiple words that follow, rather than the first word
        concat_categories = ['title', 'text']
        l5r_parser.add_argument(nargs="*", action="append", dest="name")
        l5r_parser.add_argument('--text', '-x', nargs="+", action='append', dest="text")
        # These flags capture a single type from a single word
        single_categories = ['type', 'clan', 'side', 'cost', 'unicity']
        l5r_parser.add_argument('-t', '--type', action='store', dest="type")
        l5r_parser.add_argument('-f', '--clan', action='store', dest="clan")
        l5r_parser.add_argument('-d', '--side', action='store', dest="side")
        l5r_parser.add_argument('-u', '--unique', action='store', type=bool, dest="unicity")
        # special flags
        l5r_parser.add_argument('--title-only', action='store_true', dest="title-only")
        l5r_parser.add_argument('--image-only', action='store_true', dest="image-only")
        l5r_parser.add_argument('--debug-flags', action='store_true', dest="debug-flags")
        try:
            args = l5r_parser.parse_args(string_to_parse.split())
            # return args
            parser_dictionary = vars(args)
            if parser_dictionary['debug-flags']:
                m_response += str(args) + "\n"
            # run through each key that we need to build up a list of words to check for exact existence,
            # and add them to the list, if they're in the args
            for key in parser_dictionary.keys():
                # first build up the parameters that need to be concatonated
                if key in concat_categories:
                    if parser_dictionary[key] is not None:
                        # Add the key to the printed result, if it's not already included
                        if key not in default_print_fields:
                            search_fields_appends.append(key)
                        # search parameters come in key: [['string'], ['other', 'string']
                        # for an input like: --flag string --flag other string
                        # we'll treat each --flag {value} as a seperate criteria that must be met, and join the
                        # 'other' 'string' into a match 'other string' exactly.
                        for word_list in parser_dictionary[key]:
                            concat_string = ""
                            for word in word_list:
                                concat_string += word + " "
                            if key in "title":
                                concat_string = concat_string.strip()
                            m_criteria_list.append((key, concat_string.strip()))
                # then check the lists that are done literally
                if key in single_categories:
                    if parser_dictionary[key] is not None:
                        if key not in default_print_fields:
                            search_fields_appends.append(key)
                        m_criteria_list.append((key, parser_dictionary[key]))
            if not self.init_api:
                self.refresh_l5r_api()
            m_match_list = self.search_text(m_criteria_list)
            if len(m_match_list) == 0:
                m_response = "Search criteria returned 0 results\n"
                m_response += string_to_parse
            else:
                #  figure out how we're going to respond, if we're images only, skip parsing and use this.
                if parser_dictionary["image-only"]:
                    for i, card in enumerate(m_match_list[:5]):
                        m_response += "https://fiveringsdb.com/bundles/card_images/" + card['id'] + ".png\n"
                    if len(m_match_list) > 5:
                        m_response += "[{0}/{1}]".format(5, len(m_match_list))
                else:
                    for i, card in enumerate(m_match_list):
                        c_response = ""
                        # we have a card, so let's add the default type fields, if any by type
                        # if card['type_code'] in extra_type_fields:
                        #   for extra_field in extra_type_fields[card['type_code']]:
                        #        if extra_field not in default_print_fields:
                        #            type_fields_appends.append(extra_field)
                        # if the flag is set, skip all text info
                        if parser_dictionary["title-only"]:
                            print_fields = ['title']
                        else:
                            # our list of fields to print starts with the default list of keys for all cards
                            print_fields = default_print_fields
                            # Add any fields that the particular card needs by its type
                            for field in type_fields_appends:
                                if field not in print_fields:
                                    print_fields.append(field)
                            # add any fields that the user explicitly searched for
                            for field in search_fields_appends:
                                if field not in print_fields:
                                    print_fields.append(field)
                        c_response += "```\n"
                        for c_key in print_fields:
                            if c_key in card.keys():
                                #c_response += self.transform_api_items_to_printable_format(c_key, card[c_key])
                                c_response += card[c_key]
                                # if c_key not in special_fields:
                                #    c_response += "{0}:\"{1}\"\n".format(
                                #        c_key, self.replace_api_text_with_emoji(card[c_key]))
                                # else:
                                #    if c_key in 'uniqueness' and card[c_key] is True:
                                #        c_response += '🔹:'
                                #    if c_key in 'code':
                                #        c_response += "http://netrunnerdb.com/card_image/{0}.png\n".format(
                                #           card[c_key])
                        c_response += "```\n"
                        if (len(m_response) + len(c_response)) >= (self.max_message_len - 20):
                            m_response += "\n[{0}/{1}]\n".format(i, len(m_match_list))
                            break
                        else:
                            m_response += c_response
        except DiscordArgparseParseError as dape:
            if dape.value is not None:
                m_response += dape.value
            if l5r_parser.exit_message is not None:
                m_response += l5r_parser.exit_message
        if len(m_response) >= self.max_message_len:
            # truncate message if it exceed the character limit
            m_response = m_response[:self.max_message_len - 10] + "\ncont..."
        return m_response

    @commands.command(aliases=['l5r'])
    async def l5r_flags(self, *, card_search: str):
        m_response = self.flag_parse(card_search + " --image-only")
        # await self.bot.say(m_response)
        description = ""
        for i, card in enumerate(m_response.split("\n")):
            time.sleep(0.5)
            embed_response = discord.Embed(title="[{}]".format(i), type="rich")
            url_search = re.search(r"(https://fiveringsdb\.com/bundles/card_images/)(.*)\..*$", card)
            if url_search is not None:
                embed_response.set_image(url=card)
                embed_response.description = "'{}'".format(card)
                await self.bot.say(embed=embed_response)
            else:
                description += card
        if len(description) > 0:
            embed_response = discord.Embed(title="search results:", type="rich")
            embed_response.description = description
            await self.bot.say(embed=embed_response)

    def search_text(self, criteria):
        '''
        :param criteria: criteria is a list of criteria used to search card's attributes for.
        multiple specified are unioned
        :return: card(s) that match the search criteria
        '''
        m_match = []
        card_match = True
        for i, s_card in enumerate(self.api_cards):
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
                            if not unidecode(c_value.lower()) in unidecode(s_card[c_key]).lower():
                                card_match = False
                                break
                                # print("match on " + c_value)
                    except ValueError:
                        return []
                        # m_response += "Value error parsing search!" + s_card['code'] + "\n"
                        # return m_response
                        # print("ValueError on value from search " +
                        #  c_key + " for " + c_value + " on " + s_card['code'])
                else:
                    card_match = False
                    break
            if card_match:
                m_match.append(s_card)
        return m_match


def setup(bot):
    bot.add_cog(LFR(bot))
