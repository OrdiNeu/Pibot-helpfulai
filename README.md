# Pitbot-helpfulai

A discord bot for personal use. Looks up cards from Netrunner/Lord of the Rings/Arkham Horror Fantasy Flight LCGs

# Inviting It To Your Server

Just follow this link:
https://discordapp.com/oauth2/authorize?permissions=0&client_id=272179716654628865&scope=bot
Feel free to invite it wherever you want. Message me at `@OrdiNeu#6488` if you need to.

# Setting Up Your Own Instance

Requires a pibot-discord-cred.json file that looks like the following:
```
{
  "token": "insert_token_here"
  "client_id": "insert_client_id_here"
}
```
The entries for both these fields can be obtained by following the instructions [here](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token)

You will require the following libraries (installable via pip) and python3
```
apiclient
discord
emoji
google-api-python-client
html2text
tabulate
tweepy
unidecode
```
