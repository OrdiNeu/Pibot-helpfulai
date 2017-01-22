# Various helper functions for discord.py
# PREAMBLE ####################################################################
import discord
import asyncio

from discord.ext import commands

# Checks if a message came from the administrator
def is_admin_check(message):
	return "135449740778274816" == message.author.id

def is_admin():
    return commands.check(lambda ctx: is_admin_check(ctx.message))