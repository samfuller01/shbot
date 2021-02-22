from src.SH.components import *
from src.SH.components.component_base import SHGameComponent

import discord

class SHGameComponentPolicy_powerPeek_discard (SHGameComponent):

    async def __init__(self, parent, client):
        super(SHGameComponentPolicy_powerPeek_discard, self).__init__(parent=parent, client=client)
        # ...

    async def Setup(self):
        _top_card = self.parent.deck.peek(1)[0]
        _policy_name = "L" if _top_card == 0 else "F"
        _msg = "You peek at the top card of the deck and see: " + (self.parent.request_emoji(_policy_name) + ". \nVote \"ja\" to discard it, and \"nein\" to replace it on the deck.")
        
        self.private_message = await self.parent.message_seat(self.parent.get("s_president"), content=_msg)
        # Add all of the seats to their name
        for i in ["ja", "nein"]:
            await self.private_message.add_reaction(self.parent.request_emoji(i))

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
                    _card = self.parent.deck.draw(1)[0]
                    self.parent.deck.discard(_card)
                    _pres = self.parent.get("s_president")
                    
                    _msg = "You discard the policy."

                    await self.parent.message_seat(_pres, content=_msg)
                    await self.parent.message_main(content="President " + self.parent.s_seats[_pres]["name"] + " chooses to discard athe top card of the deck.")
                    
                    self.parent.UpdateToComponent("post_policy", False)
                    return
                elif _vote == "nein":
                    _pres = self.parent.get("s_president")
                    
                    _msg = "You replace the policy."

                    await self.parent.message_seat(_pres, content=_msg)
                    await self.parent.message_main(content="President " + self.parent.s_seats[_pres]["name"] + " chooses NOT to discard athe top card of the deck.")
                    
                    self.parent.UpdateToComponent("post_policy", False)
                    return
            else:
                await self.parent.message_seat(self.parent.get("s_president"), content="Error.")

    async def Teardown(self):
        pass