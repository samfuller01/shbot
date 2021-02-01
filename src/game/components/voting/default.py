from src.game.components.component_base import SHGameComponent
from src.utils import message as msg

class SHGameComponentVotingDefault (SHGameComponent):

    async def __init__(self, parent, client):
        super(SHGameComponentVotingDefault, self).__init__(parent=parent, client=client)
        # ...

    async def Setup(self):
        self.vote_messages = []
        self.has_voted = [] # 0 = no, 1 = yes
        self.vote_value = [] # 0 = nein, 1 = ja

        # message people to vote
        for i in range(self.parent.size):
            msg = await self.parent.message_seat(i + 1, "Vote on the following government:\n" + 
                                "President: " + self.parent.president + "\n" + 
                                "Chancellor: " + self.parent.chancellor)
            self.vote_messages.append(msg)
            self.has_voted.append(0)
            self.vote_value.append(0)
            
        for i in range(self.parent.size):
            await self.vote_messages[i].add_reaction(self.parent.request_emoji("ja"))
            await self.vote_messages[i].add_reaction(self.parent.request_emoji("nein"))
        # record their votes

    async def Handle(self, context):
        if context[0] == "message":
            # TODO allow people to type in text as well?
            pass
        # if they added a reaction
        # TODO allow for unvote, revote messages?
        elif context[0] == "reaction" and context[3] == "add":
            _event = context[1]
            _message = context[2]
            _channel = _message.channel
            # TODO use the ID instead of the channel thanks rsar
            s_seat = self.parent.privateChannels.index(_channel) + 1
            if 1 <= s_seat <= self.parent.size:
                self.has_voted[s_seat - 1] = 1
                if _event.emoji == self.parent.request_emoji("ja"):
                    self.vote_value[s_seat - 1] = 1
                    await self.parent.message_main("Player has voted.")
                    await self.parent.message_seat(s_seat, "Vote **ja** registered.", delete_after=5)
                elif _event.emoji == self.parent.request_emoji("nein"):
                    self.vote_value[s_seat - 1] = 0
                    await self.parent.message_main("Player has voted.")
                    await self.parent.message_seat(s_seat, "Vote **nein** registered.", delete_after=5)
                await self.tally_votes()
            else:
                await self.parent.message_seat(self.parent.president, "Bad emoji")
    
    async def tally_votes(self):
        _counted_votes = 0
        _votes = {
            0: [],
            1: []
        }
        for i in range(self.parent.size):
            s_n  = i + 1
            if self.permitted_to_vote(s_n):
                if self.has_voted[i]:
                    _counted_votes += 1
                    _votes[self.vote_value[i]].append(i)
                else:
                    return
        _message = "Jas: " + ", ".join(list(self.parent.seats[x]["name"] for x in _votes[1])) + "\nNeins:" + ", ".join(list(self.parent.seats[x]["name"] for x in _votes[0]))
        
        _passed = len(_votes[1]) > len(_votes[0])

        if _passed:
            _message = "The vote passed by a margin of " + str(len(_votes[1])) + " to " + str(len(_votes[0])) + ".\n" + _message
            
            await self.parent.message_main(_message)

            # TODO check for hitler win, although this might get done in passed_gov
            # TODO call government_success()
        else:
            _message = "The vote failed by a margin of " + str(len(_votes[1])) + " to " + str(len(_votes[0])) + ".\n" + _message
            await self.parent.message_main(_message)
            # TODO call government_fail()
            
        
            

    ##
    # Returns whether a player is allowed to vote (e.g., maybe they're dead)
    # However, I'm lazy, so it's a TODO
    def permitted_to_vote(self, seat):
        return 1
