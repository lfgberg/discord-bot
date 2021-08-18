import discord
import time
from discord import webhook
import ccsoBotReactions
import ccsoBotCreds
import ccsoBotScheduler
import requests
import random
from discord.ext import tasks, commands

# Main: Handles main bot code and links everything together. Will use commands to run, start, and stop features.

# ------------------------------------------------------------------------------------------------------------


# Intents library required for the on_raw_reaction_add function
intents = discord.Intents.default()
intents.reactions = True
client = discord.Client(intents=intents)

# ------------------------------------- Bot commands / events -------------------------------------
# ------------------------------------- 1) Reaction Role Message -------------------------------------
# Takes an emoji and returns a role based on the input, default case is None, this return is handled in on_raw__reaction_add()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

    # channel and message id of msg to react to for roles
    # TEST SERVER
    # channel_id = 852925086238900225
    # message_id = 876803239385923584

    # static_id = 876806469939519489
    # dynamic_id = 876806477745127494

    # FOR LIVE CCSO SERVER
    # can grab from disc by shift-clicking "copy id"
    channel_id = 876897589889495070
    static_id = 876897950914187284
    dynamic_id = 876898145185964063
    
    # rules message
    # message = await client.get_channel(channel_id).fetch_message(message_id)

    # role selection messages
    staticMessage = await client.get_channel(channel_id).fetch_message(static_id)
    dynamicMessage = await client.get_channel(channel_id).fetch_message(dynamic_id)

    await ccsoBotReactions.addReactionsToMessage(staticMessage, dynamicMessage)

# ------------------------------------- 2) Youtube Parsing/Messaging -------------------------------------

# Checks for new content and posts
# https://discordpy.readthedocs.io/en/latest/ext/tasks/
@tasks.loop(seconds=10.0)
async def grabSomeContent():
    print("fetching content...")

    mustHaveChannels = ["UC0ArlFuFYMpEewyRBzdLHiw", "UCByOX6pW9k1OYKpDA2UHvJw", "UCLDnEn-TxejaDB8qm2AUhHQ", "UCKGe7fZ_S788Jaspxg-_5Sg", "UCVeW9qkBjo3zosnqUbG7CFw", "UC0ZTPkdxlAKf-V33tqXwi3Q"]

    for channel in mustHaveChannels:
        print("sending")

        # SAVE API CALLS    
        # videos = ccsoBotScheduler.checkForUpdates(channel)
        # print("mainvids: ", videos)

        # sendWebhookMessage(videos)

    print("fetching new articles...")
    ccsoBotScheduler.checkForArticles()


def sendWebhookMessage(videos):

    video = videos[0]

    webhookUrl = ccsoBotCreds.getWebhookUrl()
    # for testing

    # TODO: branch for articles VS videos 

    params = {'username': 'webhook-test',
              'avatar_url': "", 'content': "New video from {}!".format(video['channelTitle']), }
    params["embeds"] = [
        {
            'image': {
                "url": video['thumbnail'],
            },
            "description": video['description'],
            "title": video['title'],
            "url": video['url'],
            "color": 4,  # colors: https://gist.github.com/thomasbnt/b6f455e2c7d743b796917fa3c205f812
            "author": {
                "name": video['channelTitle'],
                "url": video['channelId'],
            }
        }
    ]

    try:
        requests.post(webhookUrl, json=params)

    except:
        print("request error")


# ------------------------------------- 3) Role Reactions -------------------------------------

@client.event
async def on_raw_reaction_add(payload):
    # Defines the message, reaction, user, and role variables

    # Waits for a specific message to be reacted to, then adds a user to a specific role
    await ccsoBotReactions.addRoleReaction(payload, client)
    # passing the client is probably doodoo; do this @ bootstrapping



# ------------------------------------- 4) Bot Commands -------------------------------------

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    elif message.content == "test":
        print("recognize command")
        embedVar = discord.Embed(
            title="balls in my face title", description="awesome description")
        embedVar.add_field(
            name="Field1", value="balls in my face 1", inline=False)
        embedVar.add_field(
            name="Field2", value="balls in my face 2", inline=True)
        await message.channel.send(embed=embedVar)

    # if the message !rules is sent, it will send the rules message into #rules ADD: check for server admin role
    elif message.content.startswith("!rules"):
        print(message.author.roles)
        for role in message.author.roles:
            if role.name == "server-manager":
                rulesChannel = discord.utils.get(
                    client.get_all_channels(), name="rules")
                await rulesChannel.purge()
                rulesVar = discord.Embed(
                    title="CCSO Server Rules", description="")
                rulesVar.add_field(
                    name="Rules", value="I have a ginormous colkc and \nalso my balls are ginorumes", inline=False)
                await rulesChannel.send(embed=rulesVar)

    # best cmmand
    elif message.content == "balls in my face":
        counter = 0
        while (True):
            await message.channel.send(message.content)
            time.sleep(1)
            counter += 1
            if counter > 10:
                return False

    # pop smoke command 
    elif message.content == "!pop":
        
        popSmokeSongs = ["https://www.youtube.com/watch?v=AzQJO6AyfaQ", "https://www.youtube.com/watch?v=Q9pjm4cNsfc", "https://www.youtube.com/watch?v=uuodbSVO3z0", "https://www.youtube.com/watch?v=usu0XY4QNB0"]
        aSong = random.choice(popSmokeSongs)
        await message.channel.send("RIP the goat" + "\n" + aSong)


# ------------------------------------------------------------------------------------------------------------


def bootstrapping():

    # Initial log in and check from the bot
    # grab Discord API token from creds.py file
    token = ccsoBotCreds.getDiscordKey()
    gcpKey = ccsoBotCreds.getGCPKey()

    ccsoBotReactions.sendClientToken(client)

    # starts the content scheduler
    grabSomeContent.start()
    print("bootstrapping done")
    client.run(token)
    
bootstrapping()
