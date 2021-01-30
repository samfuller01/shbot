from definitions import *
from src.game.board import SHBoard
from src.game.deck import SHDeck
from src.utils import message as msg

import random
import discord
from threading import RLock

class aobject (object):
 
    async def __new__(cls, *a, **kw):
        instance = super().__new__(cls)
        await instance.__init__(*a, **kw)
        return instance

    async def __init__(self):
        pass

#
#   Game controller.
#
class SHGame (aobject):

    #
    # client : DiscordClient
    #   a ref to the bot client
    #
    # category : CategoryChannel
    #   a channel object used to interface
    #   with the corresponding game channels
    #   on Discord; need not be current
    #
    # preset : dict
    #   a dict or JSON that contains the
    #   configuration for this game
    #
    async def __init__(self, players=None, client=None, category=None, preset=None):
        #
        #
        #   The SHGame uses the client and category
        #   to handle channel creation and management,
        #   reaction handling, and message sending.
        #
        self.client   = client
        self.category = category
        self.pseudoID = str(category.id)[:8]
        #
        #
        #   Thread/race safety!
        #
        self.mutex = RLock()
		#
		#
		#	The base permissions used by channels in this game.
		#
        self.basePermissions = {
			self.category.guild.default_role: discord.PermissionOverwrite(send_messages=False),
			self.category.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
		}
        #
        #
        #   The bot interfaces to the users in these channels.
		#	The board is read-only, and only players can chat in the game chat.
        #
        _gameChatPermissions = self.basePermissions.copy()
        for player in players:
            _gameChatPermissions.update( {player: discord.PermissionOverwrite(send_messages=True) } )
        self.gameChatChannel = await self.category.create_text_channel("game-chat", overwrites=_gameChatPermissions)
        self.boardImgChannel = await self.category.create_text_channel("board-state", overwrites=self.basePermissions)
        #
        #
        #   The list of players simply maps players to seats.
		#	The private channels are only accessible for the given player.
        #
        self.size    = len(players)
        random.shuffle(players)
        #self.players_by_seat = {}

        self.players = players
        self.privateChannels = []
        for i in range(0, self.size):
            _n       = i + 1
            _pvtperm = self.basePermissions.copy()
            _pvtadds = {
				self.category.guild.default_role: discord.PermissionOverwrite(read_messages=False),
				players[i]: discord.PermissionOverwrite(read_messages=True, send_messages=True)
			}
            _pvtperm.update(_pvtadds)
            _ch      = await self.category.create_text_channel("seat-{n}".format(n=_n), overwrites=_pvtperm)
            self.privateChannels.append(_ch)
        #
        #
        #   The seats in the game, which contain the info and are
        #   mapped against self.players. This information is set
        #   during the premise SHGameComponent, since the roles
        #   are dependent on the variant. However, each role
        #   invariably boils down to either the Liberal or Fascist
        #   archetype, since the bot is limited to a two-team game.
        #
        #   Stores data about each player in a game.
        #   Format:
        #   {
        #       seat_number : {
        #           data_1: ___
        #           data_2: ___  
        #       }, 
        #       next_seat_number : {
        #           ...
        #       }
        #       ...
        #   }
        #
        self.s_seats = {}
        for i in range(0, self.size):
            _n      = i + 1
            data    = {
                "player_reference": players[i],
                "name": "**" + players[i].name + " {" + str(i+1) + "}**",
                "role": None,
                "alive": True,
                "has_voted": False
            }
            self.s_seats[_n] = data
        #
        #
        #   The SHBoard holds the configuration and state
        #   of the board. It has an matrix of the component
        #   layout, and the state of the game.
        #
        #   The SHDeck holds the initial and current state of
        #   the deck. The configuration can control policy counts.
        #
        _config    = DEFAULT_PRESETS[self.size] if preset == None or preset == "default" else "{root}/{pre}.json".format(root=PRESET_PATH, pre=preset)
        self.board = SHBoard(preset=_config, parent=self, client=self.client, size=self.size)
        self.deck  = SHDeck(_config)
        #
        #
        #   The array of SHGameComponents that are currently active,
        #   i.e. being used in the flow. They are retrieved from the
        #   SHBoard based on the state.
        #
        self.activeComponents = {
            "premise":      None, # invariant
            "tracker":      None, # invariant
            "nomination":   None, # variant
            "voting":       None, # variant
            "passed-gov":   None, # variant
            "failed-gov":   None, # variant
            "legislative":  None, # variant
            "post-policy":  None, # variant
            "policy-power": None  # variant
        }
        #
        #   The current component. The actual objects active at any 
        #   given point in time are in the array, but fetched using the string.
		#	nextComponent and policyPlayed signal to the flow when to 
		#	initialize the next component.
        #
        self.currRef = "premise"
        self.prevRef = None
        self.policyWasPlayed = False
        self.shouldProgress = False


    #
    #   Creates the game channels and assigns permissions.
    #   Also initializes the seats according to the premise
    #   component. Sets the flow to 'nomination'.
    #
    async def Setup(self):
        #
        #   Run setup, which deals roles and proceeds to gov 1.
        #
        await self.activeComponents["premise"].Setup()

    #
    #   Handles input by passing it straight into the active
    #   component.
    #
    #   event : tuple
    #       (bundle, type), where bundle is the data form the client
    #       and type is its type as a string
    #
    async def Handle(self, event):
        #
        #   Lock to force procedural inputs and pass all input
        #   to the active component.
        #
        self.mutex.acquire(blocking=True)

        await self.activeComponents[self.currentRef].Handle(event)

        if (self.policyWasPlayed):
            await self.activeComponents[self.prevRef].Teardown()
            await self.board.UpdateComponents()
            await self.activeComponents[self.currRef].Setup()
            self.policyWasPlayed = False
            self.shouldProgress = False

        if (self.shouldProgress):
            await self.activeComponents[self.prevRef].Teardown()
            await self.activeComponents[self.currRef].Setup()
            self.shouldProgress = False

        self.mutex.release()

    #
    #   Cleans up the game and deletes the category and channels.
    #
    def Teardown(self):

        self.client.loop.create_task(self.gameChatChannel.delete())
        self.client.loop.create_task(self.boardImgChannel.delete())

        for ch in self.privateChannels:
            self.client.loop.create_task(ch.delete())

        self.client.loop.create_task(self.category.delete())

        self.client.loop.create_task(
            msg.send(tag="warning", location=__file__, channel=None, msg_type="plain", delete_after=None,
                     content="Deleting game {uuid}!".format(self.pseudoID)))

    # ...
    # anything else is a helper method!

    async def message_main (self, tag="info", location=None, msg_type="plain", delete_after=None, content=None):
        msg.send(tag=tag, location=location, channel=self.gameChatChannel, msg_type=msg_type, delete_after=delete_after, content=content)

    async def message_seat (self, s_seat_num, 
        tag="info", location=None, msg_type="plain",
        delete_after=None, content=None
    ):
        if 0 <= s_seat_num <= self.size:
            msg.send(tag=tag, location=location, channel=self.privateChannels[s_seat_num - 1], msg_type=msg_type, delete_after=delete_after, content=content)