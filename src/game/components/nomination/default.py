from src.game.components.component_base import SHGameComponent
from src.utils import message as msg

class SHGameComponentNominationDefault (SHGameComponent):

    async def __init__(self, parent, client):
        super(SHGameComponentNominationDefault, self).__init__(parent=parent, client=client)
        # ...

    async def Setup(self):
        # whatever your private state is, set it to default
        
        # TODO insert president's name
        await self.parent.message_main(content="President " + self.parent.s_seats[self.parent.game_data["s_president"]]["name"] + " to select a chancellor.")
        self.private_message = await self.parent.message_seat(self.parent.game_data["s_president"], content="Select a chancellor.")

        # tries to emulate the "one click" feature present on sh.io, for instance
        # 7 buttons pop up each with a seat.
        # 
        # TODO this currently allows illegal picks, those necessarily have to get filtered
        # out later on (in case someone decides to be malicious) but not presenting a TLed
        # seat as an option would be nice, for instance.
        for i in range(self.parent.size):
            print("REQUESTING", self.parent.request_emoji(i+1))
            await self.private_message.add_reaction(self.parent.request_emoji(i + 1))

    async def Handle(self, context):
        if context[0] == "message":
            # TODO allow people to type in text as well?
            pass
        # if they added a reaction
        elif context[0] == "reaction" and context[3] == "add":
            _event = context[1]
            _message = context[2]
            for i in range(self.parent.size):
                # TODO this is incredibly sloppy, f*** emojis
                _expected_emoji_id = self.parent.request_emoji_id(i + 1)

                if _expected_emoji_id is not None and _expected_emoji_id == _event.emoji.id:
                    if self.is_legal_pick(i + 1):
                        _pres = self.parent.game_data["s_president"]
                        _chan = i + 1

                        await self.parent.message_seat(_pres, content="You selected " + self.parent.s_seats[_chan]["name"]) #TODO
                        self.parent.game_data["s_chancellor"] = _chan
                        
                        await self.parent.message_main(content="President " + self.parent.s_seats[_pres]["name"] + " has selected" + 
                                                        " chancellor " + self.parent.s_seats[_chan]["name"] + ". Vote in player chats.")
                        
                        self.parent.UpdateToComponent("voting", False)
                        return
            else:
                await self.parent.message_seat(self.parent.game_data["s_president"], content="Illegal pick.")                

    async def Teardown(self):
        pass

    ##
    # TODO: returns whether a chancellor pick is legal
    #
    def is_legal_pick(self, s_seat_num):
        return 1

    
