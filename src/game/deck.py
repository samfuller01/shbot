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
        
        _preset = json.load(open(preset))
        
        #
        # Still need to decide what the config is, can change if necessary.
        # If there's no data about a custom deck, build a standard one.
        #
        _standard_deck = _preset == None or "deck" not in _preset or _preset["deck"] == None or len(_preset["deck"] == 0)
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

    ##
    # Reshuffles the deck if there are fewer than 3 cards.
    #
    def reshuffle_if_needed(self):
        if len(self.deck) < 3: # TODO magic number
            self.shuffle(True)

    #
    # Shuffles the deck. If include_discard is set to true, also reshuffles
    # in all discarded policies.
    # 
    # modifies: self.deck, self.discard
    #
    def shuffle(self, include_discard = True):
        if include_discard:
            self.deck.extend(self.discard)
            self.discard = []
        random.shuffle(self.deck)

    #
    # Removes n cards from the deck
    # and returns them. 
    #
    def draw(self, n):
        if n > len(self.deck):
            print("something bad happened in deck")
            return []
        else:
            _draw = self.deck[0:n]
            self.deck = self.deck[n:]
            return _draw
    
    #
    # Helper methods
    #
    def discard_policy(self, policy):
        self.discard.append(policy)

    #
    # Returns the emoji representation of a card whose value
    # is given by num.
    #
    def repr_emoji(self, num):
        return None # TODO
