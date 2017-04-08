# Netrunner extension for pibot
### PREAMBLE ##################################################################
import re
import random
import threading
import time
from unidecode import unidecode

import discord
import requests
import emoji
from json.decoder import JSONDecodeError
from discord.ext import commands

from .utils.DiscordArgParse import DiscordArgparseParseError, DiscordArgParse
from .utils.listener import Listener

class NetrunQuiz(Listener):
    def __init__(self, bot, channel, nr_api):
        self.bot = bot
        self.attach(channel)
        self.card = random.choice(nr_api)
        self.answer_transforms = {
            "neutral-runner": "neutral",
            "neutral-corp": "neutral",
            "weyland-consortium": "weyland",
            "haas-bioroid": "hb"
            }
        # Check to make sure we pick an OK category to ask
        usable_category = False
        self.has_answered = {}
        while not usable_category:
            self.q_category = random.choice(list(self.card.keys()))
            self.answer = self.card[self.q_category]

            usable_category = True
            invalid_categories = ["code", "deck_limit", "flavor", "pack_code", "position",
                                  "quantity", "side_code", "title", "illustrator", "text",
                                  "keywords", "uniqueness"]
            if self.answer == "null":
                usable_category = False
            if self.q_category in invalid_categories:
                usable_category = False
        if self.answer in self.answer_transforms.keys():
            self.answer = self.answer_transforms[self.answer]

        # Timeout
        self.timer = threading.Timer(10.0, NetrunQuiz.end_game, args=[self, channel])
        self.timer.start()

    async def on_message(self, msg):
        if msg.content.lower() == "!end":
            await self.bot.send_message(msg.channel, "Stopping the quiz...")
            await self.end_game(msg.channel)
        if not msg.author.id in self.has_answered:
            self.has_answered[msg.author.id] = 1
            if msg.content.lower() == str(self.card[self.q_category]):
                await self.bot.add_reaction(msg, u"\U0001F3C6")
                await self.bot.send_message(msg.channel, msg.author.name + " got it!\nIt was: " + self.answer)
                self.detach(msg.channel.id)
                self.timer.cancel()
            else:
                await self.bot.add_reaction(msg, u"\U0001F6AB")

    async def end_game(self, channel):
        await self.bot.send_message(channel, "Time's up!\nIt was: " + self.answer)
        self.detach(channel.id)
        self.timer.cancel()

class Netrunner:
    """Netrunner related commands"""

    def __init__(self, bot):
        self.bot = bot
        self.nr_api = [{}]
        self.init_api = False
        self.max_message_len = 1990
        self.nets_help = "!nets command syntax:!nets --help or -h for flags listing\n"
        self.api_keys = "list of keys: (not all cards have all keys!)\n```title, text, cost, strength, " \
                        "keywords, type_code,\nuniqueness, faction_cost, memory_cost, trash_cost, advancement_cost," \
                        " agenda_points,\nside_code, faction_code, pack_code, position, quantity, \n" \
                        "base_link, influence_limit, deck_limit, minimum_deck_size,  flavor, illustrator, code```"
        self.type_code_sort = {'identity': 0, 'agenda': 1, 'asset': 2, 'upgrade': 3, 'operation': 4, 'ice': 5,
                               'event': 6,
                               'hardware': 7, 'resource': 8, 'program': 9}
        self.key_transforms = {
            "cost": "Cost",
            "strength": "Strength",
            "type_code": "Type",
            "faction_cost": "Influence",
            "memory_cost": "MU cost",
            "trash_cost": "🗑 cost",
            "advancement_cost": "Advancement cost",
            "agenda_points": "Agenda Points",
            "faction_code": "Faction",
            "base_link": "[🔁]",
            "influence_limit": "Influence Limit",
            "minimum_deck_size": "Deck Minimum Size",
            }


    def flag_parse(self, string_to_parse):
        m_response = ""
        m_criteria_list = []
        default_print_fields = ['uniqueness', 'base_link', 'title', 'cost', 'type_code', 'keywords', 'text',
                                'strength', 'trash_cost', 'faction_code', 'faction_cost', ]
        search_fields_appends = []
        type_fields_appends = []
        extra_type_fields = {
            'agenda': ('advancement_cost', 'agenda_points',),
            'identity': ('minimum_deck_size', 'influence_limit',),
            'program': ('memory_cost',),
            # 'ice': ('strength', ),
        }
        special_fields = ['code', 'uniqueness']
        nets_parser = DiscordArgParse(prog='flag_nets')
        # These first flags capture multiple words that follow, rather than the first word
        concat_categories = ['title', 'text', 'keywords', 'flavor_text', 'illustrator']
        nets_parser.add_argument(nargs="*", action="append", dest="title")
        nets_parser.add_argument('--text', '-x', nargs="+", action='append', dest="text")
        nets_parser.add_argument('--subtype', '-s', nargs="+", action='append', dest="keywords")
        nets_parser.add_argument('--flavor', '-a', nargs="+", action='append', dest="flavor_text")
        nets_parser.add_argument('--illustrator', '-i', nargs="+", action='append', dest="illustrator")
        # These flags capture a single type from a single word
        single_categories = ['type_code', 'faction_code', 'side_code', 'cost', 'advancement_cost', 'memory_cost',
                             'faction_cost', 'strength', 'agenda_points', 'base_link', 'deck_limit',
                             'minimum_deck_size',
                             'trash_cost', 'unique', 'pack_code']
        nets_parser.add_argument('-t', '--type', action='store', dest="type_code")
        nets_parser.add_argument('-f', '--faction', action='store', dest="faction_code")
        nets_parser.add_argument('-d', '--side', action='store', dest="side_code")
        nets_parser.add_argument('-e', '--set', action='store', dest="pack_code")
        nets_parser.add_argument('--nrdb_code', action='store', dest="code")
        nets_parser.add_argument('-o', '--cost', action='store', type=int, dest="cost")
        nets_parser.add_argument('-g', '--advancement-cost', action='store', type=int, dest="advancement_cost", )
        nets_parser.add_argument('-m', '--memory-usage', action='store', type=int, dest="memory_cost")
        nets_parser.add_argument('-n', '--influence', action='store', type=int, dest="faction_cost")
        nets_parser.add_argument('-p', '--strength', action='store', type=int, dest="strength")
        nets_parser.add_argument('-v', '--agenda-points', action='store', type=int, dest="agenda_points")
        nets_parser.add_argument('-l', '--base-link', action='store', type=int, dest="base_link")
        nets_parser.add_argument('-q', '--deck-limit', action='store', type=int, dest="deck_limit")
        nets_parser.add_argument('-z', '--minimum-deck-size', action='store', type=int, dest="minimum_deck_size")
        nets_parser.add_argument('-b', '--trash', action='store', type=int, dest="trash_cost")
        nets_parser.add_argument('-u', '--unique', action='store', type=bool, dest="unique")
        # special flags
        nets_parser.add_argument('--title-only', action='store_true', dest="title-only")
        nets_parser.add_argument('--image-only', action='store_true', dest="image-only")
        nets_parser.add_argument('--debug-flags', action='store_true', dest="debug-flags")
        try:
            args = nets_parser.parse_args(string_to_parse.split())
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
                                concat_string = self.apply_title_transform_jokes(concat_string.strip())
                            m_criteria_list.append((key, concat_string.strip()))
                # then check the lists that are done literally
                if key in single_categories:
                    if parser_dictionary[key] is not None:
                        if key not in default_print_fields:
                            search_fields_appends.append(key)
                        m_criteria_list.append((key, parser_dictionary[key]))
            if not self.init_api:
                self.refresh_nr_api()
            m_match_list = self.search_text(m_criteria_list)
            if len(m_match_list) == 0:
                m_response = "Search criteria returned 0 results\n"
                m_response += string_to_parse
            else:
                #  figure out how we're going to respond, if we're images only, skip parsing and use this.
                if parser_dictionary["image-only"]:
                    for i, card in enumerate(m_match_list[:5]):
                        m_response += "http://netrunnerdb.com/card_image/" + card['code'] + ".png\n"
                    if len(m_match_list) > 5:
                        m_response += "[{0}/{1}]".format(5, len(m_match_list))
                else:
                    for i, card in enumerate(m_match_list):
                        c_response = ""
                        # we have a card, so let's add the default type fields, if any by type
                        if card['type_code'] in extra_type_fields:
                            for extra_field in extra_type_fields[card['type_code']]:
                                if extra_field not in default_print_fields:
                                    type_fields_appends.append(extra_field)
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
                                c_response += self.transform_api_items_to_printable_format(c_key, card[c_key])
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
            if nets_parser.exit_message is not None:
                m_response += nets_parser.exit_message
        if len(m_response) >= self.max_message_len:
            # truncate message if it exceed the character limit
            m_response = m_response[:self.max_message_len - 10] + "\ncont..."
        return m_response

    @commands.command(name="flag_test", aliases=['nets'])
    async def arg_parse_nets(self, *, string_to_parse: str):
        m_response = self.flag_parse(string_to_parse)
        await self.bot.say(m_response)

    def transform_api_items_to_printable_format(self, api_key, value):
        # this function transforms the internal keys used in the api to a more user friendly print format
        value = self.replace_api_text_with_emoji(value)
        if value is True:
            unique_str = "🔹"
        else:
            unique_str = ""

        key_transform = {
            "title": "{0}".format(value),
            "text": "\n\"{0}\"".format(value),
            "cost": "\nCost: {0}".format(value),
            "strength": "\nStr: {0}".format(value),
            "keywords": ": {0}".format(value),
            "type_code": "\n{0}".format(value),
            "uniqueness": unique_str,
            "faction_cost": " {0}▪".format(value),
            "memory_cost": "\nMU: {0}".format(value),
            "trash_cost": "\n{0}🗑".format(value),
            "advancement_cost": "\nAdv: {0}".format(value),
            "agenda_points": "\nAP: {0}".format(value),
            "side_code": "\nside: {0}".format(value),
            "faction_code": "\nfaction: {0}".format(value),
            "pack_code": "\npack: {0}".format(value),
            "position": "\nposition: {0}".format(value),
            "quantity": "\nquantity: {0}\n".format(value),
            "base_link": "{0}🔁".format(value),
            "influence_limit": "/{0}\n".format(value),
            "deck_limit": "\ndeck limit: {0}".format(value),
            "minimum_deck_size": "\ndeck: {0}".format(value),
            "flavor": "\n{0}".format(value),
            "illustrator": "\nillustrator: {0}".format(value),
            "code": "\nhttp://netrunnerdb.com/card_image/{0}.png".format(value)
        }
        return key_transform[api_key]

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

    def sort_cards(self, cards):
        # input should be a list of full card dictionaries to be sorted
        # first sort by title
        cards = sorted(cards, key=lambda card: card['title'])
        # I should pre-sort the cards by sub types, before adding them to type major sort
        # todo add that before this line.
        # next sort by type
        cards = sorted(cards, key=lambda card: self.type_code_sort[card['type_code']])
        return cards

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

    def refresh_nr_api(self):
        self.nr_api = sorted([c for c in requests.get('https://netrunnerdb.com/api/2.0/public/cards').json()['data']],
                             key=lambda card: card['title'])
        self.init_api = True

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

    @staticmethod
    def apply_title_transform_jokes(card_title_criteria):
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
            "<:stoned:259424190111678464>": "mr. Stone"
        }
        if card_title_criteria in query_corrections.keys():
            card_title_criteria = query_corrections[card_title_criteria]
        return card_title_criteria

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

    @commands.command(name="old_nets", aliases=['leg_nets'])
    async def leg(self, *, cardname: str):
        await self.bot.say("hello")
        await self.bot.say("hello")
        await self.bot.say("hello")

    @commands.command(aliases=['nr', 'netrunner'])
    async def nr_flags(self, *, card_search:str):
        m_response = self.flag_parse(card_search + " --image-only")
        await self.bot.say(m_response)

    '''@commands.command(aliases=['netrunner'])
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
                for i, card in enumerate(m_cards[:5]):
                    m_response += "http://netrunnerdb.com/card_image/" + card['code'] + ".png\n"
                if len(m_cards) > 5:
                    m_response += "[{0}/{1}]".format(5, len(m_cards))
        await self.bot.say(m_response)
'''

    def deck_parse(self, deck_id):
        m_response = ""
        m_api_prefex = "https://netrunnerdb.com/api/2.0/public/decklist/"
        card_sort_list = []
        last_type = "identity"
        if not self.init_api:
            self.refresh_nr_api()
        try:
            decklist_data = [c for c in requests.get(m_api_prefex + deck_id).json()['data']]
            # decklist_data[0]['cards'] is a dict with card_id keys to counts {'10005': 1}
            m_response += "**{0}**\n".format(decklist_data[0]['name'])
            # id_search_tuple_list = [('code', "{0}".format(decklist_data[0]['id']))]
            # m_response += "{0}\n".format(self.search_text(id_search_tuple_list)[0]['title'])
            # build a list of tuples in the pairs, value(number of card), key (id of card)
            for number, card_id in [(v, k) for (k, v) in decklist_data[0]['cards'].items()]:
                # for number, card_id, in num_card_tup:
                card = self.search_text([('code', card_id)])[0]
                # add a key to the dictionary with the number of instances, to use later
                card['number'] = number
                card_sort_list.append(card)
                # card_title = self.search_text([('code', card_id)])[0]['title']
            card_sort_list = self.sort_cards(card_sort_list)
            for card in card_sort_list:
                response_addr = ""
                if last_type not in card['type_code']:
                    response_addr += "**{0}**\n".format(card['type_code'])
                    last_type = card['type_code']
                response_addr += "{0}x {1}\n".format(card['number'], card['title'])
                if (len(m_response) + len(response_addr)) >= self.max_message_len:
                    m_response += "cont..."
                    break
                else:
                    m_response += response_addr
        except JSONDecodeError as badUrlError:
            m_response = "Unhandled error in search!"
        return m_response

    @commands.command(aliases=['nd'])
    async def deck(self, *, decklist: str):
        m_response = ""
        m_decklist = unidecode(decklist.lower())
        re_decklist_id = re.search("(https://netrunnerdb\.com/en/decklist/)(\d+)(/.*)", m_decklist)
        if re_decklist_id is None:
            m_response += "I see: \"{0}\", but I don't understand\n".format(m_decklist)
        else:
            if re_decklist_id.group(2) is None:
                m_response += "I see: \"{0}\", but I don't understand\n".format(m_decklist)
            else:
                m_response += self.deck_parse(re_decklist_id.group(2))
            await self.bot.say(m_response[:2000])

    @commands.command(aliases=['ndrand'])
    async def rand_deck(self):
        m_response = ""
        today = time.strftime("%Y-%m-%d")
        decks = [c for c in requests.get(
            'https://netrunnerdb.com/api/2.0/public/decklists/by_date/%s' % today).json()['data']]
        selection = random.randrange(len(decks))
        id = str(decks[selection]['id'])
        hyphen_name = decks[selection]['name'].replace(" ", "-").lower()
        link = r"https://netrunnerdb.com/en/decklist/" + id + "/" + hyphen_name
        m_response += link + "\n"
        m_response += self.deck_parse(id)
        await self.bot.say(m_response[:2000])

    @commands.command(pass_context=True)
    async def quiz(self, ctx):
        quiz_opts = DiscordArgParse(prog='nr_quiz')
        quiz_opts.add_argument('--spoiler', '-s', action='store_true', dest="spoiler")
        try:
            #args = quiz_opts.parse_args(ctx.message.split())
            #parser_dictionary = vars(args)
            if not self.init_api:
                self.refresh_nr_api()
            quiz = NetrunQuiz(self.bot, ctx.message.channel.id, self.nr_api)
            if quiz.q_category in self.key_transforms:
                question = self.key_transforms[quiz.q_category]
            else:
                question = quiz.q_category
            await self.bot.say("What **{0}** is: *{1}*?".format(question, quiz.card["title"]))
        except DiscordArgparseParseError as se:
            if se.value is not None:
                await self.bot.say(se.value)
            if quiz_opts.exit_message is not None:
                await self.bot.say(quiz_opts.exit_message)


def test_arg_parse_nets(string_to_parse: str):
    m_response = ""
    m_criteria_list = []
    print_fields = ['uniqueness', 'title', 'text', 'cost', 'keywords', 'faction_code', 'faction_cost', 'trash_cost',
                    'type_code']
    extra_type_fields = {
        'agenda': ('advancement_cost', 'agenda_points',),
        'identity': ('base_link', 'influence_limit', 'deck_limit', 'minimum_deck_size',),
        'program': ('memory_cost', 'strength'),
        'ice': ('strength'), }
    special_fields = ['code', 'uniqueness']
    nets_parser = DiscordArgParse(prog='nets', description='args are processed as title, unless prefaced by a flag')
    # These first flags capture multiple words that follow, rather than the first word
    concat_categories = ['title', 'text', 'keywords', 'flavor_text', 'illustrator']
    nets_parser.add_argument(nargs="*", action="append", dest="title")
    nets_parser.add_argument('--text', '-x', nargs="+", action='append', dest="text")
    nets_parser.add_argument('--subtype', '-s', nargs="+", action='append', dest="keywords")
    nets_parser.add_argument('--flavor', '-a', nargs="+", action='append', dest="flavor_text")
    nets_parser.add_argument('--illustrator', '-i', nargs="+", action='append', dest="illustrator")
    # These flags capture a single type from a single word
    single_categories = ['type_code', 'faction_code', 'side_code', 'cost', 'advancement_cost', 'memory_cost',
                         'faction_cost', 'strength', 'agenda_points', 'base_link', 'deck_limit', 'minimum_deck_size',
                         'trash_cost', 'unique']
    nets_parser.add_argument('--type', '-t', action='store', dest="type_code")
    nets_parser.add_argument('--faction', '-f', action='store', dest="faction_code")
    nets_parser.add_argument('--side', '-d', action='store', dest="side_code")
    nets_parser.add_argument('--cost', '-o', action='store', type=int, dest="cost")
    nets_parser.add_argument('--advancement-cost', '-g', action='store', type=int, dest="advancement_cost", )
    nets_parser.add_argument('--memory-usage', '-m', action='store', type=int, dest="memory_cost")
    nets_parser.add_argument('--influence', '-n', action='store', type=int, dest="faction_cost")
    nets_parser.add_argument('--strength', '-p', action='store', type=int, dest="strength")
    nets_parser.add_argument('--agenda-points', '-v', action='store', type=int, dest="agenda_points")
    nets_parser.add_argument('--base-link', '-l', action='store', type=int, dest="base_link")
    nets_parser.add_argument('--deck-limit', '-q', action='store', type=int, dest="deck_limit")
    nets_parser.add_argument('--minimum-deck-size', '-z', action='store', type=int, dest="minimum_deck_size")
    nets_parser.add_argument('--trash', '-b', action='store', type=int, dest="trash_cost")
    nets_parser.add_argument('--unique', '-u', action='store', type=bool, dest="unique")
    try:
        args = nets_parser.parse_args(string_to_parse.split())
        parser_dictionary = vars(args)
        m_response += str(args)
    except DiscordArgparseParseError as se:
        if se.value is not None:
            m_response += se.value
        if nets_parser.exit_message is not None:
            m_response += nets_parser.exit_message
    # return args
    return m_response

def setup(bot):
    bot.add_cog(Netrunner(bot))
