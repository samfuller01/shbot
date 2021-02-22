from src.SH.components.component_base import SHGameComponent
from src.utils import message as msg

class SHGameComponentPassed_govDefault (SHGameComponent):

    async def __init__(self, parent, client):
        super(SHGameComponentPassed_govDefault, self).__init__(parent=parent, client=client)
        # ...

    async def Setup(self):
        ##
        # Appends this government to the gov history
        #
        self.parent.get("s_government_history").append((self.parent.get("s_president"), self.parent.get("s_chancellor")))
        self.parent.UpdateToComponent("legislative", False)
        print("got here pog?")
        await self.parent.Handle(None)
        
    ##
    # Should not handle any events
    #
    async def Handle(self, context):
        pass

    async def Teardown(self):
        pass