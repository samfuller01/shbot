from src.game.components import *
from src.game.components.component_base import SHGameComponent
from src.game.game_base import aobject

import discord

class SHGameComponentPolicy_powerInvestigation (SHGameComponent):

    async def __init__(self, parent, client):
        super(SHGameComponentPolicy_powerInvestigation, self).__init__(parent=parent, client=client)
        # ...

    async def Setup(self):
        _msg = "You must investigate a player."
        self.private_message = await self.parent.message_seat(self.parent.game_data["s_president"], content=_msg)
        # Add all of the seats to their name
        for i in range(self.parent.size):
            await self.private_message.add_reaction(self.parent.request_emoji(i + 1))

    async def Handle(self, context):
        if context[0] == "message":
            # TODO allow people to type in text as well?
            pass
        # if they added a reaction
        elif context[0] == "reaction" and context[3] == "add":
            _event = context[1]
            _message = context[2]
            _target = self.parent.request_emoji_value(_event.emoji)

            if _target != None and self.is_legal_pick(_target):
                _pres = self.parent.game_data["s_president"]
                _role = self.parent.s_seats[_target]["role"]
                _msg = "You see the role of player " + self.parent.s_seats[_target]["name"] + " and see: " + str(_role)

                await self.parent.message_seat(_pres, content=_msg)
                
                await self.parent.message_main(content="President " + self.parent.s_seats[_pres]["name"] + " investigates the role of " + 
                                                " player " + self.parent.s_seats[_target]["name"] + ".")
                
                self.parent.UpdateToComponent("post_policy", False)
                return
            else:
                await self.parent.message_seat(self.parent.game_data["s_president"], content="Illegal pick.")

    async def Teardown(self):
        pass

    # TODO 
    def is_legal_pick(self, s_seat_num):
        return 1