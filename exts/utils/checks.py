# Various helper functions for discord.py
# PREAMBLE ####################################################################
import discord
import asyncio

from discord.ext import commands

# The keys below are the IDs of administrators permitted to run priveleged
# commands. The values are not important
admins = {
    "135449740778274816": "OrdiNeu",
    "136288437035597824": "Leg",
    "134012742146195458": "Destragon"
}

trusted = {
    "145389680341286912": "Dilron",
    "135471846471499776": "Kika",
    "134038407428046848": "Mush",
    "101120254352064512": "Nyan",
    "100994639418372096": "STEEV",
    "134396066454962177": "Triffids",
    "107181001922347008": "Yarrick",
    "65862180519550976": "Zigkirby",
    "149015142250708992": "TheHelpfulAI"
}

# Checks if a message came from the administrator
def is_admin_check(message):
    return str(message.author.id) in admins.keys()

def is_admin():
    return commands.check(lambda ctx: is_admin_check(ctx.message))

def is_trusted_check(message):
    return str(message.author.id) in trusted.keys() or is_admin_check(message)

def is_trusted():
    return commands.check(lambda ctx: is_trusted_check(ctx.message))
