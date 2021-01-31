from src.game.components.component_base import SHGameComponent
from src.utils import message as msg

class SHGameComponentLegislativeDefault (SHGameComponent):

    async def __init__(self, parent, client):
        super( parent, client )
        # ...

    async def Setup(self, parent, client):
        self.draw = parent.deck.draw(3)
        self.deal_to_president()

    async def Handle(self, context):
        if context[0] == "message":
            # TODO allow people to type in text as well?
            pass
        # if they added a reaction
        elif context[0] == "reaction" and context[3] == "add":
            _event = context[1]
            _message = context[2]
            for i in range(len(self.draw)):
                if _event.emoji == self.parent.request_emoji(i + 1):
                    if self.status == "await_president_discard":
                        _discarded_card = self.draw.pop(i)
                        self.parent.deck.discard(_discarded_card)
                        await self.deal_to_chancellor()
                    elif self.status == "await_chancellor_discard":
                        _played_card = self.draw.pop(i)
                        for card_remaining in self.draw: # should always be 1 element only, but why not
                            self.parent.deck.discard(card_remaining)
                        self.enact_policy(_played_card)
            else:
                await self.parent.message_seat(self.parent.game_data["s_president"], "Illegal discard.")

    ##
    # Shows the president their draw, and sets a flag
    # indicating that it is the president's turn to discard.
    # Could in theory be combined into one method with deal_to_chancellor
    # as much of the code is repeated.
    #
    async def deal_to_president(self):
        _draw_contents = ''.join([(self.parent.request_emoji("F") if x == 1 else self.parent.request_emoji("L") for x in self.draw)])
        _message_content = "Your draw: " + _draw_contents + "\nChoose a policy to discard."
        self.private_message = await self.message_seat(self.parent.game_data["s_president"], _message_content)
        self.status = "await_president_discard"
        for i in range(len(self.draw)):
            await self.private_message.add_reaction(self.parent.request_emoji(i + 1))

    ##
    # Shows the chancellor their draw, and sets a flag
    # indicating that it is the chancellor's turn to discard.
    #
    async def deal_to_chancellor(self):
        _draw_contents = ''.join([(self.parent.request_emoji("F") if x == 1 else self.parent.request_emoji("L") for x in self.draw)])
        _message_content = "Your draw: " + _draw_contents + "\nChoose a policy to play."
        self.private_message = await self.message_seat(self.parent.game_data["s_chancellor"], _message_content)
        self.status = "await_chancellor_discard"
        for i in range(len(self.draw)):
            await self.private_message.add_reaction(self.parent.request_emoji(i + 1))

    ##
    # Enacts a policy of the given type, as specified in SHDeck.
    # For a default game, this will either be 1 or 0.
    #
    async def enact_policy(self, policy_type):
        pass #TODO
