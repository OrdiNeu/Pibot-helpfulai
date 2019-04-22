# Netrunner extension for pibot
### PREAMBLE ##################################################################
import re
from unidecode import unidecode

import discord
import requests
# import emoji
# from json.decoder import JSONDecodeError
from discord.ext import commands
class Dungeonman(commands.Cog):
    """
    Thy Dungeonman! Thy hunger!
    """
    def __init__(self, bot):
        self.bot = bot
        self.max_message_len = 1990
        self.score = 0
        self.scroll_state = False
        self.flask_count = 0
        self.trinket_get = 0
        self.general_commands = {
            "HELP": "area_description",
            "LOOK": "area_description",
            "HELPETH": "area_description",
            "DIE": "That wasn't very smart. Your score was: \\1. "
                   "Play again? [Y/N]",
            # - Subtracts 100 points from your score.",
            "DANCE": "Thou shaketh it a little, and it feeleth all right.",
            "GET (YE|YON) (.*)": "interact",
            "YE (.*?) GET": "interact",
            "TAKE (YE|YON)? (.*)": "interact",
            "interact": "Thou cannotst get that. Quit making stuffeth up!",
            "GET DAGGER": "Yeah, okay.",
            # Adds 25 points to your score.
            # Usable infinitely.
            "GO (.*)": "Thou cannotst go there. Who do you think thou art? A magistrate?!",
            "LOOK (.*)": "It looketh pretty awesome.",
            "ELSE": "That does not computeth. Type HELP is thou needs of it.",
            "TALK (.*)": "Who is ___? Your new boyfriend? Somebody from work you don't want me to meeteth?",
            "GIVE (.*)": "Thou don'tst have a ___ to give. Go back to your tiny life.",
            "(SMELL|SNIFF)": "You smell a Wumpus."
        }
        self.prompt = "\n\nWhat wouldst thou deau?\n"
        self.main_dungeon_room_cmds = {
            "LOOK SCROLL": "Parchment, definitely parchment. I'd recognize it anywhere.",
            "LOOK FLASK": "Looks like you could quaff some serious mead out of that thing.",
            "GET SCROLL": "Ye takes the scroll and reads of it. It doth say: "
                          "BEWARE, READER OF THE SCROLL, DANGER AWAITS TO THE- "
                          "The SCROLL disappears in thy hands with ye olde ZAP!",
            # - Adds 2 points to your score
            "GET SCROLL2": "Ye doth suffer from memory loss. YE SCROLL is no more. Honestly.",
            # - Subtracts 1 point from your score
            "GET FLASK": "Ye cannot get the FLASK. It is firmly bolted to a wall which is bolted to the rest of "
                         "the dungeon which is probably bolted to a castle. Never you mind.",
            # - Adds 1 point to your score each time
            "GET FLASK3": "Okay, okay. You unbolt yon FLASK and hold it aloft. A great shaking begins. The dungeon "
                          "ceiling collapses down on you, crushing you in twain. Apparently, this was a "
                          "load-bearing FLASK. Your score was: \\1 Play again? [Y/N]",
            # - Subtracts 1000 points from your score
            "(GO)? (NORTH)": "North",
            "(GO)? (SOUTH)": "South",
            "(GO)? (DENNIS)": "Dennis",
        }
        self.north_cmds = {
            "LOOK PARAPETS": "Well, they're parapets. This much we know for sure.",
            "LOOK ROPE": "It looks okay. You've seen better.",
            "GET ROPE": "You attempt to take ye ROPE but alas it is enchanted! It glows a mustard red and smells "
                        "like a public privy. The ROPE wraps round your neck and hangs you from parapets. "
                        "With your last breath, you wonder what parapets are. "
                        "GAME OVER. Your score was:\\1. Play again? (Y/N)",
            # - Subtracts 1 point from your score
            "(GO)? SOUTH": "move",
        }
        self.south_cmds = {
            "LOOK TRINKET": "Quit looking! Just get it already.",
            "(LOOK|HELP) ": "Ye stand yeself close to a yet-unnamed escarpment. "
                            "Nonetheless, ye spies a TRINKET. Obvious exits are NORTH.",
            # Before GET TRINKET
            "GET TRINKET": "Ye getsts yon TRINKET and discover it to be a bauble. You rejoice at your good fortune. "
                           "You shove the TRINKET in your pouchel. It kinda hurts.",  # Adds 2 points to your score
            "(LOOK|HELP)2": "Ye stand high above a canyon-like depression. Obvious exits are NORTH.",
            # After GET TRINKET
            "LOOK TRINKET2": "Just a bulge in thou pouchel at thist point.",
            # (After you GET it)
            "GET TRINKET2": "Sigh. The trinket is in thou pouchel. Recallest thou?",
            # (After you GET it)- Subtracts 1 point from your score
            "(LOOK|HELP)3": "Thou hangeth out at an overlook. Obvious exits are NORTH. "
                            "I shouldn't have to tell ye there is no TRINKET.",
            # (After you try to GET TRINKET more than once)
            "NORTH": "move"
        }
        self.dennis_cmds = {
            "NOT DENNIS": "move",
            "TALK": "You engage Dennis in leisurely discussion. Ye learns that his jimberjam was purchased on sale "
                    "at a discount market and that he enjoys pacing about nervously. "
                    "You become bored and begin thinking about parapets.",
            "LOOK DENNIS": "That jimberjam really makes the outfit.",
            "LOOK JIMBERJAM": "Man, that art a nice jimberjam.",
            "GIVE TRINKET (TO)? (DENNIS)?": "A novel idea! You givst the TRINKET to Dennis and he happily agrees to "
                                            "tell you what parapets are. With this new knowledge, ye escapes from yon "
                                            "dungeon in order to search for new dungeons and to remain... "
                                            "THY DUNGEONMAN!! You hath won! Congraturation!! Your score was: (\\1)",
            "GIVE TRINKET1": "Thou don'tst have a trinket to give. Go back to your tiny life.",
            # (without actually having the TRINKET)
        }
        self.current_room = "Start Game"
        self.rooms = {
            "Main Dungeon Room": "Ye find yeself in yon dungeon. Ye see a SCROLL. Behind ye scroll is a FLASK. "
                                 "Obvious exits are NORTH, SOUTH and DENNIS.\n",
            "North": "You go NORTH through yon corridor. You arrive at parapets. Ye see a ROPE. "
                     "Obvious exits are SOUTH.\n",
            "South": "You head south to an enbankment. Or maybe a chasm. You can't decide which.\n"
                     "Anyway, ye spies a TRINKET. Obvious exits are NORTH.\n",
            "Dennis": "Ye arrive at Dennis. He wears a sporty frock coat and a long jimberjam."
                      "He paces about nervously. Obvious exits are NOT DENNIS.\n",
            "Start Game": "THY DUNGEONMAN\n\nYOU ARE THY DUNGEONMAN!\n\n"
        }
    def game_over(self):
        """
        print score, reset variables
        :return:
        """
        self.score = 0
        self.current_room = "Start Game"
    def parse_cmd(self, cmd):
        m_response = ""
        if self.current_room in "Start Game":
            m_response += self.rooms[self.current_room]
            self.current_room = "Main Dungeon Room"
            m_response += self.rooms[self.current_room]
        else:
            # pre parse the cmd, then post-parse into actions
            if(self.current_room in "Main Dungeon Room"):
                for rgx, val in self.main_dungeon_room_cmds.items():
                    search = re.search(rgx, cmd)
                    if search is not None:
                        if val in "North":
                            self.current_room = "North"
                        elif val in "South":
                            self.current_room = "South"
                        elif val in "Dennis":
                            self.current_room = "Dennis"
                        else:

        m_response += self.prompt
        return m_response
    def debug(self, cmd):
        m_response = self.parse_cmd(cmd)
        if len(m_response) >= self.max_message_len:
            # truncate message if it exceed the character limit
            m_response = m_response[:self.max_message_len - 10] + "\ncont..."
        print(m_response)
    @commands.command(name="dm", aliases=['thy'])
    async def thy(self, *, command: str):
        """
        !thy Dungeonman! :
        !thy HELP!
        """
        m_response = ""
        if len(m_response) >= self.max_message_len:
            # truncate message if it exceed the character limit
            m_response = m_response[:self.max_message_len - 10] + "\ncont..."
        await self.bot.say(m_response)
