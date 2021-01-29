import json
import discord

from src.utils import message as msg
from src.game.game_bas import SHGame

f = open('config.json')
config = json.load(f)

client = discord.Client()

activeGames = {}
activePlayers = {}
serverConfs = {}

#
#   Load per-server configurations into memory.
#
async def Setup():
    pass

#
#   A forget-and-fire function that saves all configs to memory.
#
async def Save():
    pass

#
#   Tears down everything
#
async def Shutdown():
    await Save()
    for (cat, game) in activeGames:
        client.loop.create_task(game.Teardown())

###################
# EVENTS
###################

@client.event
async def on_ready():
    await msg.send(tag="info", location=__file__, channel=None, msg_type="plain", delete_after=None,
                   content="Connected as ${client.user.name}#${client.user.discriminator}!")



@client.event
async def on_message(message):
    #
    #   Is this message intended to be read by us?
    #
    if (message.author.bot or not message.content.startswith(config["prefix"])):
        return

    #
    #   What's this message?
    #
    _content = message.content[len(config["prefix"]):]
    _m_array = _content.split()
    command  = _m_array[0]
    args     = _m_array[1:]

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
            await msg.send(tag="error", location=__file__, channel=message.channel, msg_type="plain", delete_after=2,
                     content="You can only create games on servers!")
            return

        #
        #   If author is already in a game, return.
        #
        if message.author.id in activePlayers:
            await msg.send(tag="error", location=__file__, channel=message.channel, msg_type="plain", delete_after=2,
                      content="<@${message.author.id}>, you are already in a game!")
            return

        #
        #   If any of the args following the preset are not a valid player,
        #   then return and alert.
        #
        _playerargs  = list(map(lambda x: re.sub(r'<@([0-9]+)>', r'\1', x), args[1:]))
        _playerobjs  = []
        for p in _playerargs:
            _player = await client.get_user(p)
            _playerobjs.append(_player)

        if None in _playerobjs:
            await msg.send("error", location=__file__, channel=message.channel, msg_type="plain", delete_after=2,
                     content="Invalid player passed to `${self.prefix} creategame`!")
            return

        for player in _playerobjs:
            activePlayers.update( {player.id: True} )

        #
        #   We are a) in a server and b) have all necessary conditions.
        #   Make a category and create a game in it.
        #
        _newcategory = await message.guild.create_category("Secret Hitler")
        _pseudoUUID  = str(_newcategory.id)[:8]
        await _newcategory.edit(name="Secret Hitler ${_pseudoUUID}")
        _desiredmode = args[0]
        _newgame     = await SHGame(players=_playerobjs, client=client, category=_newcategory, _preset=_desiredmode)
        activeGames.update( {_newcategory.id: _newgame} )
        await _newgame.Setup()
        return

    if command == 'deletegame':
        #
        #   This command is only for management roles.
        #   Otherwise, a game should autodelete after completion (after 1 min).
        #
        #   TODO: implement this later. for now, just automatically delete after X minutes
        pass

    #
    #   If not, just pass it along to the relevant
    #   game, and let it handle the message.
    #
    categoryID = message.channel.category_id
    if categoryID in activeGames:
        activeGame = activeGames.get(categoryID)
        client.loop.create_task(activeGame.Handle(("message", message, command, args)))



@client.event
async def on_raw_reaction_add(payload):
    _guild    = await client.fetch_guild(payload.guild_id)
    _channel  = await _guild.get_channel(payload.channel_id)
    _message  = await _channel.fetch_message(payload.message_id)
    _category = _message.channel.category.id

    if _category in activeGames:
        activeGame = activeGames.get(_category)
        client.loop.create_task(activeGame.Handle(("reaction", payload, _message, "add")))



@client.event
async def on_raw_reaction_remove(payload):
    _guild    = await client.fetch_guild(payload.guild_id)
    _channel  = await _guild.get_channel(payload.channel_id)
    _message  = await _channel.fetch_message(payload.message_id)
    _category = _message.channel.category.id

    if _category in activeGames:
        activeGame = activeGames.get(_category)
        client.loop.create_task(activeGame.Handle(("reaction", payload, _message, "remove")))

