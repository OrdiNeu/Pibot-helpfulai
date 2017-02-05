# Skulls N Roses game for discord bot
### PREAMBLE ##################################################################
import random
import re

import discord
import requests

from discord.ext import commands

PLAYER_HAS_NO_SUCH_ANTE = -1
WRONG_PLAYER_RESPONDED = -2
BET_TOO_HIGH = -3
BET_TOO_LOW = -4
PLAYER_ALREADY_ANTED = -5
INIT_PHASE_OVER = -6
WRONG_GAME_PHASE = -7
NOT_ENOUGH_PLAYERS = -8
MAX_BET_OFFERED = -9

PHASE_WAITING = 0
PHASE_INITANTE = 1
PHASE_ANTEING = 2
PHASE_BETTING = 3
PHASE_FLIPPING = 4

class SkullsSession:
	"""One active skulls N roses game"""
	def __init__(self, initialplayer):
		self.players = []
		self.decks = {}
		self.piles = {}
		self.addPlayer(initialplayer)
		self.curPlayer = 0
		self.totalTiles = 0
		self.phase = PHASE_WAITING
		self.lastBet = 0
		self.lastBettingPlayer = ""
	
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
		try:
			position = int(position_str)
		except ValueError:
			return(PLAYER_HAS_NO_SUCH_ANTE)
		if len(self.decks[player.name]) >= position:
			return(PLAYER_HAS_NO_SUCH_ANTE)
		
		if self.phase == PHASE_ANTEING:			
			if self.players[self.curPlayer] != player:
				return(WRONG_PLAYER_RESPONDED)

			# Push the selected tile onto the pile
			selected = self.decks[player.name].pop(position)
			self.piles[player.name].append(selected)
			
			# Swap player
			self.curPlayer += 1
			self.curPlayer %= len(self.players)
			return(0)
		else if self.phase == PHASE_INITANTE:
			if len(self.piles[player.name]) > 0:
				return(PLAYER_ALREADY_ANTED)
				
			# Push the selected tile onto the pile
			selected = self.decks[player.name].pop(position)
			self.piles[player.name].append(selected)
			
			# Check if everyone has ante'd
			self.curPlayer += 1
			if self.curPlayer >= len(self.players):
				self.phase = PHASE_ANTEING
				return(INIT_PHASE_OVER)
		else:
			return(WRONG_GAME_PHASE)
	
	def playerBet(self, player, amount):
		"""Bet a certain amount"""
		if self.phase != PHASE_BETTING or \
			self.phase != PHASE_ANTEING:
			return(WRONG_GAME_PHASE)
		if self.players[self.curPlayer] != player:
			return(WRONG_PLAYER_RESPONDED)
		if int(amount) <= self.lastBet:
			return(BET_TOO_LOW)
		if int(amount) > self.totalTiles:
			return(BET_TOO_HIGH)
		
		self.lastBet = int(amount)
		self.lastBettingPlayer = player
		self.phase = PHASE_BETTING
		return(0)
	
	def startGame(self, player):
		"""Start the game, checking that the given player is first"""
		if self.players[0] != player:
			return(WRONG_PLAYER_RESPONDED)
		if len(self.players) < 2:
			return(NOT_ENOUGH_PLAYERS)
		self.phase = PHASE_INITANTE
		return(0)
	
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
	def getSkullWord(self):
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
			await self.bot.say("Sorry, only one game of Skulls N Roses can be initialized per channel.")
			return
		
		# Begin the  game
		self.activeGames[] = SkullsSession(author)
		await self.bot.say(
			author + " wants to play a round of Skulls 'N Roses!\n" + \
			"Please say !down if you would like to play.\n" + \
			author + " can say !start to begin the round."
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
		
		# Handle every possible return value
		retval = session.playerAnte(author, tile)
		if retval == PLAYER_HAS_NO_SUCH_ANTE:
			await self.bot.say(author + ": that is not a valid tile\n" + \
								"Your tiles have been DM'd to you")
			await self.remind(ctx)
		elif retval == WRONG_GAME_PHASE:
			await self.bot.say("No antes can be placed right now.")
		elif retval == WRONG_PLAYER_RESPONDED:
			await self.bot.say(author + ": it is not your turn.\n")
			await self.whoseturn(ctx)
		elif retval == PLAYER_ALREADY_ANTED:
			await self.bot.say("You have already laid your starting tile. Please wait for the rest of the players.")
		else:
			await self.bot.say(author + " has placed a tile.")
			if retval == INIT_PHASE_OVER:
				await self.bot.say("The game has begun!")
			elif session.phase == PHASE_ANTEING:
				await self.whoseturn(ctx)
	
	@commands.command(pass_context = True)
	async def bet(self, ctx, amount):
		"""Make a bet of how many you can flip in an active game"""
		game_name = self.getGameName(ctx.message)
		author = ctx.message.author.name
		
		# Do nothing if no game is active
		if game_name not in self.activeGames.keys():
			return
		
		session = self.activeGames[game_name]
		
		# Begin the betting phase
		retval = session.playerBet(amount)
		
		# Handle every possible retval
		if retval == WRONG_GAME_PHASE:
			await self.bot.say("You cannot bet now.")
		elif retval == WRONG_PLAYER_RESPONDED:
			await self.bot.say(author + ": it is not your turn.\n")
			await self.whoseturn()
		elif retval == BET_TOO_HIGH:
			await self.bot.say("There aren't that many tiles to flip.")
		elif retval == BET_TOO_LOW:
			await self.bot.say("You must bet more than the last bet of " + str(session.lastBet))
		elif retval == 0:
			await self.bot.say(author + " has bet " + amount + "!")
			await self.whoseturn(ctx)
		
	@commands.command(pass_context = True)
	async def start(self, ctx):
		game_name = self.getGameName(ctx.message)
		author = ctx.message.author.name
		
		# Do nothing if no game is active
		if game_name not in self.activeGames.keys():
			return
		
		session = self.activeGames[game_name]
		
		retval = session.startGame(author)
		
		if retval == NOT_ENOUGH_PLAYERS:
			await self.bot.say("Not enough players for a game!")
		elif retval == WRONG_PLAYER_RESPONDED:
			await self.bot.say("Only " + session.players[0] + " can !start the game.")
		elif retval == WRONG_GAME_PHASE:
			await self.bot.say("This game has already begun.")
		elif retval == 0:
			message = "The game has begun! The players are: "
			message += " ".join(session.players)
			message += "\n Your hands have been DM'd to you.\n"
			message += "Please use !bet (number) to place your first tile.\n"
			message += "The game will automatically progress once everyone has placed one."
			await self.bot.say(message)
			
			# Tell all players their hand
			for (player in session.players.keys):
				await self.remind(ctx, who = player)
	
	@commands.command(aliases = ['remindme'], pass_context = True)
	async def remind(self, ctx, who = ""):
		""" Remind a user what tiles they have """
		game_name = self.getGameName(ctx.message)
		author = ctx.message.author.name
		
		if game_name not in self.activeGames.keys():
			return
		
		session = self.activeGames[game_name]
		
		# Create the message that tells them what their tiles are
		message = "Your tiles are:\n"
		pile_idx = range(0, len(session.piles[author]))
		zipped_hand = zip(pile_idx, session.piles[author])
		message += "\n".join(str(i[0]) + ": " + i[1] for i in zipped_hand)
		await self.bot.send_message(ctx.author, message)
	
	@commands.command(aliases = ['whichplayer'], pass_context = True)
	async def whoseturn(self, ctx):
		"""Remind the room whose turn it is"""
		game_name = self.getGameName(ctx.message)
		author = ctx.message.author.name
		
		if game_name not in self.activeGames.keys():
			return
		
		session = self.activeGames[game_name]
		
		await self.bot.say("It is currently " + session.getCurPlayer + "'s turn.")
	
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
