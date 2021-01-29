from src.game.components import *

import json

#
#   The controller for everything related to the actual
#   game logic. Controls the board, the component matrix,
#   the policy state, and the active components in the parent.
#
class SHBoard (object):

    def __init__(self, preset = None, parent = None, client = None, size = None):
        #
        #   For functionality, keeps a ref to the Game and Client.
        #
        self.parent = parent
        self.client = client
        #
        #   Abandon hope ye all who enter here (reading the preset).
        #
        self.size = size


    #
    #   Updates the active components in the SHGame parent to reflect the behaviour
    #   of the last played policy immediately after the policy-played component is 
    #   finished in the flow. This is called by the active component if and only if
    #   a policy is played. If a slot holds 'None', the current component in that 
    #   slot is not overwritten. If a slot holds the Empty component, the current
    #   component *is* overwritten and the new component is a no-op.
    #
    #   modifies : self.parent.activeComponents
    #
    def UpdateComponents(self):
        pass
