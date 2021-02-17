from src.utils.aobject import aobject
import discord

#
#   Interface for game overlay objects.
#
class TriviaGameComponent (aobject):

    #
    # parent : Game
    #   a ref to this component's parent
    #
    # client : DiscordClient
    #   a ref to the bot client
    #
    def __init__(self, parent=None, client=None):
        self.parent = parent
        self.client = client
        # ...

    #
    # Runs once when the Game reaches this component's part of the flow.
    #
    async def Setup(self):
        pass

    #
    # Runs every time the bot receives any input from an event
    # that occurs in the CategoryChannel owned by this component's 
    # parent Game.
    #
    # context : tuple
    #   (bundle, type), where bundle is the data from the client
    #                   and type is its type as a string
    #
    async def Handle(self, context):
        pass

