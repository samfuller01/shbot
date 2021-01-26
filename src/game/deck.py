import json
import random

#
# Controls the deck for a Game. Contains full knowledge about both the deck
# and discard piles (defined explicitly).
#
class SHDeck (object):

    def __init__(self, preset = None):

        #
        # The deck is stored internally as a list of numbers, for a base
        # game with only two types of policies, these are 0 for Liberal
        # and 1 for Fascist. The schema maps numbers to names.
        #
        self.schema = {
            0: "Liberal",
            1: "Fascist"
        }

        self.DEFAULT_LIB_POLICIES = 6
        self.DEFAULT_FAS_POLICIES = 11

        #
        # I'm abandoning hope pogU
        #
        with json.loads(preset) as _preset:
            #
            # Still need to decide what the config is, can change if necessary.
            # If there's no data about a custom deck, build a standard one.
            #
            _standard_deck = _preset == None or "deck" not in _preset or _preset["deck"] == None
                                or len(_preset["deck"] == 0)
            if _standard_deck:
                self.deck = []
                # unused variable "i" :pepeLaugh:
                for i in range(self.DEFAULT_LIB_POLICIES):
                    self.deck.append(0)
                for i in range(self.DEFAULT_FAS_POLICIES):
                    self.deck.append(1)
                self.shuffle(False)
            else:
                pass

            self.discard = []

    #
    # Shuffles the deck. If include_discard is set to true, also reshuffles
    # in all discarded policies.
    # 
    # modifies: self.deeznuts
    #
    def shuffle(self, include_discard = True):
        if include_discard:
            self.deck.extend(self.discard)
            self.discard = []
        random.shuffle(self.deck)


            
