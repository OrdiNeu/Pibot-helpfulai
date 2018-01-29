# Netrunner extension for pibot
### PREAMBLE ##################################################################
import asyncio
import re
import random
import time
from unidecode import unidecode

import discord
import emoji
import requests
from collections import OrderedDict
from tabulate import tabulate
from json.decoder import JSONDecodeError
from discord.ext import commands

from .utils.DiscordArgParse import DiscordArgparseParseError, DiscordArgParse
from .utils.listener import MsgListener


class NetrunnerDBCard:
    def __init__(self, api_dict):
        # card primitives (must be present in every card)
        # strings
        self.side_code = api_dict['side_code']
        self.type_code = api_dict['type_code']
        self.faction_code = api_dict['faction_code']
        self.pack_code = api_dict['pack_code']
        self.title = api_dict['title']
        # parsed int
        self.deck_limit = int(api_dict['deck_limit'])
        self.code = int(api_dict['code'])
        self.position = int(api_dict['position'])
        self.quantity = int(api_dict['quantity'])
        # the one boolean
        self.uniqueness = api_dict['uniqueness']
        # card variables, may or may not be set to non-None
        # type should be string:
        self.flavor = None
        if 'flavor' in api_dict:
            self.flavor = api_dict['flavor']
        self.illustrator = None
        if 'illustrator' in api_dict:
            self.illustrator = api_dict['illustrator']
        self.text = None
        if 'text' in api_dict:
            self.text = api_dict['text']
        self.image_url = None
        if 'image_url' in api_dict:
            if api_dict['image_url']:
                self.image_url = self.fix_https(api_dict['image_url'])
        # type should be int
        self.influence_limit = None
        if 'influence_limit' in api_dict:
            if api_dict['influence_limit'] is not None:
                self.influence_limit = int(api_dict['influence_limit'])
        self.minimum_deck_size = None
        if 'minimum_deck_size' in api_dict:
            if api_dict['minimum_deck_size'] is not None:
                self.minimum_deck_size = int(api_dict['minimum_deck_size'])
        self.base_link = None
        if 'base_link' in api_dict:
            if api_dict['base_link'] is not None:
                self.base_link = int(api_dict['base_link'])
        self.cost = None
        if 'cost' in api_dict:
            if api_dict['cost'] is not None:
                self.cost = int(api_dict['cost'])
        self.faction_cost = None
        if 'faction_cost' in api_dict:
            if api_dict['faction_cost'] is not None:
                self.faction_cost = int(api_dict['faction_cost'])
        self.memory_cost = None
        if 'memory_cost' in api_dict:
            if api_dict['memory_cost'] is not None:
                self.memory_cost = int(api_dict['memory_cost'])
        self.strength = None
        if 'strength' in api_dict:
            if api_dict['strength'] is not None:
                self.strength = int(api_dict['strength'])
        self.advancement_cost = None
        if 'advancement_cost' in api_dict:
            if api_dict['advancement_cost'] is not None:
                self.advancement_cost = int(api_dict['advancement_cost'])
        self.agenda_points = None
        if 'agenda_points' in api_dict:
            if api_dict['agenda_points'] is not None:
                self.agenda_points = int(api_dict['agenda_points'])
        self.trash_cost = None
        if 'trash_cost' in api_dict:
            if api_dict['trash_cost'] is not None:
                self.trash_cost = int(api_dict['trash_cost'])
        # type should be list(str)
        self.keywords = list()
        if 'keywords' in api_dict:
            for keyword in api_dict['keywords'].split("-"):
                self.keywords.append(keyword.strip())
        # things that aren't cards
        self.legality = list()
        self.assign_legality()
        self.type_code_sort = {
            'identity': 0, 'agenda': 1, 'asset': 2, 'upgrade': 3, 'operation': 4, 'ice': 5,
            'event': 6, 'hardware': 7, 'resource': 8, 'program': 9}
        self.extra_type_fields = {
            'agenda': ('advancement_cost', 'agenda_points',),
            'identity': ('minimum_deck_size', 'influence_limit',),
            'program': ('memory_cost',),
            # 'ice': ('strength', ),
        }
        self.default_print_fields = [
            'uniqueness', 'base_link', 'title', 'cost', 'type_code', 'keywords', 'text', 'strength', 'trash_cost',
            'faction_code', 'faction_cost', ]
        self.all_print_fields = [
            'code', 'deck_limit', 'faction_code', 'flavor', 'illustrator', 'influence_limit', 'keywords',
             'minimum_deck_size', 'pack_code', 'position', 'quantity', 'side_code', 'text', 'title', 'type_code',
             'uniqueness', 'base_link', 'cost', 'faction_cost', 'memory_cost', 'strength', 'advancement_cost',
             'agenda_points', 'trash_cost', 'image_url', 'legality',
        ]
        self.faction_color = {
            'jinteki': 0x660000,
            'haas-bioroid': 0x4B285A,
            'weyland-consortium': 0x385547,
            'nbn': 0xFFEB2C,
            'neutral-corp': 0x574D43,
            'shaper': 0x38CD2E,
            'anarch': 0xCD632E,
            'criminal': 0x2E78CD,
            'adam': 0x878710,
            'sunny-lebeau': 0x491349,
            'apex': 0xA20323,
            'neutral-runner': 0xF0EBE6,
        }

    def assign_legality(self):
        self.legality = list()
        # 2 decimal prefix: Any prefix except core2.0 + three decimal suffix
        legacy_legal_code_regex = "((00)|(01)|(02)|(03)|(04)|(05)|(06)|(07)|(08)|(09)|(10)|(11)|(12)|(13))(\d\d\d)"
        # 2 decimal prefix:  C&C | H&P | O&C | D&D | TD | Flashpoint | Red Sand | Core2.0 + three decimal suffix
        cache_refresh_legal_code_regex = "((03)|(05)|(07)|(09)|(13)|(11)|(12)|(20))(\d\d\d)"
        # 2 decimal prefix:  C&C | H&P | Lunar| O&C | SanSan | D&D | Mumbad | Flashpoint | Red Sand | TD |
        # Core2.0 + three decimal suffix
        rotation_legal_code_regex = "((03)|(05)|(06)|(07)|(08)|(09)|(10)|(11)|(12)|(13)|(20))(\d\d\d)"
        # (rotation)|(legacy)|(cr)
        if re.search(legacy_legal_code_regex, "{:06}".format(self.code)):
            self.legality.append('legacy')
        if re.search(cache_refresh_legal_code_regex, "{:06}".format(self.code)):
            self.legality.append('cr')
        if re.search(rotation_legal_code_regex, "{:06}".format(self.code)):
            self.legality.append('rotation')

    def transform_api_field_to_printable_format(self, field):
        # this function transforms the internal keys used in the api to a more user friendly print format
        value_list = list()
        value = ""
        unique_str = ""
        if type(self.__dict__[field]) is not list:
            value_list.append(self.__dict__[field])
        else:
            value_list = self.__dict__[field]
        for v in value_list:
            if v is None:
                return ""
            if v is True:
                unique_str = "🔹"
            if type(v) is str:
                value += self.replace_api_text_with_emoji(v) + " "
            else:
                value = v
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
            "code": "\nnrdb_code '{0}'".format(value),
            "legality": "\nlegality sets '{}'".format(value),
            "image_url": "\nimage_url'{}'".format(value),
        }
        return key_transform[field]

    @staticmethod
    def clean_api_value_for_compare(api_value):
        if type(api_value) is int:
            return api_value
        return unidecode(api_value.strip().lower())

    def parse_trace_tag(self, api_string):
        trace_tag_g = re.sub("(<trace>Trace )(\d)(</trace>)", self.transform_trace, api_string, flags=re.I)
        return trace_tag_g

    @staticmethod
    def parse_strong_tag(api_string):
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
    def fix_https(url):
        # Fixes http:// to https:// from image urls
        return re.sub('^http:', 'https:', url)

    @staticmethod
    def is_valid_card_dict(api_card_dict):
        primitive_keys = [
            'code', 'title', 'deck_limit', 'faction_code', 'pack_code', 'position', 'quantity', 'side_code',
            'type_code', 'uniqueness']
        for key in primitive_keys:
            if key not in api_card_dict:
                return False
        return True

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

    def get_card_image_url(self):
        # so we need to find the best image we can
        # first we'll check for a listed URL in the card itself, newer cards use this syntax
        if self.image_url is not None:
            if "https" in self.image_url:
                return self.image_url
        # else form the netrunnerdb image url
        # format the code from int to 0 back-filled string
        return "https://netrunnerdb.com/card_image/{:05}.png".format(self.code)

    def get_type_code_sort_val(self):
        return {'identity': 0, 'agenda': 1, 'asset': 2, 'upgrade': 3, 'operation': 4, 'ice': 5, 'event': 6,
                'hardware': 7, 'resource': 8, 'program': 9}[self.type_code]

    def search_card_match(self, search_criteria):
        """
        :param search_criteria: should be a list of dictionary keys pointing to a list of matching criteria
         [{'title': [Noise, Reina]}, {'base_link': [1]}]
        :return:
        """
        for criteria in search_criteria:
            criteria_passed = False
            # first sanitize that the key is in this object
            search_key = list(criteria.keys())[0]
            if search_key in self.__dict__:
                # if this card doesn't have a value for this key, it must not match
                if self.__dict__[search_key] is None:
                    # print("didn't find key '{}' in card".format(search_key))
                    return False
                # if this card does have this key, if none of the values we're looking for match, it's not a match
                clean_match_values = list()
                clean_card_values = list()
                for match_value in criteria[search_key]:
                    clean_match_values.append(self.clean_api_value_for_compare(match_value))
                # some card values are lists, if so, we're checking our criteria is in the set, not exact matches
                if type(self.__dict__[search_key]) == list:
                    for card_value in self.__dict__[search_key]:
                        clean_card_values.append(self.clean_api_value_for_compare(card_value))
                    # each criteria in the match_value must exist in this card
                    criteria_passed = True
                    for clean_match_value in clean_match_values:
                        if clean_match_value not in clean_card_values:
                            criteria_passed = False
                # if the card's field's type is not a list, we want the single criteria to be met or in the value
                else:
                    card_val = self.clean_api_value_for_compare(self.__dict__[search_key])
                    # each of our criteria must be met by the single value
                    criteria_passed = True
                    for clean_match_value in clean_match_values:
                        if type(clean_match_value) is int and type(card_val) is int:
                            if clean_match_value != card_val:
                                criteria_passed = False
                        else:
                            if clean_match_value not in card_val:
                                # the values matched, so move on to the next criteria
                                criteria_passed = False
            # failed to match on one of the criteria, so it's not a match
            if not criteria_passed:
                return False
        return True

    def render_text(self, render_option):
        """
        :param render_option: options class with our settings for this card
        :return: string with formatted fields requested from this card
        """
        description = ""
        # build the description of the card
        # we have a card, so let's add the default type fields, if any by type
        print_fields = list()
        print_fields += self.default_print_fields
        # next any additional fields specified by the search criteria
        for field in render_option.print_fields:
            if field not in print_fields:
                print_fields.append(field)
        # now add the fields that are relevant based on card type
        if self.type_code in self.extra_type_fields:
            for extra_field in self.extra_type_fields[self.type_code]:
                if extra_field not in render_option.print_fields:
                    print_fields.append(extra_field)
        if render_option.debug:
            render_option.print_fields = self.all_print_fields
        # if we selected to only list the tile, skip the rest of the fields
        if render_option.title_only:
            if 'title' in self.__dict__:
                description += self.transform_api_field_to_printable_format('title')
        # render the text from this class's nrdb_api_text transformer
        else:
            for field in print_fields:
                if field in self.__dict__:
                    description += self.transform_api_field_to_printable_format(field)
        return description

    def render_embed(self, render_option):
        """
        :param render_option: options class with our settings for this card
        :return: discord.Embed object built to display this one card
        """
        # maybe don't always embed with title?
        embed_response = discord.Embed(title="[{}]".format(self.title), type="rich")
        image_url = self.get_card_image_url()
        if self.faction_code in self.faction_color:
            embed_response.colour = self.faction_color[self.faction_code]
        if image_url is not None:
            embed_response.set_image(url=image_url)
        if not render_option.image_only:
            embed_response.description = "{}".format(self.render_text(render_option))
        if render_option.debug:
            embed_response.description += self.get_card_image_url()
        return embed_response


class RenderOptions:
    def __init__(self):
        self.debug = False
        self.title_only = False
        self.image_only = False
        self.print_fields = list()

    def to_string(self):
        return "debug: '{}'\ntitle_only: '{}'\nimage_only: '{}'\nprint_fields: '{}'\n".format(
            self.debug, self.title_only, self.image_only, self.print_fields)


class NetrunQuiz(MsgListener):
    ANSWER_TRANSFORMS = {
        "neutral-runner": "neutral",
        "neutral-corp": "neutral",
        "weyland-consortium": "weyland",
        "haas-bioroid": "hb",
        "identity": "id"
    }
    INVALID_CATEGORIES = ["code", "deck_limit", "flavor", "pack_code", "position",
                          "quantity", "side_code", "title", "illustrator", "text",
                          "keywords", "uniqueness"]
    MODE_ONESHOT = 0
    MODE_ROUNDS = 1
    MODE_FPTP = 2

    def __init__(self, bot, channel, nr_api, key_transforms, mode, rounds=1, timetowait=5):
        super().__init__()
        self.bot = bot
        self.api = nr_api
        self.card = None
        self.answer = ""
        self.has_answered = {}
        self.scores = {}
        self.attach(channel.id)
        self.mode = mode
        self.rounds = rounds
        self.rounds_played = 0
        self.key_transforms = key_transforms
        self.q_category = None
        self.timetowait = timetowait
        self.sleeping = False

    def create_question(self):
        """Create a question to be answered"""
        self.card = random.choice(self.api)
        # Check to make sure we pick an OK category to ask
        usable_categories = list(self.card.keys())
        usable_categories = [cat for cat in usable_categories if cat not in self.INVALID_CATEGORIES]
        usable_categories = [cat for cat in usable_categories if self.card[cat] != "null" and self.card[cat] != "None"]
        self.q_category = random.choice(usable_categories)
        self.answer = self.card[self.q_category]
        if self.answer in self.ANSWER_TRANSFORMS.keys():
            self.answer = self.ANSWER_TRANSFORMS[self.answer]

    async def ask_question(self, channel):
        """Ask the question"""
        if self.q_category in self.key_transforms:
            question = self.key_transforms[self.q_category]
        else:
            question = self.q_category
        await self.bot.send_message(channel,
                                    "What **{0}** is: *{1}*?".format(question, self.card["title"]))

    async def on_message(self, msg):
        """Handle people's responses"""
        if not self.sleeping and msg.author.id not in self.has_answered:
            self.has_answered[msg.author.id] = 1
            if msg.content.lower() == str(self.answer):
                await self.bot.add_reaction(msg, u"\U0001F3C6")
                await self.bot.send_message(msg.channel,
                                            msg.author.name + " got it!\n")
                if msg.author.name in self.scores:
                    self.scores[msg.author.name] += 1
                else:
                    self.scores[msg.author.name] = 1
                await self.end_round(msg.channel)
            else:
                await self.bot.add_reaction(msg, u"\U0001F6AB")
        if msg.content.lower() == "!end":
            await self.bot.send_message(msg.channel, "Ending the Fun...")
            await self.end_game(msg.channel, print_scores=True)
        elif msg.content.lower() == "!skip":
            await self.bot.send_message(msg.channel, "Skipping the round...")
            await self.end_round(msg.channel)

    def is_over(self):
        """Returns True if the game should be over, False otherwise"""
        if self.mode == self.MODE_ONESHOT:
            return True
        if self.mode == self.MODE_FPTP:
            for player in self.scores:
                if self.scores[player] >= self.rounds:
                    return True
            return False
        if self.mode == self.MODE_ROUNDS:
            if self.rounds_played >= self.rounds:
                return True
            return False
        return True

    async def print_scores(self, channel):
        """Print player scores to the given channel"""
        scores = [[player, self.scores[player]] for player in self.scores]
        scores = sorted(scores, key=lambda z: z[1], reverse=True)
        printable = tabulate(scores, headers=["Player", "Score"])
        printable = "```\n" + printable + "\n```"
        await self.bot.send_message(channel, printable)

    async def end_game(self, channel, print_scores=False):
        """End the game"""
        if print_scores:
            await self.print_scores(channel)
        self.detach(channel.id)

    async def end_round(self, channel):
        """End the current question"""
        await self.bot.send_message(channel, "It was: " + str(self.answer))
        self.has_answered = {}
        self.rounds_played += 1
        if self.is_over():
            await self.end_game(channel, print_scores=True)
        else:
            self.sleeping = True
            await asyncio.sleep(self.timetowait)
            # Try to end race condition here
            if self.sleeping:
                self.sleeping = False
                self.create_question()
                await self.ask_question(channel)


class Netrunner:
    """Netrunner related commands"""

    def __init__(self, bot):
        self.bot = bot
        self.nr_api = [{}]
        self.card_list = list()
        self.init_api = False
        self.max_message_len = 1990
        self.nets_help = "!nets command syntax:!nets --help or -h for flags listing\n"
        self.api_keys = "list of keys: (not all cards have all keys!)\n```title, text, cost, strength, " \
                        "keywords, type_code,\nuniqueness, faction_cost, memory_cost, trash_cost, advancement_cost," \
                        " agenda_points,\nside_code, faction_code, pack_code, position, quantity, \n" \
                        "base_link, influence_limit, deck_limit, minimum_deck_size,  flavor, illustrator, code```"
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
        self.union_keys = ["pack_code"]
        self.default_print_fields = [
            'uniqueness', 'base_link', 'title', 'cost', 'type_code', 'keywords', 'text', 'strength', 'trash_cost',
            'faction_code', 'faction_cost', 'legality']
        # 2 decimal prefix: Any prefix except core2.0 + three decimal suffix
        self.legacy_legal_code_regex = "((00)|(01)|(02)|(03)|(04)|(05)|(06)|(07)|(08)|(09)|(10)|(11)|(12)|(13))(\d\d\d)"
        # 2 decimal prefix:  C&C | H&P | O&C | D&D | TD | Flashpoint | Red Sand | Core2.0 + three decimal suffix
        self.cache_refresh_legal_code_regex = "((03)|(05)|(07)|(09)|(13)|(11)|(12)|(20))(\d\d\d)"
        # 2 decimal prefix:  C&C | H&P | Lunar| O&C | SanSan | D&D | Mumbad | Flashpoint | Red Sand | TD |
        # Core2.0 + three decimal suffix
        self.rotation_legal_code_regex = "((03)|(05)|(06)|(07)|(08)|(09)|(10)|(11)|(12)|(13)|(20))(\d\d\d)"
        self.search_legality_regex = self.rotation_legal_code_regex  # We'll support rotation, legacy, cr
        self.nr_api_url_template = ""
        self.nr_api_last_updated = ""
        self.nr_api_version_number = ""
        self.nr_api_total = 0
        self.max_card_search = 10

    def refresh_nr_api(self):
        nr_api_all = requests.get('https://netrunnerdb.com/api/2.0/public/cards').json()
        if nr_api_all['success']:
            self.nr_api_version_number = nr_api_all['version_number']
            self.nr_api_url_template = nr_api_all['imageUrlTemplate']
            self.nr_api_total = nr_api_all['total']
            self.nr_api_last_updated = nr_api_all['last_updated']
            self.nr_api = sorted([c for c in nr_api_all['data']], key=lambda card: card['code'])
            self.init_api = True
        self.build_card_list()

    def build_card_list(self):
        if not self.init_api:
            self.refresh_nr_api()
        for api_card_dict in self.nr_api:
            if NetrunnerDBCard.is_valid_card_dict(api_card_dict):
                self.card_list.append(NetrunnerDBCard(api_card_dict))

    def flag_parse(self, string_to_parse):
        """
        :param string_to_parse: take in the cmd input from one of the netrunner search functions
        :return: tuple with (search_criteria, display_configuration, error_string)
        """
        error_string = ""
        render_option = RenderOptions()
        # search_criteria_list is supposed to form data struct like [{'title': (Noise, Reina)}, {'base_link': (1)}]
        search_criteria_list = list()
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
        single_categories = [
            'type_code', 'faction_code', 'side_code', 'cost', 'advancement_cost', 'memory_cost', 'faction_cost',
            'strength', 'agenda_points', 'base_link', 'deck_limit', 'minimum_deck_size', 'code', 'trash_cost', 'unique',
            'pack_code', 'legality']
        nets_parser.add_argument('-t', '--type', action='store', dest="type_code")
        nets_parser.add_argument('-f', '--faction', action='store', dest="faction_code")
        nets_parser.add_argument('-d', '--side', action='store', dest="side_code")
        nets_parser.add_argument('-e', '--set', action='store', dest="pack_code")
        nets_parser.add_argument('--nrdb_code', action='store', dest="code", type=int)
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
        nets_parser.add_argument('-c', '--legality', action='store', dest="legality", default="rotation",
                                 help="Pick among legality subsets: rotation | legacy | cr")
        # special flags
        nets_parser.add_argument('--title-only', action='store_true', dest="title-only")
        nets_parser.add_argument('--image-only', action='store_true', dest="image-only")
        nets_parser.add_argument('--debug-flags', action='store_true', dest="debug-flags")
        try:
            # use the python module to turn the cmd string into a dictionary of card search criteria and print design
            args = nets_parser.parse_args(string_to_parse.split())
            parser_dictionary = vars(args)
            # run through each key that we need to build up a list of words to check for exact existence,
            # and add them to the list, if they're in the args
            for key in parser_dictionary.keys():
                if type(key) == list:
                    error_string += "found a key '{}' which was a list()???\n"
                    continue
                # first build up the parameters that need to be concatenated
                # entries in concat_category look like key: [['string], ['string']]
                if key in concat_categories:
                    if parser_dictionary[key] is not None:
                        # search parameters come in key: [['string'], ['other', 'string']
                        # for an input like: --flag string --flag other string
                        # we'll treat each --flag {value} as a separate criteria that must be met, and join the
                        # 'other' 'string' into a match 'other string' exactly.
                        concat_list = list()
                        for word_list in parser_dictionary[key]:
                            concat_list += word_list[:]
                        # if key in "title":
                        #    concat_string = self.apply_title_transform_jokes(concat_string.strip())
                        search_criteria_list.append({key: concat_list})
                        # Add the key to the printed result, if it's not already included
                        if key not in self.default_print_fields and key not in render_option.print_fields:
                            render_option.print_fields.append(key)
                # then check the lists that are done with single value:
                # looks like this: {'str': 5}
                if key in single_categories:
                    if parser_dictionary[key] is not None:
                        value_list = list()
                        value_list.append(parser_dictionary[key])
                        search_criteria_list.append({key: value_list})
                        if key not in self.default_print_fields and key not in render_option.print_fields:
                            render_option.print_fields.append(key)
            # form print/display options
            render_option.title_only = parser_dictionary['title-only']
            render_option.image_only = parser_dictionary['image-only']
            render_option.debug = parser_dictionary['debug-flags']
            if parser_dictionary['debug-flags']:
                error_string += "\noriginal args = '{}'\n".format(parser_dictionary)
                error_string += "\nsearch_criteria_list = '{}'\n".format(search_criteria_list)
                error_string += "\nrender_option = '{}'\n".format(render_option.to_string())
        except DiscordArgparseParseError as dape:
            if dape.value is not None:
                error_string += dape.value
            if nets_parser.exit_message is not None:
                error_string += nets_parser.exit_message
            if len(error_string) >= self.max_message_len:
                # truncate message if it exceed the character limit
                error_string = error_string[:self.max_message_len - 10] + "\ncont..."
        return search_criteria_list, render_option, error_string

    def rich_embed_deck_parse(self, deck_id):
        deck_list = dict()
        m_api_prefex = "https://netrunnerdb.com/api/2.0/public/decklist/"
        if not self.init_api:
            self.refresh_nr_api()
        try:
            decklist_data = [c for c in requests.get(m_api_prefex + deck_id).json()['data']]
            # decklist_data[0]['cards'] is a dict with card_id keys to counts {'10005': 1}
            e_response = discord.Embed(title=decklist_data[0]['name'], type="rich")
            # build a list of tuples in the pairs, value(number of card), key (id of card)
            for count, card_id in [(v, k) for (k, v) in decklist_data[0]['cards'].items()]:
                search_criteria = [{'code': int(card_id)}]
                card_list = self.search_card(self.card_list, search_criteria)
                # if more than one card matches somehow, we'll pick the last one
                deck_list[card_list[-1]] = count
            card_sort_list = self.sort_cards(deck_list)
            # for each card, now sorted by type, we'll create a new field, and add all cards from the list
            type_section = ""
            last_type = ""
            # grab the deck ID, and use its colour as the embed color
            deck_id = card_sort_list.get(0)
            e_response.colour = deck_id.faction_color[deck_id.type_code]
            for card, count in card_sort_list.items():
                # if this is the first card of its type, we'll print the previous cards as a new section
                if card.type_code not in last_type:
                    # skip empty sections
                    if last_type and type_section:
                        e_response.add_field(name=last_type.upper(), value=type_section, inline=False)
                    type_section = ""
                # add this card's title and count
                type_section += "{}x {}\n".format(count, card.title)
                last_type = card.type_code
            return e_response
        except JSONDecodeError as badUrlError:
            error_embed = discord.Embed(title="badUrlError", type="rich")
            error_embed.description = badUrlError.msg
            return error_embed

    async def find_and_say_card(self, string_to_parse, use_embed=True):
        if not self.init_api:
            self.refresh_nr_api()
        search_criteria_list, render_option, error_string = self.flag_parse(string_to_parse)
        num_matches = 0
        for card in self.card_list:
            if card.search_card_match(search_criteria_list):
                num_matches += 1
                if num_matches > self.max_card_search:
                    continue
                time.sleep(0.5)
                if use_embed:
                    await self.bot.say(embed=card.render_embed(render_option))
                else:
                    await self.bot.say(card.render_text(render_option))
        if error_string:
            time.sleep(0.5)
            await self.bot.say("I saw these errors: '{}'".format(error_string))
        # TODO It'd be nice to calculate the pool of cards by legality that we searched...
        time.sleep(0.5)
        await self.bot.say("listed {} of {} matched cards (total {})".format(
            min(num_matches, self.max_card_search, ), num_matches, len(self.card_list)))

    @commands.command(name="flag_nets", aliases=['nets'])
    async def arg_parse_nets(self, *, string_to_parse: str):
        await self.find_and_say_card(string_to_parse, use_embed=True)

    @commands.command(name="flag_nets_cr", aliases=['netscr'])
    async def arg_parse_nets_cr(self, *, string_to_parse: str):
        await self.find_and_say_card(string_to_parse + " --legality cr ", use_embed=True)

    @commands.command(name="flag_nets_legacy", aliases=['netslegacy'])
    async def arg_parse_nets_legacy(self, *, string_to_parse: str):
        await self.find_and_say_card(string_to_parse + " --legality legacy ", use_embed=True)

    @commands.command(aliases=['nr', 'netrunner'])
    async def nr_flags(self, *, string_to_parse: str):
        await self.find_and_say_card(string_to_parse + " --image-only ", use_embed=True)

    @commands.command(aliases=['nrcr', 'cache_refresh'])
    async def cr_flags(self, *, string_to_parse: str):
        await self.find_and_say_card(string_to_parse + " --image-only --legality cr ", use_embed=True)

    @commands.command(aliases=['nrleg', 'nr_legacy'])
    async def legacy_flags(self, *, string_to_parse: str):
        await self.find_and_say_card(string_to_parse + " --image-only --legality legacy ", use_embed=True)

    @commands.command(aliases=['broke'])
    async def nr_debug(self, *, cmd: str):
        await self.bot.say("debug print, the arguments were '{}'".format(cmd))
        search_criteria_list, render_option, error_string = self.flag_parse(cmd)
        for card in self.card_list:
            if card.search_card_match(search_criteria_list):
                await self.bot.say("debug print, card is '{}', url is '{}'".format(
                    card.code, card.get_card_image_url()))

    @commands.command(aliases=['nd'])
    async def deck(self, *, decklist: str):
        m_response = ""
        m_decklist = unidecode(decklist.lower())
        re_decklist_id = re.search("(https://netrunnerdb\.com/en/decklist/)(\d+)(/.*)", m_decklist)
        if re_decklist_id is None or re_decklist_id.group(2) is None:
            m_response += "I see: \"{0}\", but I don't understand\n".format(m_decklist)
        else:
            # m_response += self.deck_parse(re_decklist_id.group(2))
            e_response = self.rich_embed_deck_parse(re_decklist_id.group(2))
            await self.bot.say(embed=e_response)
        if len(m_response) > 0:
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
        m_response += self.rich_embed_deck_parse(id)
        await self.bot.say(m_response[:2000])

    @commands.command(pass_context=True)
    async def quiz(self, ctx):
        quiz_opts = DiscordArgParse(prog='!quiz')
        quiz_opts.add_argument('--spoiler', '-s', action='store_true', dest="spoiler")
        quiz_opts.add_argument('--rounds', '-r', action='store', type=int, dest="rounds")
        quiz_opts.add_argument('--fptp', '-f', action='store', type=int, dest="points")
        quiz_opts.add_argument('--waittime', '-wt', action='store', type=int, dest="waittime", default=5)
        try:
            # Arg parsing
            flags = ctx.message.content.split()
            if len(flags) > 1:
                flags = flags[1:]
            else:
                flags = []
            args = quiz_opts.parse_args(flags)
            args_dict = vars(args)
            num_rounds = 1
            mode = NetrunQuiz.MODE_ONESHOT
            if args_dict["rounds"]:
                if args_dict["points"]:
                    await self.bot.say("You can't have both rounds and fptp set!")
                    return
                num_rounds = args_dict["rounds"]
                mode = NetrunQuiz.MODE_ROUNDS
            elif args_dict["points"]:
                num_rounds = args_dict["points"]
                mode = NetrunQuiz.MODE_FPTP

            # Create the quiz
            if not self.init_api:
                self.refresh_nr_api()
            quiz = NetrunQuiz(self.bot, ctx.message.channel, self.nr_api,
                              self.key_transforms, mode, num_rounds, args_dict["waittime"])
            quiz.create_question()
            await quiz.ask_question(ctx.message.channel)
        except DiscordArgparseParseError as se:
            if se.value is not None:
                await self.bot.say(se.value)
            if quiz_opts.exit_message is not None:
                await self.bot.say(quiz_opts.exit_message)

    @staticmethod
    def apply_title_transform_jokes(card_title_criteria):
        # Auto-correct some card names (and inside jokes)
        query_corrections = {
            "smc": "self-modifying code",
            "jesus": "jackson howard",
            "neh": "near earth hub",
            "sot": "same old thing",
            "tilde": "blackat",
            "neko": "blackat",
            "<:stoned:259424190111678464>": "mr. Stone",
            "<:dan:302195700136148994>": "deuces wild",
            "<:snare:230408123079196672>": "snare",
            "<:abomb:269152319004868610>": "emp device",
            "<:moonman:249217069185368064>": "shoot the moon",
        }
        if card_title_criteria.lower() in query_corrections.keys():
            card_title_criteria = query_corrections[card_title_criteria.lower()]
        return card_title_criteria

    @staticmethod
    def apply_title_redirect_jokes(card_title_criteria):
        # Auto-link some images instead of other users' names
        query_redirects = {
            "nyan": "http://i.imgur.com/TnwGEhG.jpg",  # http://i.imgur.com/AtqdQiP.jpg
            "ordineu": "http://i.imgur.com/PDySfQ7.png",
            "kika": "http://i.imgur.com/WnsNJho.jpg",
            "leg": "http://i.imgur.com/53dBofH.png",
            "triffids": "http://run4games.com/wp-content/gallery/altcard_runner_id_shaper/Nasir-by-stentorr-001.jpg",
            "dee": "http://i.imgur.com/vrQmmOf.png",
            "garvin": "http://i.imgur.com/KtvboU8.jpg",
            "cyberface": "http://i.imgur.com/cV7EAtx.png",
        }
        if card_title_criteria.lower() in query_redirects.keys():
            return query_redirects[card_title_criteria.lower()]
        else:
            return None

    @staticmethod
    def search_card(card_list, search_criteria):
        """
        :param card_list: take in a list of card obj to search for a subset of
        :param search_criteria: criteria by which we subset the card
        :return: list(NetrunnerDBCard)
        """
        final_list = list()
        for card in card_list:
            if card.search_card_match(search_criteria):
                final_list.append(card)
        return final_list

    @staticmethod
    def sort_cards(cards):
        """
        :param cards: dict to be ordered
        :return: OrderedDict based on card order
        """
        deck_list0 = OrderedDict()
        deck_list1 = OrderedDict()
        # input should be a list of full card dictionaries to be sorted
        # first sort by title
        deck_list0 += sorted(cards.items(), key=lambda item: item[0].title)
        # I should pre-sort the cards by sub types, before adding them to type major sort
        # todo add that before this line.
        # next sort by type
        deck_list1 += sorted(deck_list0.items(), key=lambda item: item[0].get_type_code_sort_val())
        return deck_list1


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
