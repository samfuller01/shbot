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
        self.size   = size
        #   
        #   Abandon hope ye all who enter here (reading the preset).
        #
        config = json.load(open(preset))
        #
        self.starting_ruleset = config["startingComponents"]
        self.board_configs = {
            "Liberal": config["boards"]["Liberal"],
            "Fascist": config["boards"]["Fascist"]
        }
        self.board_lengths = {
            "Liberal": len(self.board_configs["Liberal"]),
            "Fascist": len(self.board_configs["Fascist"])
        }
        #
        #   An entry into board_config is a list of slots.
        #   Index 0 corresponds to policy 1 on the board.
        #   If a given component is None, it does not overwrite.
        #   If you want a component to do nothing, explicitly
        #   define the Empty component.
        #



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
