# Various helper functions for discord.py
# PREAMBLE ####################################################################
import discord
import asyncio

from discord.ext import commands

# Checks if a message came from the administrator
def is_admin(message):
	return "135449740778274816" == message.author.id

def is_owner():
    return commands.check(lambda ctx: is_owner_check(ctx.message))