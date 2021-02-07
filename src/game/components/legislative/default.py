from src.game.components.component_base import SHGameComponent
from src.utils import message as msg

class SHGameComponentLegislativeDefault (SHGameComponent):

    async def __init__(self, parent, client):
        super(SHGameComponentLegislativeDefault, self).__init__(parent=parent, client=client)
        # ...

    async def Setup(self):
        self.draw = self.parent.deck.draw(3)
        print("ok but i got here ya?")
        await self.deal_to_president()

    async def Handle(self, context):
        if context[0] == "message":
            # TODO allow people to type in text as well?
            pass
        # if they added a reaction
        elif context[0] == "reaction" and context[3] == "add":
            _event = context[1]
            _message = context[2]
            for i in range(len(self.draw)):
                if _event.emoji.id == self.parent.request_emoji_id(i + 1):
                    if self.status == "await_president_discard":
                        _discarded_card = self.draw[i]
                        del self.draw[i]
                        self.parent.deck.discard_policy(_discarded_card)
                        await self.deal_to_chancellor()
                        return
                    elif self.status == "await_chancellor_discard":
                        _played_card = self.draw.pop(i)
                        for card_remaining in self.draw: # should always be 1 element only, but why not
                            self.parent.deck.discard_policy(card_remaining)
                        self.status = "enacted"
                        self.enact_policy_via_player(_played_card)
                        self.parent.UpdateToComponent("policy_power", True)
                        return
            else:
                if self.status == "await_president_discard":
                    await self.parent.message_seat(self.parent.game_data["s_president"], content="Illegal discard.")
                elif self.status == "await_chancellor_discard":
                    await self.parent.message_seat(self.parent.game_data["s_chancellor"], content="Illegal discard.")

    async def Teardown(self):
        pass

    ##
    # Shows the president their draw, and sets a flag
    # indicating that it is the president's turn to discard.
    # Could in theory be combined into one method with deal_to_chancellor
    # as much of the code is repeated.
    #
    async def deal_to_president(self):
        _fas_emoji = self.parent.request_emoji("F")
        _lib_emoji = self.parent.request_emoji("L")
        print("draw", self.draw)
        _draw_contents = ''.join([_fas_emoji if x == 1 else _lib_emoji for x in self.draw])
        _message_content = "Your draw: " + _draw_contents + "\nChoose a policy to discard."
        self.private_message = await self.parent.message_seat(self.parent.game_data["s_president"], content=_message_content)
        self.status = "await_president_discard"
        for i in range(len(self.draw)):
            await self.private_message.add_reaction(self.parent.request_emoji(i + 1))

    ##
    # Shows the chancellor their draw, and sets a flag
    # indicating that it is the chancellor's turn to discard.
    #
    async def deal_to_chancellor(self):
        _fas_emoji = self.parent.request_emoji("F")
        _lib_emoji = self.parent.request_emoji("L")
        _draw_contents = ''.join([_fas_emoji if x == 1 else _lib_emoji for x in self.draw])
        _message_content = "Your draw: " + _draw_contents + "\nChoose a policy to play."
        self.private_message = await self.parent.message_seat(self.parent.game_data["s_chancellor"], content=_message_content)
        self.status = "await_chancellor_discard"
        for i in range(len(self.draw)):
            await self.private_message.add_reaction(self.parent.request_emoji(i + 1))

    ##
    # Enacts a policy of the given type, as specified in SHDeck.
    # For a default game, this will either be 1 or 0.
    #
    
    def enact_policy_via_player(self, policy_type=None, was_played=True):
        _board = self.parent.board
        if policy_type == 0: # TODO I dislike this.
            _board.policiesPlayed["Liberal"] += 1
            _board.lastPolicy = "Liberal"
            
        elif policy_type == 1:
            _board.policiesPlayed["Fascist"] += 1
            _board.lastPolicy = "Fascist"