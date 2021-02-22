from src.SH.components import *
from src.SH.components.component_base import SHGameComponent

import discord

class SHGameComponentTrackerDefault (SHGameComponent):


    async def __init__(self, parent, client):
        super(SHGameComponentTrackerDefault, self).__init__(parent=parent, client=client)
        self.tracker_pos = 0
        self.parent.set("special_presidents", [])
        # ...

    async def Setup(self):
        ##
        # Since tracker can be Setuped() from several places, this
        # is a flag to keep track of which tracker action to use.
        #

        _status = self.parent.get("tracker_status")
        ##
        # tracker_status is set to "success" in "voting", when a government
        # passes.
        #
        if _status == "success":
            # reset the tracker position
            self.tracker_pos = 0
            # move to the next eligible president
            self.updatePresident()
            self.parent.deck.reshuffle_if_needed()
            # and prompt that president to pick a chancellor
            self.parent.UpdateToComponent("nomination", False)
            await self.parent.Handle(None)
        ##
        # tracker_status is set to "fail" in "voting", when a government
        # fails.
        #
        elif _status == "fail":
            # move the tracker position up by one position
            self.tracker_pos += 1
            # move to the next eligible president
            self.updatePresident()
            # if we need to topdeck, topdeck
            if self.tracker_pos >= 3: # TODO remove magic numbers?
                await self.top_deck()
            
            elif not self.parent.get("game_over"):
                self.parent.deck.reshuffle_if_needed()
                self.parent.UpdateToComponent("nomination", False)
                await self.parent.Handle(None)
        elif _status == "reset":
            self.tracker_pos = 0
            if not self.parent.get("game_over"):
                self.parent.deck.reshuffle_if_needed()
                self.parent.UpdateToComponent("nomination", False)
                await self.parent.Handle(None)

    async def Handle(self, context):
        pass

    async def Teardown(self):
        pass

    def updatePresident(self):
        _spec = self.parent.get("special_presidents")
        if len(_spec) > 0:
            self.parent.set("s_president", _spec[0])
            _spec = _spec[1:]
            self.parent.set("special_presidents", _spec)
        else:
            print("should have gotten here")
            _pres = self.parent.get("s_president")
            acceptable = False
            while not acceptable:
                _pres += 1
                if _pres > self.parent.size:
                    _pres = 1
                if self.parent.s_seats[_pres]["alive"]:
                    acceptable = True
            self.parent.set("s_president", _pres)
    
    def get_next_president(self):
        _pres = self.parent.get("s_president")

    ##
    # Topdecks a card from the deck to the table. TD is guaranteed to 
    # happen BEFORE the deck reshuffles (allowing for 100% winrate plays
    # in a 3r1b deck, for example)
    #
    async def top_deck(self):
        ## 
        # sets the tracker status to an empty third "reset" state.
        # We're already in the tracker component right now, but when
        # a policy gets enacted we're going to reflow from post-policy
        # 
        #  
        self.parent.set("tracker_status", "reset")
        _card = self.parent.deck.draw(1)
        self.parent.deck.reshuffle_if_needed()
        # 
        # Appends a dummy government to the history. This is
        # for the main purpose of evaluating term limits on the
        # most recent government 
        # 
        self.parent.get("s_government_history").append(tuple())

        await self.parent.enact_policy(_card, was_topdecked=True, fire_event=True)