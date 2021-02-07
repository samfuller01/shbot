from src.game.components.component_base import SHGameComponent
from src.utils import message as msg

class SHGameComponentFailed_govDefault (SHGameComponent):

    async def __init__(self, parent, client):
        super(SHGameComponentFailed_govDefault, self).__init__(parent=parent, client=client)
        # ...

    async def Setup(self):
        _message = "The election fails and the election tracker moves forward. ("
        _message += str("TODO") + "/" + str(3) +")." # TODO

        await self.parent.message_main(content=_message)
        self.parent.UpdateToComponent("tracker", False)
        await self.parent.Handle(None)
    
    async def Handle(self, context):
        pass

    async def Teardown(self):
        pass