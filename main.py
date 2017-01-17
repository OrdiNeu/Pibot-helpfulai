import discord
import asyncio
import requests
import random
import time

coolkids = [
            'Mush',
            'Destragon'
            ]

list_log = [
        'No, you.',
        'Which is hilarious.',
        '(╯°□°）╯︵ ┻━┻',
        '*roooooooooooooooooooo*',
        '¯\_(ツ)_/¯'
      ]

list_ask = [
        "according to the data, I'd have to say yes.",
        "the data suggests that's a negative.",
        "the chances are very slim.",
        "I would have to say the chances are favorable.",
        "I do not have enough data to answer this question.",
        "I'm processing the answer, please ask again later."
        ]

dict_people = {}

dict_tagged = {}
dict_hand = {}

dict_server = {}

g_frequency = 0

g_log = True

g_nsa = True

g_unhelpful = False

channeltest = 0
tests = 0




async def exec_command(client, msg):
    if msg.content.startswith('!nr'):
        await nr(client, msg)
    elif msg.content.startswith('!trash'):
        await trash(client, msg)
    elif msg.content.startswith('!chat'):
        await chat(client, msg)
    elif msg.content.startswith('!log'):
        await log(client, msg)
    elif msg.content.startswith('!stats'):
        await stats(client, msg)
    elif msg.content.startswith('!fortune'):
        await fortune_gen(client, msg)
    elif msg.content.startswith('!ask'):
        await ask(client, msg)
    elif msg.content.startswith('!nsa'):
        await nsa(client, msg)
    elif msg.content.startswith('!unhelpful'):
        await unhelpful(client, msg)
    elif msg.content.startswith('!tag'):
        await tag(client, msg)
    elif msg.content.startswith('!scorch'):
        await scorch(client, msg)
    elif msg.content.startswith('!id'):
    	await id(client, msg)
    elif msg.content.startswith('!bgg'):
    	await bgg(client, msg)
    elif msg.content.startswith('!yt'):
    	await yt(client, msg)
    elif msg.content.startswith('!gg'):
    	await gg(client, msg)
    elif msg.content.startswith('!lotr'):
    	await lotr(client, msg)

    elif msg.content.startswith('!test'):
    	await test(client, msg)
    elif msg.content.startswith('!this'):
    	await this(client, msg)
    elif msg.content.startswith('!tost'):
    	await tost(client, msg)
    elif msg.content.startswith('!mentiontest'):
    	await mentiontest(client, msg)
    elif msg.content.startswith('!classtest'):
        await classtest(client, msg)
		
    elif msg.content.startswith('!resistance'):
    	await resistance(client, msg)
    elif msg.content.startswith('!rules'):
    	await rules(client, msg)


client = discord.Client()


class Skull:

	def __init__(self):
		self.channel = 0
		self.player = []
	
	async def setup(self,client,msg):
		self.channel = msg.channel
		self.playerNr = len(msg.mentions)
		if self.playerNr < 1:
			await send_message(self.channel, "Too few players.")
		elif self.playerNr > 100:
			await send_message(self.channel, "Too many players.")
		else:
			await self.skull_round(client,msg)
		
	def async skull_round(self,client,msg):
		#while total cards below playerNr every player play a card
		#

class MafiaDeCuba:

	def __init__(self):
		self.channel = 0
		self.player = []

class Resistance:

	spies = {1:0, 5:2, 6:2, 7:3, 8:3, 9:3, 10:4}
	mission = {1:(1,1,1,1,1), 5:(2,3,2,3,3), 6:(2,3,4,3,4), 7:(2,3,3,4,4), 8:(3,4,4,5,5), 9:(3,4,4,5,5), 10:(3,4,4,5,5)}
	requiredFails = {1:(1,1,2,1,1), 5:(1,1,1,1,1), 6:(1,1,1,1,1), 7:(1,1,1,2,1), 8:(1,1,1,2,1), 9:(1,1,1,2,1), 10:(1,1,1,2,1)}
	
	def __init__(self):
		self.channel = 0
		self.playerNr = 0
		self.player = []
		self.playerSpy = {}
		self.currentMission = 0
		self.firstPlayer = 0
		self.firstPlayerIt = 0
		self.failedVotes = 0
		self.resPoints = 0
		self.spyPoints = 0
		self.playerOrder = ""
		
	async def setup(self,client,msg):
		self.channel = msg.channel
		self.playerNr = len(msg.mentions)
		if self.playerNr < 5:
			await send_message(self.channel, "Too few players.")
		elif self.playerNr > 10:
			await send_message(self.channel, "Too many players.")
		else:
			randomness = random.sample(range(0, self.playerNr), self.playerNr)
			for x in range(0, self.playerNr):
				self.player.append(msg.mentions[randomness[x]])
						
			randomnesss = random.sample(self.player, self.spies[self.playerNr])						
			for guy in self.player:
				if guy in randomnesss:
					self.playerSpy[guy] = 1
				else:
					self.playerSpy[guy] = 0
					
			for guy in self.player:
				if self.playerSpy[guy] == 0:
					await send_message(guy, "You are loyal member of the **resistance**.")
				if self.playerSpy[guy] == 1:
					await send_message(guy, "You are a **spy**.")
					for gal in self.player:
						if self.playerSpy[gal] == 1 and gal != guy:
							await send_message(guy, gal.name + " is a **spy**, too.")
					
			self.playerOrder = ", ".join(x.name for x in self.player)
			await self.resRound(client, msg)
	
	
	async def resRound(self,client,msg):
		self.firstPlayer = self.player[self.firstPlayerIt]
		#await send_message(self.channel, self.firstPlayer.name + " please choose " + str([self.playerNr][self.currentMission]) + " people to send on the mission.")
		await send_message(self.channel, "\n".join(["Current score: Resistance: {} Spies: {}".format(self.resPoints, self.spyPoints),
										"The order of players is: " + self.playerOrder,
										"Amount of people needed for the missions: " + " ".join(x for x in str(self.mission[self.playerNr])),
										"Current mission: " + str(self.currentMission + 1)] ))
		if self.requiredFails[self.playerNr][self.currentMission] == 2:
			await send_message(self.channel, "There will be **TWO** fails required for this mission to be unsuccessful.")
		await send_message(self.channel, "{} please choose {} players to send on the mission.".format(self.firstPlayer.name, self.mission[self.playerNr][self.currentMission]))
		message = await client.wait_for_message(author=self.firstPlayer, check=lambda m: m.content.startswith("!assign") and len(m.mentions) == self.mission[self.playerNr][self.currentMission] and set(m.mentions).issubset(set(self.player)) )
		assignedPlayers = message.mentions
		await send_message(self.channel, "The assigned players are: " + ", ".join(x.name for x in assignedPlayers))
		await send_message(self.channel, "Everyone, please vote for or against this mission.")
		
		#Vote on the assignement
		for x in range (0, self.playerNr):
			await send_message(self.player[x], "\n".join(["The assigned players are: " + ", ".join(x.name for x in assignedPlayers),
												"Please send \'!vote yes\' or \'!vote no\'."]))
		voter = {}
		votes = 0
		yes = 0
		no = 0
		while votes < self.playerNr:
			message = await client.wait_for_message(check=lambda m: m.content.startswith("!vote") and m.channel.is_private)
			if message.author in self.player:
				if message.content.startswith('!vote yes'):
					if message.author in voter:
						if voter[message.author] == "No":
							no -= 1
							yes += 1
							await send_message(message.author, "Vote changed." )
					else:
						voter[message.author] = "Yes"
						yes = yes + 1
						votes = votes + 1
						await send_message(message.author, "Vote received." )
						
				if message.content.startswith('!vote no'):
					if message.author in voter:
						if voter[message.author] == "Yes":
							yes -= 1
							no += 1
							await send_message(message.author, "Vote changed." )
					else:
						voter[message.author] = "No"
						no = no + 1
						votes = votes + 1
						await send_message(message.author, "Vote received." )
		
		if no >= yes:
			await send_message(self.channel, "The mission was **canceled**.")

			votedVotes = ", ".join([key.name+": "+str(voter[key]) for key in voter.keys()])
			await send_message(self.channel, "The votes were: " + votedVotes)
			self.firstPlayerIt = (self.firstPlayerIt + 1)%self.playerNr
			self.failedVotes += 1
			await self.checkGameEnd(client,msg)
		else:
			self.failedVotes = 0
			await send_message(self.channel, "The mission has been **approved**.")
			votedVotes = ", ".join([key.name+": "+str(voter[key]) for key in voter.keys()])
			await send_message(self.channel, "The votes were: " + votedVotes)
			await send_message(self.channel, ", ".join(x.name for x in assignedPlayers) + " please perform the mission." )
		
			#Missions
			for x in range (0, len(assignedPlayers)):
				await send_message(assignedPlayers[x], "You are on a mission. Please send \'!mission success\' if you would like it to succeed or are a loyal member of the resistance. Send \'!mission fail\' if you would like to sabotage it." )

			voter = {}
			votes = 0
			success = 0
			fail = 0
			while votes < self.mission[self.playerNr][self.currentMission]:
				message = await client.wait_for_message(check=lambda m: m.content.startswith("!mission") and m.channel.is_private)
				if message.author in assignedPlayers:
					if message.content.startswith('!mission success'):
						if message.author in voter:
							if voter[message.author] == "Fail":
								voter[message.author] = "Success"
								fail -= 1
								success += 1
								await send_message(message.author, "Action changed." )
						else:
							voter[message.author] = "Success"
							success = success + 1
							votes = votes + 1
							await send_message(message.author, "Action received." )
					if message.content.startswith('!mission fail'):
						if self.playerSpy[message.author] == 0:
							await send_message(message.author, "You cannot sabotage yourself. Please send '!mission success' instead.")	
						else:
							if message.author in voter:
								if voter[message.author] == "Success":
									voter[message.author] = "Fail"
									success -= 1
									fail += 1
									await send_message(message.author, "Action changed." )
							else:
								voter[message.author] = "Fail"
								fail = fail + 1
								votes = votes + 1
								await send_message(message.author, "Action received." )
			if fail >= self.requiredFails[self.playerNr][self.currentMission]:
				await send_message(self.channel, "The mission was **unsuccessful**. " + str(fail) + " player sabotaged this mission.")
				self.spyPoints += 1
				self.currentMission += 1
				await self.checkGameEnd(client,msg)
			else:
				await send_message(self.channel, "The mission was **successful**.")
				self.resPoints += 1
				self.currentMission += 1
				await self.checkGameEnd(client,msg)
			
			

	async def checkGameEnd(self,client,msg):
		if self.failedVotes >= 5 or self.spyPoints >= 3:
			await send_message(self.channel, "**The game is over. The spies were victorious.**")
		elif self.resPoints >= 3:
			await send_message(self.channel, "**The game is over. The resistance was victorious.**")
		else:
			self.firstPlayerIt = (self.firstPlayerIt + 1)%self.playerNr
			await self.resRound(client,msg)
		

async def resistance(client,msg):
	rest = Resistance()
	await rest.setup(client,msg)




class Dog:
    kind = 'canine'
    tricks = ["bark"]           # mistaken use of a class variable

    def __init__(self, name):
        self.name = name

    def add_trick(self, trick):
        self.tricks.append(trick)
		
async def classtest(client,msg):
	a = Dog('Rex')
	a.add_trick('roll over')
	a.kind
	await send_message(msg.channel, a.name + a.kind + a.tricks[0])


		
async def rules(client, msg):
    if msg.content.startswith("!rules resistance"):
        await send_message(msg.channel, "\n".join(["Resistance members need 3 successful missions to win.",
        "Spies need 3 failed missions.",
        "Every round someone is first player and assigns a number of people to a mission.",
        "Then everyone votes in private by writing !vote yes/no to the bot.",
        "If half voted no, then the next player in order is first player.",
        "Otherwise the mission happens.",
        "The people assigned to the mission write !mission successful/fail to the bot in private",
        "Resistance members should always write successful.",
        "Spies can choose which option they want.",
        "If at least ONE person on the mission wrote fail, the mission fails.",
        "Otherwise the mission is successful and the next player is first player.",
        "Spies also win in case 5 votes ever consecutively fail."]))
		
		
	
	
async def test(client,msg):
    global channeltest
    await send_message(channeltest, "*Testing tests.*")

async def tost(client,msg):
    global tests
    global channeltest
    tests = tests + 1
    if tests >= 2:
        await send_message(channeltest, "*Testing lots of tests.*")


async def mentiontest(client,msg):
    await send_message(msg.channel, len(msg.mentions))

async def this(client,msg):
    global channeltest
    channeltest = msg.channel

async def trash(client,msg):
    if msg.author.name in coolkids:
        await send_message(msg.channel, "*The Helpful AI is trashed to increase the motivation of looking up cards on your own.*")
        exit()
    else:
        await send_message(msg.channel, "*The runner is not tagged.*")

async def ask(client,msg):
    if len(' '.join(msg.content.split()[1:]).lower()) > 0 and '?' in msg.content:
        m_response = msg.author.mention + ', ' + random.choice(list_ask) 
    else:
        m_response = msg.author.mention + ", please ask a yes or no question." 
    await send_message(msg.channel, m_response)

async def fortune_gen(client,msg):
    if len(' '.join(msg.content.split()[1:])) != 0:
            m_response = "Invalid data entry. Please simply say: ```!fortune```"
    else:
        timestamp = str(msg.timestamp).split()[0].split('-')[2]
        if msg.author.id in dict_people:
            if int(str(dict_people[msg.author.id]).split()[0].split('-')[2]) - int(timestamp) != 0:
                await fortune_roll(client,msg)
            else:
                m_response = msg.author.mention + ', you only get one fortune per day!'
                await send_message(msg.channel, m_response)
        else:
            await fortune_roll(client,msg)

async def fortune_roll(client,msg):
    dict_people[msg.author.id] = msg.timestamp
    m_fortune = random.randint(1,99)
    m_fortune = 100 - m_fortune
    if m_fortune > 98:
        m_fortune = "PERFECT! Go confess your love! Go ace that test! Today is your day! ＹＡＨ♪☆0(＾＾0)＾＾(0＾＾)0☆♪ＹＡＨ"
    elif m_fortune > 94:
        m_fortune = "Amazing! Go out and have fun! Nothing can go wrong today! ルンルン♪~♪ d(⌒o⌒)b ♪~♪ルンルン"
    elif m_fortune > 86:
        m_fortune = "Excellent! Make the best of the day, it'll be wonderful! o(＾∇＾)oﾜｰｲ♪"
    elif m_fortune > 72:
        m_fortune = "Great! Do something difficult! You'll be successful! (v^ー°) ヤッタネ"
    elif m_fortune > 49:
        m_fortune = "Good! Spend some time with your friends to make it even better! (*^-ﾟ)vｨｪｨ♪ "
    elif m_fortune > 26:
        m_fortune = "Bad! I hope it's not too bad. You'll make it through just fine! （´ノω・。）"
    elif m_fortune > 12:
        m_fortune = "Awful! Please don't do anything dangerous today! You could get hurt! ｪﾝ（ｐ´；ω；`ｑ）ｪﾝ"
    elif m_fortune > 4:
        m_fortune = "Terrible! Just take it easy and stay home! Today is just scary! ｡゜:(つд⊂):゜。ｳえーﾝ；；"
    elif m_fortune > 1:
        m_fortune = "Abysmal! Maybe you should just go to sleep until today is over! ｩゎ━｡ﾟ(ﾟ´Д｀*ﾟ)ﾟ｡━ﾝ!!!"
    else:
        m_fortune = "WURST! I suppose your life hasn't been too bad! ｡ﾟ(●ﾟ´Д)ﾉ｡ﾟヽ(　　)ﾉﾟ｡ヽ(Д｀ﾟ●)ﾉﾟ｡｡ﾟヽ(●ﾟ´Д｀ﾟ●)ﾉﾟ｡ｳﾜｧｧｧﾝ!!"
    m_response = msg.author.mention + " , your fortune is: " + m_fortune
    await send_message(msg.channel, m_response)

async def tag(client,msg):
    runner = msg.mentions[0]
    if runner.id in dict_tagged and dict_tagged[runner.id] != 0:
        dict_tagged[runner.id] = dict_tagged[runner.id] + 1
        m_response = runner.name + " now has " + str(dict_tagged[runner.id]) + " tags."
    else:
        dict_tagged[runner.id] = 1
        m_response = runner.name + " is now tagged."
    await send_message(msg.channel, m_response)

async def scorch(client,msg):
    runner = msg.mentions[0]
    if runner.id in dict_tagged and dict_tagged[runner.id] != 0:
        if runner.id in dict_hand:
            if dict_hand[runner.id] >= 4:
                dict_hand[runner.id] = dict_hand[runner.id] - 4
                m_response = runner.name + " suffered 4 meat damage and now has " + str(dict_hand[msg.author.id]) + " cards remaining."
            else:
                dict_hand[runner.id] = 5
                dict_tagged[runner.id] = 0
                m_response = runner.name + " has flatlined."
        else:
            dict_hand[runner.id] = 1
            m_response = runner.name + " suffered 4 meat damage and now has 1 card remaining."
    else:
        m_response = runner.name + " is not tagged."
    await send_message(msg.channel, m_response)

async def log(client, msg):
    global g_log
    if g_log == True:
        g_log = False
        print('Logging messages has been turned off.')
    else:
        g_log = True
        print('Logging messages has been turned on.')
    print()

async def stats(client,msg):
    global g_frequency
    print("Frequence of chat in " + msg.channel.name + " is: " + str(g_frequency))
    print("Logged message count: " + str(len(list_log)))
    print()

async def chat(client, msg):
    global g_frequency
    m_content = ' '.join(msg.content.split()[1:])
    m_channel = ' '.join(m_content.split()[0:1])
    m_frequency = ' '.join(msg.content.split()[2:])
    if len(str(m_frequency)) != 0:
        if len(str(m_frequency)) > 3:
            print("Number too long. Cannot set chat frequency.")
        else:
            g_frequency = int(m_frequency)
            dict_server[m_channel] = g_frequency
            print("Frequency of chat in", m_channel, "is:", str(g_frequency))
    else:
        if len(str(m_channel)) != 0:
            if len(str(m_channel)) > 3:
                print("Number too long. Cannot set chat frequency.")
            else:
                g_frequency = int(m_channel)
                dict_server[msg.channel.id] = g_frequency
                print("Frequency of chat in", msg.channel, "is:", str(g_frequency))
        else:
           g_frequency = 0
           dict_server[msg.channel.id] = g_frequency
           print("Frequency of chat in", msg.channel, "is:", str(g_frequency))
    print()

async def nsa(client, msg):
    global g_nsa
    if g_nsa == True:
        g_nsa = False
        print("==================================================")
        print("NSA mode is off.")
        print("==================================================")
        print()
    else:
        g_nsa = True
        print("==================================================")
        print("You are now invading people's privacy.")
        print("Errors may occur if names, servers, or messages contain special characters.")
        print("==================================================")
        print()

async def unhelpful(client, msg):
    global g_unhelpful
    if g_unhelpful == True:
        g_unhelpful = False
        print("==================================================")
        print("Unhelpful mode is off.")
        print("==================================================")
        print()
    else:
        g_unhelpful = True
        print("==================================================")
        print("You are now being unhelpful so that Mush has a friend to talk to.")
        print("==================================================")
        print()

async def nr(client, msg):
    m_query = ' '.join(msg.content.split()[1:]).lower()
    if m_query == "smc":
        m_query = "self-modifying code"
    elif m_query == "jesus":
        m_query = "jackson howard"
    elif m_query == "sot":
        m_query = "same old thing"
    elif m_query == "nyan":
        m_query = "noise"
    elif m_query == "neh":
        m_query = "near earth hub"
    elif m_query == "sot":
        m_query = "same old thing"
    elif m_query == "nyan":
        m_query = "noise"
    elif m_query == "tilde" or m_query == "neko":
        m_query = "blackat"
    elif m_query == "ordineu":
        m_query = "exile"
    if m_query == "kika":
        m_response = "http://a.pomf.cat/hxntik.png"
    elif m_query == "leg":
        m_response = "http://puu.sh/nmYZW.png"
    elif m_query == "triffids":
        m_response = "http://run4games.com/wp-content/gallery/altcard_runner_id_shaper/Nasir-by-stentorr-001.jpg"
    else:
        m_cards = [c for c in requests.get('http://netrunnerdb.com/api/cards/').json() if c['title'].lower().__contains__(m_query)]
        for x in range(0, len(m_cards)):
            if m_query == m_cards[x]['title'].lower():
                m_response = "http://netrunnerdb.com" + m_cards[x]['imagesrc']
                await send_message(msg.channel, m_response)
                return
        if len(m_cards) == 1:
            m_response = "http://netrunnerdb.com" + m_cards[0]['imagesrc']
        elif len(m_cards) == 0:
            m_response = "Sorry, I cannot seem to find any card with these parameters."
        else:
            m_response = "http://netrunnerdb.com/find/?q=" + m_query.replace (" ","+")
    await send_message(msg.channel, m_response)

async def lotr(client, msg):
    m_query = ' '.join(msg.content.split()[1:]).lower()
    m_cards = [c for c in requests.get('https://ringsdb.com/api/public/cards/').json() if c['name'].lower().__contains__(m_query)]
    for x in range(0, len(m_cards)):
        if m_query == m_cards[x]['name'].lower():
            m_response = "https://ringsdb.com" + m_cards[x]['imagesrc']
            await send_message(msg.channel, m_response)
            return
    if len(m_cards) == 1:
        m_response = "https://ringsdb.com" + m_cards[0]['imagesrc']
    elif len(m_cards) == 0:
        m_response = "Sorry, I cannot seem to find any card with these parameters."
    else:
        m_response = "https://ringsdb.com/find?q=" + m_query.replace (" ","+")
    await send_message(msg.channel, m_response)

async def bgg(client, msg):
    query = ' '.join(msg.content.split()[1:]).lower()
    query = query.replace (" ","+")
    response = "https://boardgamegeek.com/geeksearch.php?action=search&objecttype=boardgame&q=" + query
    await send_message(msg.channel, response)

async def yt(client, msg):
    query = ' '.join(msg.content.split()[1:]).lower()
    query = query.replace (" ","+")
    response = "https://www.youtube.com/results?search_query=" + query
    await send_message(msg.channel, response)

async def nsa_check(client, msg):
	global g_nsa
	global g_log
	if g_nsa == True:
		if msg.server != None:
			print("==================================================")
			print("Server name: " + str(msg.server.name.encode('utf-8')).lstrip("b'").rstrip("'"))
			print("User name: " + str(msg.author.name.encode('utf-8')).lstrip("b'").rstrip("'"))
			print("Channel name: " + str(msg.channel.name.encode('utf-8')).lstrip("b'").rstrip("'"))
			print("Channel code: " + msg.channel.id)
			print("--------------------------------------------------")
			print(str(msg.content.encode('utf-8')).lstrip("b'").rstrip("'"))
			print("==================================================")
	if g_log == True:
		if len(str(msg.content)) > 10:
			if 'http' in msg.content or '@' in msg.content or msg.content.startswith('!'):
				x = "placeholder"
			else:
				list_log.append(msg.content)

async def gg(client, msg):
    response = "http://36.media.tumblr.com/c90711c18b4f133e5bda77f1c696f40e/tumblr_nyr7rqpjXr1ueh03io1_1280.jpg"
    await send_message(msg.channel, response)

	
async def send_message(location, message):
	for tries in range(1, 6):
		try:
			return await client.send_message(location, message)
		except discord.HTTPException as e:
			if e.response.status == 502:
				await asyncio.sleep(tries * 2)
			else:
				raise e

@client.event
async def on_ready():
    print('Logged in as')
    print('Helpful AI') #original: client.user.name
    print(client.user.id)
    print('------')

@client.event
async def on_message(msg):
    global g_frequency
    if msg.author.name != client.user.name:
        await nsa_check(client, msg)
        if msg.channel.id in dict_server:
             g_frequency = dict_server[msg.channel.id]
        else:
            g_frequency = 0
        m_frequency = g_frequency
        m_chat = random.randint(1, 100)
        if msg.content.startswith('!'):
            msg.content = msg.content.lower()
            await exec_command(client, msg)
        else:
            m_message = msg.content.lower()
            if ('ai' in m_message and ('?' in m_message or "you" in m_message)) and g_unhelpful == True:
                response = random.choice(list_log)
                if g_nsa == False:
                    print("==================================================")
                    print("Server name: " + str(msg.server.name.encode('utf-8')).lstrip("b'").rstrip("'"))
                    print("Channel name: " + str(msg.channel.name.encode('utf-8')).lstrip("b'").rstrip("'"))
                    print("==================================================")
                    print("Responded to " + str(msg.author.name.encode('utf-8')).lstrip("b'").rstrip("'") + "'s message:")
                    print(str(msg.content.encode('utf-8')).lstrip("b'").rstrip("'"))
                    print("--------------------------------------------------")
                print("Responded based on message content, response was:")
                print(str(response.encode('utf-8')).lstrip("b'").rstrip("'"))
                print("--------------------------------------------------")
                if g_nsa == False:
                    print()
                await send_message(msg.channel, response)
            elif m_chat <= m_frequency:
                while m_chat <= m_frequency:
                    m_frequency = m_frequency - 100
                    response = random.choice(list_log)
                    if g_nsa == False:
                        print("==================================================")
                        print("Server name: " + str(msg.server.name.encode('utf-8')).lstrip("b'").rstrip("'"))
                        print("Channel name: " + str(msg.channel.name.encode('utf-8')).lstrip("b'").rstrip("'"))
                        print("==================================================")
                        print("Responded to " + str(msg.author.name.encode('utf-8')).lstrip("b'").rstrip("'") + "'s message:")
                        print(str(msg.content.encode('utf-8')).lstrip("b'").rstrip("'"))
                        print("--------------------------------------------------")
                    print("Responded by chance, response was:")
                    print(str(response.encode('utf-8')).lstrip("b'").rstrip("'"))
                    print("--------------------------------------------------")
                    if g_nsa == False:
                        print()
                    await send_message(msg.channel, response)
        if g_nsa == True:
            print()

client.run('haas@mt2015.com', 'welovemush')