from src.game.components.component_base import SHGameComponent
from src.utils import message as msg

class SHGameComponentPassed_govDefault (SHGameComponent):

    async def __init__(self, parent, client):
        super(SHGameComponentPassed_govDefault, self).__init__(parent=parent, client=client)
        # ...

    async def Setup(self):
        ##
        # Appends this government to the gov history
        #
        self.parent.game_data["s_government_history"].append((self.parent.game_data["s_president"], self.parent.game_data["s_chancellor"]))
        #TODO call legislative session
        
    ##
    # Should not handle any events
    #
    async def Handle(self, context):
        pass

    async def Teardown(self):
        pass