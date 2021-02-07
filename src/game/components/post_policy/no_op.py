from src.game.components import *
from src.game.components.component_base import SHGameComponent
from src.game.game_base import aobject

import discord

class SHGameComponentPost_policyNo_op (SHGameComponent):


    async def __init__(self, parent, client):
        super(SHGameComponentPost_policyNo_op, self).__init__(parent=parent, client=client)
        # ...

    async def Setup(self):
        _board = self.parent.board
        _last_policy_played = _board.lastPolicy # TODO standardize policy naming convention.
                                                           # (0 / 1 vs. "Fascist"/"Liberal")
        if _board.policiesPlayed[_last_policy_played] >= _board.board_lengths[_last_policy_played]:
            self.parent.end_game(code=1)
        else:
            self.parent.UpdateToComponent("tracker")
            await self.parent.Handle(None)
        

    async def Handle(self, context):
        pass

    async def Teardown(self):
        pass
