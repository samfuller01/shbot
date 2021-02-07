from src.game.components.component_base import SHGameComponent
from src.utils import message as msg

class SHGameComponentPassed_govHitler_zone (SHGameComponent):

    async def __init__(self, parent, client):
        super( parent, client )
        # ...

    async def Setup(self, parent, client):
        ##
        # Appends this government to the gov history
        #
        parent.game_data["s_government_history"].append((self.parent.game_data["s_president"], self.parent.game_data["s_chancellor"]))

        if parent.s_seats[self.parent.game_data["s_chancellor"]]["role"] == "H":
            # TODO end game
            pass
        else:
            self.parent.UpdateToComponent("legislative", False)
            await self.parent.Handle(None)
        
    ##
    # Should not handle any events
    #
    async def Handle(self, context):
        pass

    async def Teardown(self):
        pass