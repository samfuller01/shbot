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
        return "XXXXXXX"

def get_base_boards(num_players):
    liberal_board = [None, None, None, None, None]
    fascist_board = None
    if num_players == 5 or num_players == 6:
        fascist_board = [None, None, "peek", "gun", "gun", None]
    elif num_players == 7 or num_players == 8:
        fascist_board = [None, "inv", "SE", "gun", "gun", None]
    elif num_players == 7 or num_players == 8:
        fascist_board = ["inv", "inv", "SE", "gun", "gun", None]
    return {
        "B": liberal_board,
        "R": fascist_board
    }

def get_role_name(abbrev):
    if abbrev == "L":
        return "**Liberal**"
    elif abbrev == "F":
        return "**Fascist**"
    elif abbrev == "H":
        return "**Hitler**"
    else:
        return "**if you see this something went wrong**"