#
#   Interface for game overlay objects.
#
class SHGameComponent (object):

    #
    # parent : SHGame
    #   a ref to this component's parent
    #
    # client : DiscordClient
    #   a ref to the bot client
    #
    def __init__(self, parent, client):
        self.stage = None
        self.parent = parent
        self.client = client
        # ...

    #
    # Runs once when the SHGame reaches this component's part of the flow.
    #
    def Setup(self):
        pass

    #
    # Runs every time the bot receives any input from an event
    # that occurs in the CategoryChannel owned by this component's 
    # parent SHGame.
    #
    # context : tuple
    #   (bundle, type), where bundle is the data from the client
    #                   and type is its type as a string
    #
    def Handle(self, context):
        pass

