from src.game.components.component_base import SHGameComponent
import random
#   
# Returns the base role distributions for a classic SH game,
# in string format.
# 
def get_base_roles(num_players):
    if num_players == 5:
        return "LLLFH"
    elif num_players == 6:
        return "LLLLFH" 
    elif num_players == 7:
        return "LLLLFFH"
    elif num_players == 8:
        return "LLLLLFFH"
    elif num_players == 9:
        return "LLLLLFFFH"
    elif num_players == 10:
        return "LLLLLLFFFH"
    else:
        return None

#
# Returns the full names for an abbreviated role.
#
def get_role_name(abbrev):
    if abbrev == "L":
        return "**Liberal**"
    elif abbrev == "F":
        return "**Fascist**"
    elif abbrev == "H":
        return "**Hitler**"

#
# Sets up a classic game of SH.
#
class SHGameComponentPremiseDefault(SHGameComponent):

    async def __init__(self, parent, client):
        super(SHGameComponentPremiseDefault, self).__init__(parent=parent, client=client)
        # ...

    async def Setup(self):
        print("hello i got here")
        _roles = list(x for x in get_base_roles(self.parent.size))
        _num_fascists = sum([1 for x in _roles if x == "F"])
        random.shuffle(_roles)
        #await self.parent.message_main(content="test")
        for i in range(self.parent.size):
            s_n = i+1
            self.parent.s_seats[s_n]["role"] = _roles[i]
            msg = "The game begins and you receive the " + get_role_name(_roles[i]) + " role."
            if _roles[i] == "H":
                _grammar = ("is " + str(_num_fascists) + " **Fascist**,") if _num_fascists == 1 else ("are " + str(_num_fascists) + " **Fascists,**")
                msg += "\nThere " + _grammar + " they know who you are."
            elif _roles[i] == "F":
                for j in range(self.parent.size):
                    if _roles[j] == "F" and j != i:
                        msg += "\nYou see that " + self.parent.s_seats[j+1]["name"] + " is also a **Fascist.**"
                for j in range(self.parent.size):
                    if _roles[j] == "H" and j != i:
                        msg += "\nYou see that " + self.parent.s_seats[j+1]["name"] + " is **Hitler.** They " + "do not know who you are."
            await self.parent.message_seat(s_n, content=msg)
        self.parent.UpdateToComponent("nomination", False)
        await self.parent.Handle(None)

    async def Handle(self, context):
        pass

    async def Teardown(self):
        pass