from board import SHBoard
from definitions import *
from components.create_component import CreateComponent

import random
import discord

#
#   Game controller.
#
class SHGame (object):

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
    def __init__(self, playerIDs, client=None, category=None, preset=None):
    #
        #
        #   The SHGame uses the client and category
        #   to handle channel creation and management,
        #   reaction handling, and message sending.
        #
        self.client   = client
        self.category = category
    #
        #
        #   The list of players simply maps players to seats.
        #
        self.size    = len(playerIDs)
        self.players = random.shuffle(playerIDs)
    #
        config = preset if preset else DEFAULT_PRESETS[self.size]
        #
        #   The SHBoard holds the configuration and state
        #   of the board. It has an matrix of the component
        #   layout, and the state of the game.
        #
        #   The SHDeck holds the initial and current state of
        #   the deck. The configuration can control policy counts.
        #
        self.board = SHBoard(config)
        self.deck  = SHDeck(config)
    #
        #
        #   The array of SHGameComponents that are currently active,
        #   i.e. being used in the flow. They are retrieved from the
        #   SHBoard based on the state.
        #
        self.activeComponents = {
            "premise":      None, # invariant
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
        #
        self.currentComponent = "premise"
    #
        #
        #   The seats in the game, which contain the info and are
        #   mapped against self.players. This information is set
        #   during the premise SHGameComponent, since the roles
        #   are dependent on the variant. However, each role
        #   invariably boils down to either the Liberal or Fascist
        #   archetype, since the bot is limited to a two-team game.
        #
        self.seats = []



    #
    #   Creates the game channels and assigns permissions.
    #   Also initializes the seats according to the premise
    #   component. Sets the flow to 'nomination'.
    #
    def Setup(self):
        pass



    #
    #   Handles input by passing it straight into the active
    #   component.
    #
    #   event : tuple
    #       (bundle, type), where bundle is the data form the client
    #       and type is its type as a string
    #
    def Handle(self, event):
        pass



    #
    #   Cleans up the game and deletes the category and channels.
    #
    def Teardown(self):
        pass

    # ...
    # anything else is a helper method!
