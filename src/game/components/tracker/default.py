from src.game.components import *
from src.game.components.component_base import SHGameComponent
from src.game.game_base import aobject

import discord

class SHGameComponentTrackerDefault (SHGameComponent):


    async def __init__(self, parent, client):
        super(SHGameComponentTrackerDefault, self).__init__(parent=parent, client=client)
        # ...

    async def Setup(self):
        pass


    async def Handle(self, context):
        pass

