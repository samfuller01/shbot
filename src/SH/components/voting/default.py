from src.SH.components.component_base import SHGameComponent
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
            msg = await self.parent.message_seat(i + 1, content="Vote on the following government:\n" + 
                                "President: " + self.parent.s_seats[self.parent.get("s_president")]["name"] + "\n" + 
                                "Chancellor: " + self.parent.s_seats[self.parent.get("s_chancellor")]["name"])
            self.vote_messages.append(msg)
            self.has_voted.append(0)
            self.vote_value.append(0)
            
        for i in range(self.parent.size):
            print("adding message to position", i, "in vote messages with length", len(self.vote_messages))
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
            _vote = self.parent.request_emoji_value(_event.emoji)
            # TODO use the ID instead of the channel thanks rsar
            s_seat = [x.id for x in self.parent.privateChannels].index(_channel.id) + 1
            if 1 <= s_seat <= self.parent.size:
                self.has_voted[s_seat - 1] = 1
                # If they reacted with ja
                if _vote == "ja":
                    # Update their current vote, and send a message.
                    self.vote_value[s_seat - 1] = 1
                    await self.parent.message_main(content="Player has voted.")
                    await self.parent.message_seat(s_seat, content="Vote **ja** registered.", delete_after=5)
                elif _vote == "nein":
                    # Update their current vote, and send a message.
                    self.vote_value[s_seat - 1] = 0
                    await self.parent.message_main(content="Player has voted.")
                    await self.parent.message_seat(s_seat, content="Vote **nein** registered.", delete_after=5)
                await self.tally_votes()
            else:
                await self.parent.message_seat(self.parent.get("s_president"), "Bad emoji")
    
    async def Teardown(self):
        pass

    async def tally_votes(self):
        _counted_votes = 0
        _votes = {
            0: [],
            1: []
        }
        #for i in range(self.parent.size):
        for i in range(1):
            s_n  = i + 1
            if self.permitted_to_vote(s_n):
                if self.has_voted[i]:
                    _counted_votes += 1
                    _votes[self.vote_value[i]].append(i)
                else:
                    # Returns if anyone who has to vote has not yet voted.
                    return

        # Gets a list of all of the votes of players
        _message = "Jas: " + ", ".join(list(self.parent.s_seats[x + 1]["name"] for x in _votes[1])) + "\nNeins: " + ", ".join(list(self.parent.s_seats[x + 1]["name"] for x in _votes[0]))
        
        # Did the government pass? Jas must be strictly greater than Neins.
        _passed = len(_votes[1]) > len(_votes[0])

        if _passed:
            _message = "The vote passed by a margin of " + str(len(_votes[1])) + " to " + str(len(_votes[0])) + ".\n" + _message
            self.parent.set("tracker_status", "success")
            await self.parent.message_main(content=_message)
            self.parent.UpdateToComponent("passed_gov", False)
        else:
            _message = "The vote failed by a margin of " + str(len(_votes[1])) + " to " + str(len(_votes[0])) + ".\n" + _message
            self.parent.set("tracker_status", "fail")
            await self.parent.message_main(content=_message)
            self.parent.UpdateToComponent("failed_gov", False)
            
    
    ##
    # Returns whether a player is allowed to vote (e.g., maybe they're dead)
    # However, I'm lazy, so it's a TODO
    def permitted_to_vote(self, seat):
        return 1