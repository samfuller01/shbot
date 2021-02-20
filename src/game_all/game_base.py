from definitions import *
from src.utils import message as msg
from src.utils.aobject import aobject

import discord
from threading import RLock

#
#   Game controller.
#
class Game (aobject):

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
    def __init__(self, players=None, client=None, category=None, flags=None, context=None):
        #
        #
        #   The SHGame uses the client and category
        #   to handle channel creation and management,
        #   reaction handling, and message sending.
        #
        self.client   = client
        self.category = category
        self.pseudoID = str(category.id)[:8]
        self.flags = flags
        #
        #
        #   Thread/race safety!
        #
        self.mutex = RLock()
        self.context = context
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
        """_gameChatPermissions = self.basePermissions.copy()
        for player in players:
            _gameChatPermissions.update( {player: discord.PermissionOverwrite(read_messages=True) } )
            _gameChatPermissions.update( {player: discord.PermissionOverwrite(send_messages=True) } )
            # TODO i dont think this actually works yao"""

        self.size    = len(players)

        self.players = players

        
        # 
        # Stores any and all 'global' data for a game.
        # Use in any component you like, free of charge.
        # 
        self.game_data = {
        }

        #
        #   What types of components are being used.
        #
        self.componentNames = {
        }
        #
        #   The array of GameComponents that are currently active,
        #   i.e. being used in the flow.
        #
        self.activeComponents = {
        }
        
        #
        #   The current component. The actual objects active at any 
        #   given point in time are in the array, but fetched using the string.
		#	nextComponent and policyPlayed signal to the flow when to 
		#	initialize the next component.
        #
        self.currRef = None
        self.prevRef = None


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

    def parse_flags(self):
        return

    def get(self, path):
        reference = path.split("/")
        if len(reference) == 0:
            return None
        location = self.game_data
        for x in reference:
            if x in location:
                location = location[x]
            else:
                return None
        return location

    def set(self, path, value):
        reference = path.split("/")
        old_value = self.get(path)
        location = self.game_data
        if len(reference) == 0:
            return None
        
        if len(reference) == 1:
            self.game_data[reference[0]] = value
            return old_value

        for x in range(len(reference) - 1):
            arg = reference[x]
            if arg in location:
                location = location[arg]
            else:
                return None
        
        location[reference[:-1]] = value
        return old_value