# Netrunner extension for pibot
### PREAMBLE ##################################################################
import re
from unidecode import unidecode

import discord
import requests
import emoji
from json.decoder import JSONDecodeError

from discord.ext import commands


class Netrunner:
    """Netrunner related commands"""

    def __init__(self, bot):
        self.bot = bot
        self.nr_api = [{}]
        self.init_api = False
        self.nets_help = "!nets command syntax:\n" \
                         "**!nets help!:** this listing\n" \
                         "**!nets keys!** list the keys that this database supports\n" \
                         "**!nets \"key:value\"** where key is a valid entry of the api, " \
                         "and value is an exact match.\n" + \
                         "any number of key:value pairs may be specified (space seperated), and the output will " \
                         "always include this key\n" + \
                         "**!nets \"key:value\" \"key\"** where the second \" bounded, space delineated keys are " \
                         "additional values to print, but not match on (title and text are always printed)"
        self.api_keys = "list of keys: (not all cards have all keys!)\n```title, text, cost, strength, " \
                        "keywords, type_code,\nuniqueness, faction_cost, memory_cost, trash_cost, advancement_cost," \
                        " agenda_points,\nside_code, faction_code, pack_code, position, quantity, \n" \
                        "base_link, influence_limit, deck_limit, minimum_deck_size,  flavor, illustrator, code```"

    @staticmethod
    def transform_trace(re_obj):
        ss_conv = {
            '0': '⁰',
            '1': '¹',
            '2': '²',
            '3': '³',
            '4': '⁴',
            '5': '⁵',
            '6': '⁶',
            '7': '⁷',
            '8': '⁸',
            '9': '⁹',
        }
        ret_string = "Trace"
        ret_string += ss_conv[re_obj.group(2)] + " -"
        return ret_string

    def parse_trace_tag(self, api_string):
        trace_tag_g = re.sub("(<trace>Trace )(\d)(</trace>)", self.transform_trace, api_string, flags=re.I)
        return trace_tag_g

    def parse_strong_tag(self, api_string):
        strong_g = re.sub("(<strong>)(.*?)(</strong>)", "**\g<2>**", api_string)
        return strong_g

    def replace_api_text_with_emoji(self, api_string):
        if isinstance(api_string, str):
            api_string = re.sub("(\[click\])", "🕖", api_string)
            api_string = re.sub("(\[recurring-credit\])", "💰⮐", api_string)
            api_string = re.sub("(\[credit\])", "💰", api_string)
            api_string = re.sub("(\[subroutine\])", "↳", api_string)
            api_string = re.sub("(\[trash\])", "🗑", api_string)
            api_string = re.sub("(\[mu\])", "μ", api_string)
            api_string = self.parse_trace_tag(api_string)
            api_string = self.parse_strong_tag(api_string)
        return api_string

    @staticmethod
    def replace_emoji_with_api_text(emoji_string):
        emoji_string = emoji.demojize(emoji_string)
        emoji_string = re.sub("🕖", "\[click\]", emoji_string)
        emoji_string = re.sub("💰", "\[credit\]", emoji_string)
        emoji_string = re.sub("💰⮐", "\[recurring-credit\)", emoji_string)
        emoji_string = re.sub("↳", "\[subroutine\)", emoji_string)
        emoji_string = re.sub("🗑", "\[trash\)", emoji_string)
        emoji_string = re.sub("μ", "\[mu\)", emoji_string)

        return emoji_string

    """
    criteria should be list of str.key:str.value tuples to be checked for exist in for each card
    """
    def search_text(self, criteria):
        m_match = []
        card_match = True
        for i, s_card in enumerate(self.nr_api):
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

    def refresh_nr_api(self):
        self.nr_api = sorted([c for c in requests.get('https://netrunnerdb.com/api/2.0/public/cards').json()['data']],
                             key=lambda card: card['title'])
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
        """
        !nets command syntax:
        !nets help!: this listing
        !nets keys! list the keys that this database supports
        !nets \"key:value\" where key is a valid entry of the api, and value is an exact match.
            any number of key:value pairs may be specified (space separated),
            and the output will always include this key.
        !nets \"key:value\" \"key\" where the second \" bounded, space delineated keys are
        additional values to print, but not match on ('title' and 'text' and search criteria are always printed)
        """
        m_response = ""
        m_criteria_list = []
        print_fields = ['uniqueness', 'title', 'text', 'cost', 'keywords', 'faction_code', 'faction_cost', 'trash_cost',
                        'type_code']
        extra_type_fields = {
            'agenda': ('advancement_cost', 'agenda_points',),
            'identity': ('base_link', 'influence_limit', 'deck_limit', 'minimum_deck_size',),
            'program': ('memory_cost', 'strength'),
            'ice': ('strength'),
        }
        special_fields = ['code', 'uniqueness']
        if not self.init_api:
            self.refresh_nr_api()
        """This should give me a list of key:str.value to search by"""
        # command = re.search('\s*(help!)*\s*(keys!)*\s*(.*?)*\s*(".*?")*', cardname)
        param_parse = re.search('''\s*(help!)*\s*(keys!)*\s*([^"]*)(".*")*.*''', cardname)
        # first we parse into the search criteria or help command, or the field param
        # (0) full line
        # (1) "help!" or None if not specified
        # (2) 'keys!' list all keys command or None if not specified
        # (3) value and/or 'value value' and/or key:'value'
        # (4) "extra_key other_extra_key"

        title_preview = re.search('''([\w\s\']*)(?![\w\:])([\w\:\s\']*)''', param_parse.group(3))

        # command should build a re group with
        # (0) full line
        # (1) cheat for first title params up to negative lookback to first word with ':' in it
        # (2) 'title:value pairs beyond first implicit title'
        #   value value' and/or 'key:value"' section or None if not specified
        extra_search = re.sub('\"(.*?)\s*\"', "\g<1>", title_preview.group(2)).split(" ")
        # I need to fix up this one, it's not splitting properly yet
        command = re.search('''((?:\w(?!\s+')+|\s(?!\s*'))+\w)\s*(.*)\s*''', cardname)

        if param_parse is None:
            m_response += "I see: \"{0}\", but I don't understand\n".format(cardname)
            m_response += self.nets_help
        else:
            if param_parse.group(1) is not None or (param_parse.group(3) is None and param_parse.group(2) is None):
                # if the user asks for help, or doesn't specify the expected arguments, print help
                m_response += self.nets_help
            else:
                if param_parse.group(2) is not None:
                    # if the user specifies they're looking for keys listing print that and stop
                    m_response += self.api_keys
                else:
                    # for key_val in re.sub('\"(.*?)\s*\"', "\g<1>", command.group(3)).split(" "):
                    m_criteria_list.append(('title', title_preview.groups()[0].strip("\' ").lower()))
                    for key_tup in title_preview.groups()[1:]:
                        # each key_val in our second parameter is split into sanitized key:value key_val iterators
                        split_val = key_tup.split(":")
                        if len(split_val) != 2:
                            continue
                        m_criteria_list.append((split_val[0], split_val[1].lower().strip('\'')))
                        if split_val[0] not in print_fields:
                            print_fields.append(split_val[0])
                    if param_parse.group(4) is not None:
                        for field in re.sub('\"(.*?)\s*\"', "\g<1>", param_parse.group(4)).split(" "):
                            if field not in print_fields:
                                print_fields.append(field)
                    m_match_list = self.search_text(m_criteria_list)
                    if len(m_match_list) == 0:
                        m_response = "Search criteria returned 0 results"
                    else:
                        for card in m_match_list:
                            # we have a card, so let's add the default type fields, if any by type
                            if card['type_code'] in extra_type_fields:
                                for extra_field in extra_type_fields[card['type_code']]:
                                    if extra_field not in print_fields:
                                        print_fields.insert(3, extra_field)
                            m_response += "```\n"
                            for c_key in print_fields:
                                if c_key in card.keys():
                                    if c_key not in special_fields:
                                        m_response += "{0}:\"{1}\"\n".format(
                                            c_key, self.replace_api_text_with_emoji(card[c_key]))
                                    else:
                                        if c_key in 'uniqueness' and card[c_key] is True:
                                            m_response += '🔹:'
                                        if c_key in 'code':
                                            m_response += "http://netrunnerdb.com/card_image/{0}.png\n".format(
                                                card[c_key])
                            m_response += "```\n"
        if len(m_response) >= 2000:
            # truncate message if it exceed the character limit
            m_response = m_response[:1990] + "\ncont..."
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

    @commands.command(aliases=['nd'])
    async def deck(self, *, decklist: str):
        m_response = ""
        m_api_prefex = "https://netrunnerdb.com/api/2.0/public/decklist/"
        m_decklist = unidecode(decklist.lower())
        re_decklist_id = re.search("(https://netrunnerdb\.com/en/decklist/)(\d+)(/.*)", decklist)
        if re_decklist_id is None:
            m_response += "I see: \"{0}\", but I don't understand\n".format(m_decklist)
        else:
            if re_decklist_id.group(2) is None:
                m_response += "I see: \"{0}\", but I don't understand\n".format(m_decklist)
            else:
                if not self.init_api:
                    self.refresh_nr_api()
                # decklist_id = "41160"
                decklist_id = re_decklist_id.group(2)
                # make a request for the id of the decklist posted in the commandline
                # should get a result array, 1 len
                # dict in array, dict_keys(['id', 'date_creation', 'date_update', 'name',
                # 'description', 'user_id', 'user_name', 'tournament_badge', 'cards'])
                try:
                    decklist_data = [c for c in requests.get(m_api_prefex + decklist_id).json()['data']]
                    # decklist_data[0]['cards'] is a dict with card_id keys to counts {'10005': 1}
                    m_response += "{0}\n".format(decklist_data[0]['name'])
                    m_response += "{0}\n".format(self.search_text([('code', "{0}".format(decklist_data[0]['id']))]))
                    # build a list of tuples in the pairs, value(number of card), key (id of card)
                    for number, card_id in [(v, k) for(k, v) in decklist_data[0]['cards'].items()]:
                        #for number, card_id, in num_card_tup:
                        card_title = self.search_text([('code', card_id)])[0]['title']
                        m_response += "{0}x {1}\n".format(number, card_title)
                except JSONDecodeError as badUrlError:
                    m_response = "Unhandled error in search!"


def setup(bot):
    bot.add_cog(Netrunner(bot))
