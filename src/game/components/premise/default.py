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
        super(parent, client)
        # ...
    
    async def Setup(self, parent, client):
        _roles = list(x for x in get_base_roles(parent.size))
        _num_fascists = sum([1 for x in _roles if x == "F"])
        random.shuffle(_roles)
        for i in range(parent.size):
            _n = i+1
            self.seats[_n]["role"] = roles[i]
            msg = "The game begins and you receive the " + get_role_name(roles[i]) + " role."
            if roles[i] == "H":
                msg += "\nThere are **" + str(_num_fascists) + " Fascists, they know who you are."
            elif roles[i] == "F":
                for j in range(parent.size):
                    if roles[j] == "F" and j != i:
                        msg += "\nYou see that " + parent.seats[j+1]["name"] + " is also a **Fascist.**"
                for j in range(self.num_players):
                    if roles[j] == "H" and j != i:
                        msg += "\nYou see that " + parent.seats[j+1]["name"] + " is **Hitler.** They " + 
                                    "do not know who you are."
            #message this to the player
        
                



