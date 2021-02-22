from src.SH.components import *
from src.SH.components.component_base import SHGameComponent

import discord

class SHGameComponentPolicy_powerEmpty (SHGameComponent):


    async def __init__(self, parent, client):
        super(SHGameComponentPolicy_powerEmpty, self).__init__(parent=parent, client=client)
        # ...

    async def Setup(self):
        self.parent.UpdateToComponent("post_policy", False)
        await self.parent.Handle(None)

    async def Handle(self, context):
        pass

    async def Teardown(self):
        pass
