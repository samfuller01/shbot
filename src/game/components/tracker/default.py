from src.game.components import *
from src.game.components.component_base import SHGameComponent
from src.game.game_base import aobject

import discord

class SHGameComponentTrackerDefault (SHGameComponent):


    async def __init__(self, parent, client):
        super(SHGameComponentTrackerDefault, self).__init__(parent=parent, client=client)
        self.tracker_pos = 0
        self.parent.game_data["special_presidents"] = []
        # ...

    async def Setup(self):
        print("got here!")
        _status = self.parent.game_data["tracker_status"]
        print("got here! with status", _status)
        if _status == "success":
            self.tracker_pos = 0
            print("updating president")
            self.updatePresident()
            print("updated president")
            self.parent.UpdateToComponent("nomination", False)
            await self.parent.Handle(None)
        elif _status == "fail":
            self.tracker_pos += 1
            self.updatePresident()
            if self.tracker_pos >= 3: # TODO remove magic numbers?
                await self.top_deck_and_reset()
            
            elif not self.parent.game_data["game_over"]:
                self.parent.deck.reshuffle_if_needed()
                self.parent.UpdateToComponent("nomination", False)
                await self.parent.Handle(None)

    async def Handle(self, context):
        pass

    async def Teardown(self):
        pass

    def updatePresident(self):
        _spec = self.parent.game_data["special_presidents"]
        if len(_spec) > 0:
            self.parent.game_data["s_president"] = _spec[0]
            _spec = _spec[1:]
        else:
            print("should have gotten here")
            _pres = self.parent.game_data["s_president"]
            acceptable = False
            while not acceptable:
                _pres += 1
                if _pres > self.parent.size:
                    _pres = 1
                if self.parent.s_seats[_pres]["alive"]:
                    acceptable = True
            self.parent.game_data["s_president"] = _pres
    
    async def top_deck_and_reset(self):
        _card = self.parent.deck.draw(1)
        self.parent.deck.reshuffle_if_needed()
        self.tracker_pos = 0
        self.parent.game_data["s_government_history"].append(tuple())
        self.enact_policy_via_topdeck(_card)

        self.parent.UpdateToComponent("post_policy", False)
        await self.parent.Handle(None)

    ##
    # Currently no difference between this function and the one
    # in legislative.default (other than name). Imo still good
    # practice to keep them separate because combining them
    # would create an odd dependency.
    #
    def enact_policy_via_topdeck(self, policy_type):
        _board = self.parent.board
        if policy_type == 0: # TODO I dislike this.
            _board.policiesPlayed["Liberal"] += 1
            _board.lastPolicy = "Liberal"
            
        elif policy_type == 1:
            _board.policiesPlayed["Fascist"] += 1
            _board.lastPolicy = "Fascist"
        
        