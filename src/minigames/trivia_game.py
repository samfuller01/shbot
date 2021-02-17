from src.utils.aobject import aobject
from src.utils import message as msg

import random
import discord
from threading import RLock
import json

from src.minigames.trivia_premise import TriviaComponentPremiseDefault
from src.minigames.trivia_question import TriviaComponentQuestionDefault
from src.minigames.trivia_component_base import TriviaGameComponent
#
#   Game controller.
#
class TriviaGame (aobject):

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
			self.category.guild.default_role: discord.PermissionOverwrite(send_messages=True), #TODO fix this lol 
            # TODO flesh this out ^ (read messages = False, only added to prevent spam notifs for people who have them turned on)
			self.category.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
		}
        #
        #
        #   The bot interfaces to the users in these channels.
		#	The board is read-only, and only players can chat in the game chat.
        #
        _gameChatPermissions = self.basePermissions.copy()
        """for player in players:
            print(player.name)
            _gameChatPermissions.update( {player: discord.PermissionOverwrite(read_messages=True) } )
            _gameChatPermissions.update( {player: discord.PermissionOverwrite(send_messages=True) } )"""
        self.gameChatChannel = await self.category.create_text_channel("game-chat", overwrites=_gameChatPermissions)
        for player in players:
            await self.gameChatChannel.set_permissions(player, read_messages=True)
            await self.gameChatChannel.set_permissions(player, send_messages=True)
        #
        #
        #   The list of players simply maps players to seats.
		#	The private channels are only accessible for the given player.
        #
        self.size    = len(players)

        self.players = players

        f = open("questions.json", "r")
        self.question_bank = json.load(f)
        self.used_questions = set()
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
        self.game_data = {

        }

        self.s_seats = {}
        for i in range(0, self.size):
            _n      = i + 1
            data    = {
                "player_reference": players[i],
                "name": "**" + players[i].name + "**",
            }
            self.s_seats[_n] = data

        #
        #   The array of SHGameComponents that are currently active,
        #   i.e. being used in the flow. They are retrieved from the
        #   SHBoard based on the state.
        #
        self.activeComponents = {
            "premise":      await TriviaComponentPremiseDefault(client=client, parent=self), # invariant
            "question":     await TriviaComponentQuestionDefault(client=client, parent=self)
        }

        #
        #   The current component. The actual objects active at any 
        #   given point in time are in the array, but fetched using the string.
		#	nextComponent and policyPlayed signal to the flow when to 
		#	initialize the next component.
        #
        self.currRef = "premise"
        self.prevRef = None
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

        if (self.shouldProgress):
            self.shouldProgress = False
            await self.activeComponents[self.prevRef].Teardown()
            self.activeComponents[self.currRef] = await TriviaComponentQuestionDefault(client=self.client, parent=self)
            await self.activeComponents[self.currRef].Setup()

        self.mutex.release()

    #
    #   Cleans up the game and deletes the category and channels.
    #
    async def Teardown(self):

        await self.gameChatChannel.delete()

        await self.category.delete()

        await msg.send(tag="warning", location=__file__, channel=None, msg_type="plain", delete_after=None,
                     content="Deleting game {uuid}!".format(uuid=self.pseudoID))

    # ...
    # anything else is a helper method!

    def UpdateToComponent(self, name=None):
        self.prevRef         = self.currRef
        self.currRef         = name
        self.shouldProgress  = True

    async def message_main (self, tag="info", location=None, msg_type="plain", delete_after=None, content=None):
        return await msg.send(tag=tag, location=location, channel=self.gameChatChannel, msg_type=msg_type, delete_after=delete_after, content=content)

    def request_emoji(self, name):
        return None
    
    def request_emoji_id(self, name):
        return None
