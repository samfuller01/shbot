from src.game.components import *
from src.game.components.component_base import SHGameComponent
from src.game.game_base import aobject

import discord

class SHGameComponentPolicy_powerEmpty (SHGameComponent):


    async def __init__(self, parent, client):
        super(SHGameComponentPolicy_powerEmpty, self).__init__(parent=parent, client=client)
        # ...

    async def Setup(self):
        print("somehow got here? no way")
        self.parent.UpdateToComponent("post_policy", False)
        await self.parent.Handle(None)

    async def Handle(self, context):
        pass

    async def Teardown(self):
        pass
