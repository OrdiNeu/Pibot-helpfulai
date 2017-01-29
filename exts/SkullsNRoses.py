# Skulls N Roses game for discord bot
### PREAMBLE ##################################################################
import re

import discord
import requests

from discord.ext import commands

activeGames = {}

class SkullsSession:
	"""One active skulls N roses game"""
	def __init__(self, initialplayer):
		self.players = []
		self.decks = {}
		self.addPlayer(initialplayer)
	
	def addPlayer(self, player):
		self.decks[player.name] = getDeck()
		self.players.append(player.name)
	
	def getDeck(self):
		return [
			self.getRoseWord(), 
			self.getRoseWord(), 
			self.getRoseWord(), 
			self.getSkullWord()
			]
	
	def getRoseWord(self):
		return("Rose")
	def getSKullWord(self):
		return("Skull")

class Skulls:
	"""SkullsNRoses related commands"""
	
	def __init__(self, bot):
		self.bot = bot
		
	@commands.command(aliases=['skullsnroses','skulls'], pass_context=True)
	async def snr(self, ctx):
		"""Begins a game of Skulls N Roses"""
		await self.bot.say(ctx.message.channel)


def setup(bot):
	bot.add_cog(Skulls(bot))
