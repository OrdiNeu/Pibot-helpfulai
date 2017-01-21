# Netrunner extension for pibot
### PREAMBLE ##################################################################
import re

import discord
import requests

from discord.ext import commands

class Arkham:
	"""Arkham Horror related commands"""
	
	def __init__(self, bot):
		self.bot = bot
		
	@commands.command(aliases=['arkham','arkhamhorror'])
	async def ah(self, ctx, *, member: discord.Member = None):
		"""Arkham Horror card lookup"""
		m_query = ctx.lower()
		
		# Auto-correct some card names (and inside jokes)
		query_corrections = {
			}
		if m_query in query_corrections.keys():
			m_query = query_corrections[m_query]
		
		# Auto-link some images instead of other users' names
		query_redirects = {
			}
		m_response = ""
		if m_query in query_redirects.keys():
			m_response = query_redirects[m_query]
		else:
			# Otherwise find and handle card names
			m_cards = [c for c in requests.get('https://arkhamdb.com/api/public/cards').json() if c['title'].lower().__contains__(m_query)]
			if len(m_cards) == 1:
				m_response = "http://arkhamdb.com/card_image/" + m_cards[0]['imagesrc'] + ".png"
			elif len(m_cards) == 0:
				m_response = "Sorry, I cannot seem to find any card with these parameters."
			else:
				m_response = "http://arkhamdb.com/find?q=" + m_query.replace (" ","+")
		await self.bot.say(m_response)


def setup(bot):
	bot.add_cog(Arkham(bot))
