from definitions import *
from src.game.board import SHBoard
from src.game.deck import SHDeck
from src.utils import message as msg
from src.utils.aobject import aobject

import random
import discord
from threading import RLock



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
    async def __init__(self, players=None, client=None, category=None, preset=None, context=None):
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
			self.category.guild.default_role: discord.PermissionOverwrite(send_messages=False, read_messages=False), 
            # TODO flesh this out ^ (read messages = False, only added to prevent spam notifs for people who have them turned on)
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
        # Stores any and all 'global' data for a game.
        # Use in any component you like, free of charge.
        # 
        self.game_data = {
            "s_president": 1,
            "s_chancellor": None,
            "s_government_history": [],
            "game_over": False
        }
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
            "passed_gov":   None, # variant
            "failed_gov":   None, # variant
            "legislative":  None, # variant
            "post_policy":  None, # variant
            "policy_power": None  # variant
        }
        #
        #   The SHBoard holds the configuration and state
        #   of the board. It has an matrix of the component
        #   layout, and the state of the game.
        #
        #   The SHDeck holds the initial and current state of
        #   the deck. The configuration can control policy counts.
        #
        _config    = DEFAULT_PRESETS[self.size] if preset == None or preset == "default" else "{root}/{pre}.json".format(root=PRESET_PATH, pre=preset)
        self.board = await SHBoard(preset=_config, parent=self, client=self.client, size=self.size, context=context)
        self.deck  = SHDeck(preset=_config)
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

        if event != None: # TODO too hacky? this is for non-awaiting game components
            await self.activeComponents[self.currRef].Handle(event)

        if (self.policyWasPlayed):
            self.policyWasPlayed = False
            self.shouldProgress = False
            await self.activeComponents[self.prevRef].Teardown()
            await self.board.UpdateComponents()
            print(self.activeComponents[self.currRef])
            await self.activeComponents[self.currRef].Setup()

        if (self.shouldProgress):
            self.shouldProgress = False
            await self.activeComponents[self.prevRef].Teardown()
            print("setting up " + self.currRef)
            await self.activeComponents[self.currRef].Setup()

        self.mutex.release()

    #
    #   Cleans up the game and deletes the category and channels.
    #
    async def Teardown(self):

        await self.gameChatChannel.delete()
        await self.boardImgChannel.delete()

        for ch in self.privateChannels:
            await ch.delete()

        await self.category.delete()

        await msg.send(tag="warning", location=__file__, channel=None, msg_type="plain", delete_after=None,
                     content="Deleting game {uuid}!".format(uuid=self.pseudoID))

    # ...
    # anything else is a helper method!

    def UpdateToComponent(self, name=None, policyPlayed=False):
        self.prevRef         = self.currRef
        self.currRef         = name
        self.shouldProgress  = True
        self.policyWasPlayed = policyPlayed
    

    ##
    # Enacts a given policy (of type 1 or 0, or as specified
    # in SHDeck. If fire_event is set to true, instructs
    # this object to handle a dummy Event.
    #
    async def enact_policy(self, policy_type, was_topdecked=False, fire_event=True):
        print("got here 1.5")
        _board = self.board
        _policy_emoji = None
        print(policy_type)
        print("got here 2")
        if policy_type == 0: # TODO Magic numbers, to an extent.
            _board.policiesPlayed["Liberal"] += 1
            _board.lastPolicy = "Liberal"
            _policy_emoji = self.request_emoji("L")
        elif policy_type == 1:
            _board.policiesPlayed["Fascist"] += 1
            _board.lastPolicy = "Fascist"
            _policy_emoji = self.request_emoji("F")
        else:
            return
        
        _msg = "A " + _policy_emoji + " policy has been enacted."
        _msg += str(_board.policiesPlayed[_board.lastPolicy]) + "/" + str(_board.board_lengths[_board.lastPolicy]) + ")."

        print("got here 3")

        await self.message_main(content=_msg)
        ##
        # If we topdecked a policy, no power should activate, so we go straight to
        # post_policy. If it was played, then load the policy_power component.0
        #
        if was_topdecked:
            self.UpdateToComponent("post_policy", True)
        else:
            self.UpdateToComponent("policy_power", True)

        ##
        # If we got here from a Setup() call, then kickstart another event
        # to handle it.
        #
        if fire_event:
            await self.Handle(None)

    async def message_main (self, tag="info", location=None, msg_type="plain", delete_after=None, content=None):
        return await msg.send(tag=tag, location=location, channel=self.gameChatChannel, msg_type=msg_type, delete_after=delete_after, content=content)


    async def message_seat (self, s_seat_num,
        tag="info", location=None, msg_type="plain",
        delete_after=None, content=None
    ):
        if 0 <= s_seat_num <= self.size:
            return await msg.send(tag=tag, location=location, channel=self.privateChannels[s_seat_num - 1], msg_type=msg_type, delete_after=delete_after, content=content)

    def request_emoji(self, name):
        if name == 1:
            return "<:bridge_at_dawn:804837797848416317>"
        elif name == 2:
            return "<:bridge_at_day:804838279206797362>"
        elif name == 3:
            return "<:bridge_at_dusk:804831260685893672>"
        elif name == 4:
            return "<:rainbow_bridge:806005320476131328>"
        elif name == 5:
            return "<:snowy:804985355111628810>"
        elif name == 6:
            return "<:stormy:805302129580441641>"
        elif name == 7:
            return "<:jerry:808102741309128734>"
        elif name == "ja":
            return "<:ja:799071595615748106>"
        elif name == "nein":
            return "<:nein:799071624749907970>"
        elif name == "F":
            return "<:fas:799478022478626826>"
        elif name == "L":
            return "<:lib:799478022586892358>"
        else:
            return None
    
    def request_emoji_id(self, name):
        if name == 1:
            return 804837797848416317
        elif name == 2:
            return 804838279206797362
        elif name == 3:
            return 804831260685893672
        elif name == 4:
            return 806005320476131328
        elif name == 5:
            return 804985355111628810
        elif name == 6:
            return 805302129580441641
        elif name == 7:
            return 808102741309128734
        elif name == "ja":
            return 799071595615748106
        elif name == "nein":
            return 799071624749907970
        elif name == "F":
            return 799478022478626826
        elif name == "L":
            return 799478022586892358
        else:
            return None

    # yo this is absolute garbage
    def request_emoji_value(self, emoji):
        for i in [1, 2, 3, 4, 5, 6, 7, "ja", "nein", "F", "L"]:
            if emoji.id == self.request_emoji_id(i):
                return i
        return None