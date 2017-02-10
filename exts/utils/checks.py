# Various helper functions for discord.py
# PREAMBLE ####################################################################
import discord
import asyncio

from discord.ext import commands

# The keys below are the IDs of administrators permitted to run priveleged
# commands. The values are not important
admins = {
    "135449740778274816": "OrdiNeu",
    "136288437035597824": "Leg"
}

# Checks if a message came from the administrator
def is_admin_check(message):
    return message.author.id in admins.keys()

def is_admin():
    return commands.check(lambda ctx: is_admin_check(ctx.message))