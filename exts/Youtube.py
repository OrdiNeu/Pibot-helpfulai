# youtube video-finding extension for pibot
### PREAMBLE ##################################################################
import datetime
import httplib2
import os
import re
import sys
from unidecode import unidecode

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

import discord
from discord.ext import commands
import requests
import random

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets

CLIENT_SECRETS_FILE = "client_secrets.json"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the {{ Cloud Console }}
{{ https://cloud.google.com/console }}

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))



class Youtube_Lookup:
    """youtube generating related commands"""

    def __init__(self, bot):
        self.bot = bot
        self.leg_api_key = "AIzaSyBDgSAyyKh1Fak5XFxmRVumT8p6mTxJJW8"
        self.client_secrets_file = "client_secrets.json"

    @commands.command(pass_context = True)
    async def fortune(self, ctx):
        """Grabs your fortune for the day!"""
        fort = await self.get_fortune(ctx.message.author.id)

        await self.bot.say(fortune[True])

def setup(bot):
    bot.add_cog(Fortune(bot))
