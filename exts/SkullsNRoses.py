# Skulls N Roses game for discord bot
### PREAMBLE ##################################################################
import random
import re

import discord
import requests

from discord.ext import commands

PLAYER_HAS_NO_SUCH_ANTE = -1
WRONG_PLAYER_RESPONDED = -2

PHASE_WAITING = 0
PHASE_INITANTE = 1
PHASE_ANTEING = 2
PHASE_BETTING = 3

class SkullsSession:
	"""One active skulls N roses game"""
	def __init__(self, initialplayer):
		self.players = []
		self.decks = {}
		self.piles = {}
		self.addPlayer(initialplayer)
		self.curPlayer = 0
		self.phase = PHASE_WAITING
	
	def addPlayer(self, player):
		"""Add a player to the game"""
		self.decks[player.name] = self.getDefaultHand()
		random.shuffle(self.decks[player.name])
		self.players.append(player.name)
		self.piles[player.name] = []
		
	def playerAnte(self, player, position_str):
		"""Place a player's tile down, and swap players"""
		position = 0
		
		# Sanity checks
		if self.players[self.curPlayer] != player:
			return(WRONG_PLAYER_RESPONDED)
		try:
			position = int(position_str)
		except ValueError:
			return(PLAYER_HAS_NO_SUCH_ANTE)
		if len(self.decks[player.name]) >= position:
			return(PLAYER_HAS_NO_SUCH_ANTE)
		
		# Push the selected tile onto the pile
		selected = self.decks[player.name].pop(position)
		self.piles[player.name].append(selected)
		
		# Swap player
		self.curPlayer += 1
		self.curPlayer %= len(self.players)
		return(0)
	
	def playerBet(self, player, amount):
		"""Bet a certain amount"""
		if (self)
	
	def getDefaultHand(self):
		"""Return a starting hand for the player"""
		return [
			self.getRoseWord(),
			self.getRoseWord(),
			self.getRoseWord(),
			self.getSkullWord()
			]
	
	def getCurPlayer(self):
		return self.players[self.curPlayer]
	def getRoseWord(self):
		return("Rose")
	def getSKullWord(self):
		return("Skull")

class Skulls:
	"""SkullsNRoses related commands"""
	
	def __init__(self, bot):
		### TODO: Grab a ref to the client so we can send DMs
		self.bot = bot
		self.activeGames = {}
		
	def getGameName(self, message):
		return message.server + "#" + message.channel
	
	@commands.command(aliases = ['skullsnroses','skulls'], pass_context = True)
	async def snr(self, ctx):
		"""Begins a game of Skulls N Roses"""
		game_name = self.getGameName(ctx.message)
		author = ctx.message.author.name
		
		# Prevent two games going on in one channel
		if game_name in self.activeGames.keys():
			await self.bot.say("Sorry, only one game of Skulls N Roses can be initialized per channel")
			return
		
		# Begin the  game
		self.activeGames[] = SkullsSession(author)
		await self.bot.say(
			author + " wants to play a round of Skulls 'N Roses!\n" + \
			"Please say !down if you would like to play\n" + \
			author + " can say !start to begin the round"
			)
	
	@commands.command(pass_context = True)
	async def ante(self, ctx, tile : str):
		"""Play a tile from hand in an active game"""
		game_name = self.getGameName(ctx.message)
		author = ctx.message.author.name
		
		# Do nothing if no game is active
		if game_name not in self.activeGames.keys():
			return
		
		session = self.activeGames[game_name]
		
		# Make sure it is currently in the anteing round
		if session.phase == PHASE_BETTING:
			await self.bot.say(author + ": We are currently in the betting around: no more antes can be placed.")
			return
		
		# Make sure the active player is playing
		if author != session.getCurPlayer:
			await self.bot.say(author + ": it is not your turn.\n" + \
								"It is currently " + session.getCurPlayer + "'s turn.")
			return
	
		if session.playerAnte(author, tile) == PLAYER_HAS_NO_SUCH_ANTE:# TODO: fix this line
			await self.bot.say(author + ": that is not a valid tile\n" + \
								"Your tiles have been DM'd to you")
			await self.remind(ctx)
			return
	
		# Player ante success -- go to next player
		await self.bot.say(author + " has placed a tile. It is now " + session.getCurPlayer + "'s turn")
	
	@commands.command(pass_context = True)
	async def bet(self, ctx):
		game_name = self.getGameName(ctx.message)
		author = ctx.message.author.name
		
		# Do nothing if no game is active
		if game_name not in self.activeGames.keys():
			return
		
		session = self.activeGames[game_name]
		
		# Begin the betting phase
		session.phase = PHASE_INITANTE
		
		# Do more stuff
		
	@commands.command(pass_context = True)
	async def start(self, ctx):
		game_name = self.getGameName(ctx.message)
		author = ctx.message.author.name
		
		# Do nothing if no game is active
		if game_name not in self.activeGames.keys():
			return
		
		session = self.activeGames[game_name]
		
		# Begin the game
		session.phase = PHASE_ANTEING
		
		message = "The game has begun! The players are: "
		message += " ".join(session.players)
		
		await self.bot.say(message)
	
	@commands.command(pass_context = True)
	async def remind(self, ctx):
		""" Remind a user what tiles they have """
		game_name = self.getGameName(ctx.message)
		author = ctx.message.author.name
		
		if game_name not in self.activeGames.keys():
			return
		
		session = self.activeGames[game_name]
		
		message = "Your tiles are: "
		pile_idx = range(0, len(session.piles[author]))
		zipped_hand = zip(pile_idx, session.piles[author])
		message += "\n".join(str(i[0]) + ": " + i[1] for i in zipped_hand)
		await self.bot.send_message(ctx.author, message)
	
	@commands.command(pass_context = True)
	async def down(self, ctx):
		# Add a player to the current game
		game_name = self.getGameName(ctx.message)
		author = ctx.message.author.name
		
		# Do nothing if no game is active
		if game_name not in self.activeGames.keys():
			return
		
		session = self.activeGames[game_name]
		await self.bot.say(author + " has been added to the game!\n")

def setup(bot):
	bot.add_cog(Skulls(bot))
