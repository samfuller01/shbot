import discord
import re

import src.game.utils

#
#   Wrapper for the bot.
#
class SHBot (object):

    def __init__(self, token = None, prefix = None):
        #
        #   The discord bot client.
        #
        self.client = discord.Client()
        self.token  = token;
        self.prefix = prefix;
        #
        #   Games are essentially a function that
        #   reside in a category. We determine the
        #   category in which each Discord event
        #   took place to route it to the correct game.
        #
        self.activeGames = {}

    #
    #   Set up the event handlers, route all non-global
    #   events into the games via the (bundle, "type") structure.
    #
    def Setup(self):
        pass

    #
    #   We're ready to log in.
    #
    async def Start(self):
        await self.client.login(token, bot=True)

    #####
    #   Event handlers.
    #####

    #
    #
    #
    @self.client.event
    async def on_ready():
        utils.log("info", "Connected as ${self.client.username}#${self.client.discriminator}!")

    #
    #
    #
    @self.client.event
    async def on_message(message):
        #
        #   Is this message intended to be read by us?
        #
        if (message.author.bot or not message.content.startswith(self.prefix)):
            return

        #
        #   What's this message?
        #
        _content = message.content[len(self.prefix):]
        _m_array = _content.split(' ')
        command  = _m_array[0]
        args     = _m_array[1:]

        #
        #   Is this a special or global command?
        #
        if command == 'creategame':

            #
            #   If not a server, return.
            #
            if (message.guild == None):
                utils.log("error", __file__, "Can't make a game in a DM channel!")
                utils.msg("error", message.channel, "You can only create games on servers!")
                return

            #
            #   If author is already in a game, return.
            #
            if message.author.id in self.activePlayers:
                utils.log("error", __file__, "${message.author.id} is already in a game!")
                utils.msg("error", message.channel, "<@${message.author.id}>, you are already in a game!")
                return

            #
            #   If any of the args following the preset are not a valid player,
            #   then return and alert.
            #
            _playerargs  = list(map(lambda x: re.sub(r'<@([0-9]+)>', r'\1', x), args[1:]))
            _playerobjs  = list(map(lambda x: await self.client.get_user(x), _playerargs))
            if None in _playerobjs:
                utils.log("error", __file__, "Invalid player passed to createGame.")
                utils.msg("error", message.channel, "Invalid player passed to `${self.prefix} creategame`!")
                return
            for player in _playerobjs:
                self.activePlayers.update( {player.id: True} )

            #
            #   We are a) in a server and b) have all necessary conditions.
            #   Make a category and create a game in it.
            #
            _newcategory = await message.guild.create_category("Secret Hitler")
            _pseudoUUID  = str(_newcategory.id)[:7]
            await _newcategory.edit(name="Secret Hitler ${_pseudoUUID}")
            _desiredmode = args[0]
            _newgame     = await SHGame(players=_playerobjs, client=self.client, category=_newcategory, _preset=_desiredmode)
            self.activeGames.update( {_newcategory.id: _newgame} )
            return

        if command == 'deletegame':
            #
            #   This command is only for management roles.
            #   Otherwise, a game should autodelete after completion (after 1 min).
            #
            pass

        #
        #   If not, just pass it along to the relevant
        #   game, and let it handle the message.
        #
        categoryID = message.channel.category_id
        if categoryID in self.activeGames:
            activeGame = self.activeGames.get(categoryID)
            activeGame.Handle(("message", message, command, args))

    #
    #
    #
    @self.client.event
    async def on_raw_reaction_add(payload):
        _guild    = await self.client.fetch_guild(payload.guild_id)
        _channel  = await _guild.get_channel(payload.channel_id)
        _message  = await _channel.fetch_message(payload.message_id)
        _category = _message.channel.category.id

        if _category in self.activeGames:
            activeGame = self.activeGames.get(_category)
            activeGame.Handle(("reaction", payload, _message, "add"))

    #
    #
    #
    @self.client.event
    async def on_raw_reaction_remove(payload):
        _guild    = await self.client.fetch_guild(payload.guild_id)
        _channel  = await _guild.get_channel(payload.channel_id)
        _message  = await _channel.fetch_message(payload.message_id)
        _category = _message.channel.category.id

        if _category in self.activeGames:
            activeGame = self.activeGames.get(_category)
            activeGame.Handle(("reaction", payload, _message, "remove"))

