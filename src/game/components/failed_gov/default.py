from src.game.components.component_base import SHGameComponent
from src.utils import message as msg

class SHGameComponentFailed_govDefault (SHGameComponent):

    async def __init__(self, parent, client):
        super(SHGameComponentFailed_govDefault, self).__init__(parent=parent, client=client)
        # ...

    async def Setup(self):
        self.parent.message_main("The election fails.")
        # TODO call tracker to update with a failed gov response.
    
    async def Handle(self, context):
        pass

    async def Teardown(self):
        pass