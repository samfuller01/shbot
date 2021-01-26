from src.game.components import *

#
#   The controller for everything related to the actual
#   game logic. Controls the board, the component matrix,
#   the policy state, and the active components in the parent.
#
class SHBoard (object):

    def __init__(self, config = None, parent = None, client = None, size = None):
        self.parent = parent
        self.client = client
        self.config = config
        self.size   = size
        #
        #   Abandon hope ye all who enter here (reading the config).
        #
