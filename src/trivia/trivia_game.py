from src.utils import message as msg
from src.game_all.game_base import Game
from src.game_all.create_component import CreateComponentFromQualified

import random
import discord
from threading import RLock
import json

#
#   Game controller.
#
class TriviaGame (Game):


    async def __init__(self, players=None, client=None, category=None, flags=None, context=None):
        super(TriviaGame, self).__init__(players=players, client=client, category=category, flags=flags, context=context)
        
        _gameChatPermissions = self.basePermissions.copy()
        for player in players:
            print(player.name)
            _gameChatPermissions.update( {player: discord.PermissionOverwrite(read_messages=True) } )
            _gameChatPermissions.update( {player: discord.PermissionOverwrite(send_messages=True) } )
        self.gameChatChannel = await self.category.create_text_channel("game-chat", overwrites=_gameChatPermissions)
        

        f = open("src/trivia/questions.json", "r")
        self.question_bank = json.load(f)
        self.used_questions = set()

        self.s_seats = {}
        for i in range(0, self.size):
            _n      = i + 1
            data    = {
                "player_reference": players[i],
                "name": "**" + players[i].name + "**",
            }
            self.s_seats[_n] = data

        self.componentNames = {
            "premise": "default",
            "question": "default"
        }
        #
        #   The array of GameComponents that are currently active,
        #   i.e. being used in the flow. They are retrieved from the
        #   SHBoard based on the state.
        #
        self.activeComponents = {
            "premise":      None,
            "question":     None
        }
        self.activeComponents["premise"] = await CreateComponentFromQualified(parent=self, context=self.context, game="trivia", slot="premise", name="default")

        #
        #   The current component. The actual objects active at any 
        #   given point in time are in the array, but fetched using the string.
		#	nextComponent and policyPlayed signal to the flow when to 
		#	initialize the next component.
        #

        self.parse_flags()

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

        

        if self.shouldProgress:
            self.shouldProgress = False
            await self.activeComponents[self.prevRef].Teardown()
            if self.refresh:
                self.refresh = False
                _comp_name = self.componentNames[self.currRef]
                if _comp_name == None:
                    _comp_name = "default"
                self.activeComponents[self.currRef] = await CreateComponentFromQualified(parent=self, context=self.context, game="trivia", slot=self.currRef, name=_comp_name)
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

    ##
    # Updates to the game component specified by "name." If
    # refresh is set to true, loads a new copy of the component
    # from scratch, as opposed to re-using the old one, sort of a
    # shorthand of board.UpdateComponents in SHGame.
    #
    def UpdateToComponent(self, name=None, refresh=False):
        self.prevRef         = self.currRef
        self.currRef         = name
        self.shouldProgress  = True
        self.refresh         = refresh

    async def message_main (self, tag="info", location=None, msg_type="plain", delete_after=None, content=None):
        return await msg.send(tag=tag, location=location, channel=self.gameChatChannel, msg_type=msg_type, delete_after=delete_after, content=content)

    def request_emoji(self, name):
        return None
    
    def request_emoji_id(self, name):
        return None

    def parse_flags(self, flags):
        
        self.set("win", 10)
        if "w" in flags:
            try:
                x = int(flags["w"])
                if 0 < x < 100:
                    self.set("win", x)
            except Exception as e:
                pass
        
        if "nohint" in flags:
            self.set("no_hint", 1)
        
        