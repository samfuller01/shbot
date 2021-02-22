import json
import re
import discord
import discord.ext.commands as commands
import asyncio
from threading import Thread

from src.utils import message as msg
from src.SH.sh_game import SHGame
from src.trivia.trivia_game import TriviaGame

f = open('config.json')
config = json.load(f)

client = commands.Bot(config["prefix"])

activeGames = {}
activePlayers = {}
serverConfs = {}

#
#   A forget-and-fire function that saves all configs to memory.
#
async def Save():
    await msg.send(tag="debug", location=__file__, channel=None, msg_type="plain", delete_after=None,
                   content="Saved configuration state!")

async def SaveTask():
    await Save()
    await asyncio.sleep(300)

#
#   Load per-server configurations into memory.
#
async def Setup():
    client.loop.create_task(SaveTask())

#
#   Tears down everything
#
async def Shutdown():
    await Save()
    for (cat, game) in activeGames.items():
        await game.Teardown()

###################
# EVENTS
###################

async def cleanup(guild):
    for channel in guild.text_channels:
        if channel.name.startswith("seat") or channel.name == "game-chat" or channel.name == "board-state":
            await channel.delete()
    for category in guild.categories:
        if category.name.startswith("Secret Hitler") or category.name.startswith("Trivia") or category.name.startswith("Game"):
            await category.delete()

@client.event
async def on_ready():
    await msg.send(tag="info", location=__file__, channel=None, msg_type="plain", delete_after=None,
                   content="Connected as {name}#{num}!".format(name=client.user.name, num=client.user.discriminator))
    for guild in client.guilds:
        await cleanup(guild) # TODO remove this once we actually have an intelligent game management system in place.
                             # currently just purges all games on startup.

@client.event
async def on_message(message):
    #
    #   Is this message intended to be read by us?
    #
    if (message.author.bot):
        return

    #if (message.author.bot or not message.content.startswith(config["prefix"])):
    #    return



    #
    #   What's this message?
    #
    _content = message.content
    _m_array = _content.split()
    directory = _m_array[0]
    command  = _m_array[1] if len(_m_array) > 1 else None
    args     = _m_array[2:] if len(_m_array) > 1 else None
    flags    = build_flags(args)


    #
    #   Is this a special or global command?
    #
    #   TODO: permissions structure for global commands!
    #
    
    
    if command == 'creategame':

        #
        #   If not a server, return.
        #
        if (message.guild == None):
            await msg.send(tag="error", location=__file__, channel=message.channel, msg_type="plain", delete_after=5,
                     content="You can only create games on servers!")
            return

        #
        #
        #
        if (len(args) == 0):
            await msg.send(tag="info", location=__file__, channel=message.channel, msg_type="plain", delete_after=None,
                           content="Usage: {pref} creategame 'preset' [@players]".format(pref=config["prefix"]))
            return

        #
        #   If author is already in a game, return.
        #
        if message.author.id in activePlayers:
            await msg.send(tag="error", location=__file__, channel=message.channel, msg_type="plain", delete_after=5,
                            content="<@{id}>, you are already in a game!".format(id=message.author.id))
            return

        #
        #   If any of the args following the preset are not a valid player,
        #   then return and alert.
        #
        _playerargs  = list(map(lambda x: re.sub(r'<@!?([0-9]+)>', r'\1', x), args[0:]))
        print(_playerargs)
        _playerobjs  = []
        for p in _playerargs:
            try:
                _player = await message.channel.guild.fetch_member(p)
                _playerobjs.append(_player)
            except(discord.NotFound, discord.HTTPException):
                 await msg.send("error", location=__file__, channel=message.channel, msg_type="plain", delete_after=5,
                                content="Invalid player '{player}' passed to `{pref} creategame`!".format(player=p, pref=config["prefix"]))
                 _playerobjs.append(None)

        if None in _playerobjs:
            return

        

        #
        #   We are a) in a server and b) have all necessary conditions.
        #   Make a category and create a game in it.
        #
        _newcategory = await message.guild.create_category("Game")
        _pseudoUUID  = str(_newcategory.id)[:8]
        
        _desiredmode = args[0]
        _newgame = None
        if directory == "sh!":
            # TODO I want this check moved somewhere else probably
            if (len(_playerobjs) < 5 or len(_playerobjs) > 10):
                await msg.send(tag="error", location=__file__, channel=message.channel, msg_type="plain", delete_after=5,
                            content="Your game must have between 5 and 10 players! No mode will support more or less players.")
                return

            for player in _playerobjs:
                activePlayers.update( {player.id: True} )
            
            _newgame     = await SHGame(players=_playerobjs, client=client, category=_newcategory, flags=flags, context=message)
            await _newcategory.edit(name="Secret Hitler {uuid}".format(uuid=_pseudoUUID))
        elif directory == "trivia!":
            # TODO trivia games maybe shouldn't really have an "active player" restriction?
            for player in _playerobjs:
                activePlayers.update( {player.id: True} )
            
            _newgame     = await TriviaGame(players=_playerobjs, client=client, category=_newcategory, flags=flags, context=message)
            await _newcategory.edit(name="Trivia {uuid}".format(uuid=_pseudoUUID))
        else:
            return
        activeGames.update( {_newcategory.id: _newgame} )
        await _newgame.Setup()
        await msg.send(tag="success", location=__file__, channel=None, msg_type="plain", delete_after=None,
                       content="Game {uuid} created!".format(uuid=_pseudoUUID))
        return

    if command == 'deletegame':
        #
        #   This command is only for management roles.
        #   Otherwise, a game should autodelete after completion (after 1 min).
        #
        #   TODO: update this to run per-server.

        if (message.guild == None or message.channel.category.id not in activeGames):
            await msg.send(tag="error", location=__file__, channel=message.channel, msg_type="plain", delete_after=5,
                           content="There is no game running here!")
            return

        if (message.author.id not in activePlayers and message.author.id not in config["admins"]):
            await msg.send(tag="error", location=__file__, channel=message.channel, msg_type="plain", delete_after=5,
                           content="<@{mention}>, you are not in a game!".format(mention=message.author.id))
            return

        activeGame = activeGames.get(message.channel.category.id)
        playerids = list(map(lambda x: x.id, activeGame.players))

        if (message.author.id not in playerids and message.author.id not in config["admins"]):
            await msg.send(tag="error", location=__file__, channel=message.channel, msg_type="plain", delete_after=5,
                           content="<@{mention}>, you are not allowed to delete this game.".format(message.author.id))
            return

        for player in activeGame.players:
            if player.id in activePlayers:
                activePlayers.pop(player.id)

        _the_id = message.channel.category.id
        await activeGame.Teardown()
        activeGames.pop(_the_id)

    #
    #   If not, just pass it along to the relevant
    #   game, and let it handle the message.
    #
    categoryID = message.channel.category_id
    if categoryID in activeGames:
        activeGame = activeGames.get(categoryID)
        auxthread = Thread(group = None, target = asyncio.run_coroutine_threadsafe, args = (activeGame.Handle(("message", message, command, args)), client.loop))
        auxthread.start()

    client.loop.create_task(client.process_commands(message))

def build_flags(args):
    flags = {}
    if args == None:
        return {}
    # find places where we have a flag
    for i in range(len(args)):
        if args[i].startswith("-"):
            # read data until we reach the next flag
            values = []
            for j in range(i + 1, len(args)):
                if args[j].startswith("-"):
                    break
                else:
                    values.append(args[j])
            flags[args[i]] = values
    return flags



@client.event
async def on_raw_reaction_add(payload):
    if payload.member.bot:
        return 

    _channel  = client.get_channel(payload.channel_id)
    _message  = await _channel.fetch_message(payload.message_id)
    _category = _message.channel.category.id

    #print(payload.emoji)

    if _category in activeGames:
        activeGame = activeGames.get(_category)
        auxthread = Thread(group = None, target = asyncio.run_coroutine_threadsafe, args = (activeGame.Handle(("reaction", payload, _message, "add")), client.loop))
        auxthread.start()



@client.event
async def on_raw_reaction_remove(payload):
    _channel  = client.get_channel(payload.channel_id)
    _message  = await _channel.fetch_message(payload.message_id)
    _category = _message.channel.category.id

    if _category in activeGames:
        activeGame = activeGames.get(_category)
        auxthread = Thread(group = None, target = asyncio.run_coroutine_threadsafe, args = (activeGame.Handle(("reaction", payload, _message, "remove")), client.loop))
        auxthread.start()


###################
# COMMANDS
###################

@client.command()
async def shutdown(context):
    if context.author.id not in config["admins"]:
        await msg.send(tag="warning", location=__file__, channel=context.channel, msg_type="plain", delete_after=5,
                   content="<@{}>, you can't shutdown the bot.".format(context.author.id))
        return

    await Shutdown()
    await msg.send(tag="success", location=__file__, channel=None, msg_type="plain", delete_after=None,
                   content="Shutting down.")
    await client.logout()

#@client.command()
#async def help(context):
#    pass

@client.command()
async def presets(context):
    pass

###################
# MAIN
###################

client.loop.create_task(Setup())
client.run(config["token"])
