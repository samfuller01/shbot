def generate_base_preset(players=5, gamemode="default"):
    data = {

    }

    _startingComponents = {
		"premise"      : "default",
		"tracker"      : "default",
		"nomination"   : "default",
		"voting"       : "default",
		"passed_gov"   : "default",
		"failed_gov"   : "default",
		"legislative"  : "default",
		"post_policy"  : "no_op",
		"policy_power" : "empty"
	}

    _libBoard = ["empty"] * 5
    _fasBoard = ["empty"] * 6
    _fasBoard[3] = "execute"
    _fasBoard[4] = "execute"
    if players == 5 or players == 6:
        _fasBoard[2] = "peek_three"
    elif players == 7 or players == 8:
        _fasBoard[1] = "investigation"
        _fasBoard[2] = "special_elect"
    elif players == 9 or players == 10:
        _fasBoard[1] = "investigation"
        _fasBoard[1] = "investigation"
        _fasBoard[2] = "special_elect"
    
    _boards = {
        "Liberal": _libBoard,
        "Fascist": _fasBoard
    }

    data["STARTING_COMPONENTS"] = _startingComponents
    data["BOARDS"] = _boards
    data["HZ_ENTRY"] = 3
    data["VZ_ENTRY"] = 5
    
    # any other game-wide constants should go here.
    
    return data