from src.game.components.component_base import SHGameComponent
from src.utils import message as msg

class SHGameComponentNominationDefault (SHGameComponent):

    async def __init__(self, parent, client):
        super( parent, client )
        # ...

    async def Setup(self, parent, client):
        # whatever your private state is, set it to default
        
        # TODO insert president's name
        parent.send_text(0, "President ___ to select a chancellor.")
        self.private_message = parent.message_seat(channel=parent.game_data["s_president"], content="Select a chancellor.")

        # tries to emulate the "one click" feature present on sh.io, for instance
        # 7 buttons pop up each with a seat.
        # 
        # TODO this currently allows illegal picks, those necessarily have to get filtered
        # out later on (in case someone decides to be malicious) but not presenting a TLed
        # seat as an option would be nice, for instance.
        for i in range(parent.size):
            await self.private_message.add_reaction(parent.request_emoji(i + 1))

    async def Handle(self, context):
        if context[0] == "message":
            # TODO allow people to type in text as well?
            pass
        # if they added a reaction
        elif context[0] == "reaction" and context[3] == "add":
            _event = context[1]
            _message = context[2]
            for i in range(self.parent.size):
                if _event.emoji == self.parent.request_emoji(i + 1):
                    if self.is_legal_pick(i + 1):
                        await self.parent.message_seat(self.parent.game_data["s_president"], "You selected ____") #TODO
                        self.parent.game_data["s_chancellor"] = i + 1
                        # TODO announce nomination
                        # TODO move along to voting stage
            else:
                await self.parent.message_seat(self.parent.game_data["s_president"], "Illegal pick.")                

    ##
    # TODO: returns whether a chancellor pick is legal
    #
    def is_legal_pick(self, s_seat_num):
        return 1
