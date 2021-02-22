from src.SH.components import *
from src.SH.components.component_base import SHGameComponent

import discord

class SHGameComponentPolicy_powerPeek_three (SHGameComponent):

    async def __init__(self, parent, client):
        super(SHGameComponentPolicy_powerPeek_three, self).__init__(parent=parent, client=client)
        # ...

    async def Setup(self):
        _msg = "Click \"ja\" to peek at the top three cards of the deck."
        
        self.private_message = await self.parent.message_seat(self.parent.get("s_president"), content=_msg)
        await self.private_message.add_reaction(self.parent.request_emoji("ja"))

    async def Handle(self, context):
        if context[0] == "message":
            # TODO allow people to type in text as well?
            pass
        # if they added a reaction
        elif context[0] == "reaction" and context[3] == "add":
            _event = context[1]
            _message = context[2]
            _vote = self.parent.request_emoji_value(_event.emoji)

            if _vote != None:
                if _vote == "ja":
                    _draw = self.parent.deck.peek(3)
                    _pres = self.parent.get("s_president")
                    

                    _fas_emoji = self.parent.request_emoji("F")
                    _lib_emoji = self.parent.request_emoji("L")
                    _draw_contents = ''.join([_fas_emoji if x == 1 else _lib_emoji for x in _draw])
                    _msg = "Your peek at the top of the deck and see the following: " + _draw_contents + "."

                    await self.parent.message_seat(_pres, content=_msg)
                    await self.parent.message_main(content="President " + self.parent.s_seats[_pres]["name"] + " peeks at the top three cards of the deck.")
                    

                    self.parent.UpdateToComponent("post_policy", False)
                    return
            else:
                await self.parent.message_seat(self.parent.get("s_president"), content="Error.")

    async def Teardown(self):
        pass