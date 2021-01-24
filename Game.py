import discord
from random import *
from resources import *

class Game():
    def __init__(self, guild, id, client):
        self.participants = []
        self.num_players = 0
        self.guild = guild
        self.id = id
        self.client = client
        print("here")

    def add_player(self, p):
        self.participants.append(p)

    async def prepare_game(self):
        self.status = "preparing"
        o = {
            self.guild.default_role: discord.PermissionOverwrite(read_messages=False)
        }
        self.main_channel = await self.guild.create_text_channel("game-" + str(self.id) + str("-chat"), overwrites=o)
        #self.main_channel = await self.guild.create_text_channel("game-" + str(self.id) + str("-chat"))
        await self.init_players()
        self.side_channels = {}
        self.seats_by_channel = {}
        for p in range(len(self.playerList)):
            overwrites = {
                self.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                self.players_by_seat[p+1]["player_reference"]: discord.PermissionOverwrite(read_messages=True)
            }
            temp = await self.guild.create_text_channel("seat-" + str(p+1), overwrites=overwrites)
            self.side_channels[p+1] = temp
            self.seats_by_channel[temp] = p+1

    async def start_game(self):
        print("starting game")
        self.game_over = False
        self.HZ_requirement = 3
        self.VZ_requirement = 5
        self.init_deck()
        self.discard_pile = []
        self.ja_emoji = "<:ja:799071595615748106>"
        self.nein_emoji = "<:nein:799071624749907970>"
        self.fas_emoji = "<:fas:799478022478626826>"
        self.lib_emoji = "<:lib:799478022586892358>"
        #self.deck = ["R", "R", "R", "B"]
        await self.assign_roles()
        self.policy_boards = get_base_boards(self.num_players)
        print(self.policy_boards)
        self.policies_played = {
            "R": 0,
            "B": 0
        }
        self.presidents = [(x+1) for x in range(self.num_players)] * 60
        self.pres_candidate = self.presidents[0]
        self.presidents = self.presidents[1:]
        #self.pres_candidate = 1
        self.pres_name = self.players_by_seat[1]["player"]
        self.tracker_position = 0
        self.max_tracker_position = 3
        self.TLed_picks = []
        self.dead_players = []
        await self.nomination_start()

    async def message_seat(self, seat_num, content):
        channel = self.side_channels[seat_num]
        return await channel.send(content)

    async def nomination_start(self):
        self.played_card = "nothing"
        await self.main_channel.send("President " + self.pres_name + " to select a chancellor.")
        await self.prompt_nomination()
        # more debug messages prolly

    async def prompt_nomination(self):
        await self.message_seat(self.pres_candidate, "Pick a chancellor (using \".pick 1\", for example):")
        
        def check(m):
            player = m.author
            channel = m.channel

            if player not in self.seats_by_player:
                return False
            if channel not in self.seats_by_channel:
                return False
            author = self.seats_by_channel[channel]
            #author = self.seats_by_player[player]
            text = m.content
            if not text.startswith("."):
                return False
            args = text.split(" ")
            try:
                command = args[0]
            except:
                return False
            
            #if author != self.pres_candidate:
            #    return False
            return True
        
        proceed = False
        final_seat = None

        while not proceed:
            msg = await self.client.wait_for('message', check=check)

            text = msg.content
            player = msg.author
            channel = msg.channel
            author = self.seats_by_channel[channel]
            args = text.split(" ")
            command = args[0]

            if command == ".pick" or command == ".p":
                if author != self.pres_candidate:
                    await self.message_seat(author, "you arent the president.")
                    continue
                if len(args) == 2 and args[1].isdigit():
                    seat = int(args[1])
                    if seat in self.players_by_seat and seat != self.pres_candidate:
                        if not self.players_by_seat[seat]["alive"]:
                            await self.message_seat(author, "You picked a dead player.")
                            continue
                        elif self.players_by_seat[seat]["TL_chancellor"]:
                            await self.message_seat(author, "You cannot pick a previous chancellor.")
                            continue
                        else:
                            alive_players = self.num_players - sum([0 if self.players_by_seat[seat]["alive"] else 1])
                            if not self.players_by_seat[seat]["TL_pres"] or alive_players <= 5:
                                final_seat = seat
                                proceed = True #await self.receive_nomination(seat)
                            else:
                                await self.message_seat(author, "You cannot pick a previous president.")
                                continue
                    else:
                        await self.message_seat(author, "You picked an invalid seat.")
                        continue
                else:
                    await self.message_seat(author, "There was a problem with your command.")
                    continue

        await self.receive_nomination(final_seat)
        #self.status = "await_nomination"

    async def receive_nomination(self, nominee):
        #self.status = "finished_nomination"
        self.chancellor_candidate = nominee
        self.chancellor_name = self.players_by_seat[nominee]["player"]
        print("President ", self.pres_name, "has selected chancellor", self.chancellor_candidate)
        self.current_gov_message = await self.main_channel.send("President " + self.pres_name + " has selected chancellor " + self.chancellor_name + ". Vote in player chats.")
        #await self.current_gov_message.add_reaction(self.ja_emoji)
        #await self.current_gov_message.add_reaction(self.nein_emoji)
        #self.vote_queue = Queue()
        await self.init_voting()

    async def init_voting(self):
        vote_messages = {}

        for i in self.players_by_seat.keys():
            msg = await self.message_seat(i, "Vote on the following government (check to make sure your vote registers):\n" + 
                                "President: " + self.pres_name + "\n" + 
                                "Chancellor: " + self.chancellor_name)
            
            vote_messages[msg] = i
            self.players_by_seat[i]["has_voted"] = 0
            self.players_by_seat[i]["vote_ja"] = 0
        #self.status = "await_votes"

        def check(reaction, user):
            msg = reaction.message

            if user not in self.seats_by_player:
                return False
            #if channel not in self.seats_by_channel:
            #    return False
            if msg not in vote_messages:
                return False
            
            return True
        

        expected_votes = 0
        for i in self.players_by_seat.keys():
        #for i in [1]:
            if self.players_by_seat[i]["alive"] == 1:
                expected_votes += 1

        for ms in vote_messages:
            await ms.add_reaction(self.ja_emoji)
            await ms.add_reaction(self.nein_emoji)

        proceed = False
        while not proceed:
            reaction, user = await self.client.wait_for('reaction_add', check = check)

            #author = self.seats_by_player[user]
            author = self.seats_by_channel[reaction.message.channel]
            vote_ja = 0
            if str(reaction.emoji) == self.ja_emoji:
                vote_ja = 1
            elif str(reaction.emoji) == self.nein_emoji:
                vote_ja = 0
            else:
                continue
            #vote_ja = 1 if str(reaction.emoji) == self.ja_emoji else 0

            #print(reaction.emoji)

            #print(vote_ja)

            await self.receive_vote(author, vote_ja)

            num_votes = 0
            for i in self.players_by_seat.keys():
            #alive_players = self.num_players - sum([0 if self.players_by_seat[seat]["alive"] else 1])

            #for i in [1]:
                if self.players_by_seat[i]["has_voted"] and self.players_by_seat[i]["alive"]:
                    num_votes += 1

            print("num_votes", num_votes)
            print("expected", expected_votes)

            if num_votes == expected_votes:
                proceed = True
        
        await self.tally_finished_votes()

    async def tally_finished_votes(self):
        ja_votes = 0
        nein_votes = 0
        jas = []
        neins = []
        
        for i in self.players_by_seat.keys():
        #for i in [1]:
            if self.players_by_seat[i]["has_voted"]:
                if not self.players_by_seat[i]["alive"]:
                    continue
                elif self.players_by_seat[i]["vote_ja"]:
                    ja_votes += 1
                    jas.append(self.players_by_seat[i]["player"])
                else:
                    nein_votes += 1
                    neins.append(self.players_by_seat[i]["player"])
        message = "Jas: " + ', '.join(jas) + "\nNeins: " + ', '.join(neins)
        passed = ja_votes > nein_votes
        if passed:
            message = "The vote passed by a margin of " + str(ja_votes) + " to " + str(nein_votes) + ".\n" + message
            await self.main_channel.send(message)

            if self.policies_played["R"] >= self.HZ_requirement and self.players_by_seat[self.chancellor_candidate]["role"] == "H":
                await self.end_game(2)
                return

            await self.government_success()
            #return
        else:
            message = "The vote failed by a margin of " + str(ja_votes) + " to " + str(nein_votes) + ".\n" + message
            await self.main_channel.send(message)
            await self.government_fail()
            
            #return

    async def receive_vote(self, seat, vote_ja):
        if self.players_by_seat[seat]["has_voted"]:
            #await self.main_channel.send(self.players_by_seat[seat]["player"] + " has revoted.")
            pass
        else:
            self.players_by_seat[seat]["has_voted"] = 1
            await self.main_channel.send(self.players_by_seat[seat]["player"] + " has voted.")
        self.players_by_seat[seat]["vote_ja"] = vote_ja
    
    async def government_success(self):
        print("government succeeded.")
        #self.status = "government_success"
        for i in self.players_by_seat.keys():
            self.players_by_seat[i]["TL_pres"] = 0
            self.players_by_seat[i]["TL_chancellor"] = 0
        self.players_by_seat[self.pres_candidate]["TL_pres"] = 1
        self.players_by_seat[self.chancellor_candidate]["TL_chancellor"] = 1
        await self.president_draw()

    async def president_draw(self):
        if len(self.deck) < 3:
            print("how tf did u get here lol")
            return
        
        self.pres_draw = self.deck[0:3]
        self.deck = self.deck[3:]
        draw_contents = ''.join([(self.fas_emoji if x == "R" else self.lib_emoji) for x in self.pres_draw])
        print(''.join([("F" if x == "R" else "L") for x in self.pres_draw]))
        print(self.pres_draw)
        await self.message_seat(self.pres_candidate, "Your draw: " + draw_contents + "\n" +
                            "Type .discard (1, 2, 3) to choose which one to discard.")

        def check(m):
            player = m.author
            channel = m.channel

            if player not in self.seats_by_player:
                return False
            if channel not in self.seats_by_channel:
                return False
            author = self.seats_by_channel[channel]
            text = m.content
            if not text.startswith("."):
                return False
            args = text.split(" ")
            try:
                command = args[0]
            except:
                return False
            
            return True

        proceed = False
        final_card = None
        while not proceed:
            msg = await self.client.wait_for('message', check=check)

            text = msg.content
            player = msg.author
            channel = msg.channel
            author = self.seats_by_channel[channel]
            args = text.split(" ")
            command = args[0]

            if author != self.pres_candidate:
                await self.message_seat(author, "Error: You can't do that.")
                continue
            if len(args) == 2 and args[1].isdigit():
                card = int(args[1])
                if card in [1, 2, 3]:
                    final_card = card
                    proceed = True
                else:
                    await self.message_seat(author, "Invalid format.")
                    continue
            else:
                await self.message_seat(author, "Invalid format.")
                continue
        await self.pres_discard(final_card - 1)

    async def pres_discard(self, card_pos):
        discarded_card = self.pres_draw[card_pos]
        self.pres_draw.pop(card_pos)
        self.discard_pile.append(discarded_card)
        self.status = "finished_pres_discard"
        await self.chancellor_receive()
    
    async def chancellor_receive(self):
        draw_contents = ''.join([(self.fas_emoji if x == "R" else self.lib_emoji) for x in self.pres_draw])
        await self.message_seat(self.chancellor_candidate, "You received: " + draw_contents + "\n" + 
                                "Type .play (1, 2) to choose which one to play.")
        #self.status = "await_chancellor_play"

        def check(m):
            player = m.author
            channel = m.channel

            if player not in self.seats_by_player:
                return False
            if channel not in self.seats_by_channel:
                return False
            author = self.seats_by_channel[channel]
            text = m.content
            if not text.startswith("."):
                return False
            args = text.split(" ")
            try:
                command = args[0]
            except:
                return False
            
            return True

        proceed = False
        final_card = None
        while not proceed:
            msg = await self.client.wait_for('message', check=check)

            text = msg.content
            player = msg.author
            channel = msg.channel
            author = self.seats_by_channel[channel]
            args = text.split(" ")
            command = args[0]

            if author != self.chancellor_candidate:
                await self.message_seat(author, "Error: You can't do that.")
                continue
            if len(args) == 2 and args[1].isdigit():
                card = int(args[1])
                if card in [1, 2]:
                    final_card = card
                    proceed = True
                else:
                    await self.message_seat(author, "Invalid format.")
                    continue
            else:
                await self.message_seat(author, "Invalid format.")
                continue
        await self.chancellor_play(final_card - 1)
    
    async def chancellor_play(self, card_pos):
        self.played_card = self.pres_draw[card_pos]
        self.discard_pile.append(self.pres_draw[1-card_pos])
        #self.status = "finished_chancellor_play"
        print("enacting policy" + str(self.played_card))
        if self.policies_played["R"] >= self.VZ_requirement:
            #self.status = "await_chancellor_veto"
            await self.message_seat(self.chancellor_candidate, "Would you like to veto both of these policies? Type .ja to veto or .nein to play your policy.")
            def check(m):
                player = m.author
                channel = m.channel

                if player not in self.seats_by_player:
                    return False
                if channel not in self.seats_by_channel:
                    return False
                author = self.seats_by_channel[channel]
                text = m.content
                if not text.startswith("."):
                    return False
                return True
            proceed = False
            while not proceed:
                msg = await self.client.wait_for('message', check=check)
                text = msg.content
                player = msg.author
                channel = msg.channel
                author = self.seats_by_channel[channel]
                args = text.split(" ")
                command = args[0]
                
                if author != self.chancellor_candidate:
                    await self.message_seat(author, "Error: You can't do that.")
                    continue
                if len(args) == 1 and (args[0] == ".ja" or args[0] == ".j"):
                    proceed = True
                    await self.main_channel.send("Chancellor " + self.players_by_seat[author]["player"] + " requests to veto this election.")
                    #self.status == "await_president_veto"
                    await self.message_seat(self.pres_candidate, "Would you like to veto both of the policies you sent the chancellor? Type .ja to veto or .nein to force a policy to be played.")
                    await self.await_president_veto()
                elif len(args) == 1 and (args[0] == ".nein" or args[0] == ".n"):
                    proceed = True
                    await self.main_channel.send("Chancellor " + self.players_by_seat[author]["player"] + " chooses not to veto this election.")
                    await self.enact_policy(self.played_card, True)

        else:
            await self.enact_policy(self.played_card, True)

    async def await_president_veto(self):
        def check(m):
            player = m.author
            channel = m.channel

            if player not in self.seats_by_player:
                return False
            if channel not in self.seats_by_channel:
                return False
            author = self.seats_by_channel[channel]
            text = m.content
            if not text.startswith("."):
                return False
            return True
        proceed = False
        while not proceed:
            msg = await self.client.wait_for('message', check=check)
            text = msg.content
            player = msg.author
            channel = msg.channel
            author = self.seats_by_channel[channel]
            args = text.split(" ")
            command = args[0]

            if author != self.pres_candidate:
                await self.message_seat(author, "Error: You can't do that.")
                continue
            if len(args) == 1 and (args[0] == ".ja" or args[0] == ".j"):
                proceed = True
                await self.main_channel.send("President " + self.players_by_seat[author]["player"] + " vetoes this election.")
                self.discard_pile.append(self.played_card)
                await self.government_fail()
            elif len(args) == 1 and (args[0] == ".nein" or args[0] == ".n"):
                proceed = True
                await self.main_channel.send("President " + self.players_by_seat[author]["player"] + " chooses not to veto this election.")
                await self.enact_policy(self.played_card, True)

    async def government_fail(self):
        await self.main_channel.send("The election tracker moves forward. (" + str(self.tracker_position + 1) + "/" + str(self.max_tracker_position) + ").")
        print("The election fails and the tracker moves forward. moving to next player.")
        await self.update_tracker_on_fail()

    async def update_tracker_on_fail(self):
        self.tracker_position += 1
        self.pres_candidate = self.presidents[0]
        self.presidents = self.presidents[1:]
        print(self.presidents)
        #if self.pres_candidate > len(self.players_by_seat):
        #    self.pres_candidate = 1
        self.pres_name = self.players_by_seat[self.pres_candidate]["player"]
        if self.tracker_position >= self.max_tracker_position:
            await self.tracker_exceeded()
        
        if not self.game_over:
            self.policy_cleanup()
            await self.nomination_start()

    async def update_tracker_on_success(self):
        self.tracker_position = 0
        print(self.presidents)
        self.pres_candidate = self.presidents[0]
        self.presidents = self.presidents[1:]
        #self.pres_candidate = self.pres_candidate + 1
        #if self.pres_candidate > len(self.players_by_seat):
        #    self.pres_candidate = 1
        self.pres_name = self.players_by_seat[self.pres_candidate]["player"]

    async def tracker_exceeded(self):
        top_card = self.deck[0]
        self.deck = self.deck[1:]
        self.tracker_position = 0
        for i in self.players_by_seat.keys():
            self.players_by_seat[i]["TL_pres"] = 0
            self.players_by_seat[i]["TL_chancellor"] = 0
        await self.enact_policy(top_card, False)

    async def enact_policy(self, policy, was_played):
        if policy == "R" or policy == "B":
            print("A", policy, "policy has been enacted.")
            emoji = ""
            if policy == "R":
                emoji = self.fas_emoji
            else:
                emoji = self.lib_emoji
            self.policies_played[policy] += 1
            boards = self.policy_boards
            await self.main_channel.send("A " + emoji + " policy has been enacted. (" + str(self.policies_played[policy]) + "/" + 
                                            str(len(boards[policy])) + ").")
            if self.policies_played["R"] >= len(boards["R"]) or self.policies_played["B"] >= len(boards["B"]):
                await self.end_game(1)
            else:
                print(self.policies_played)
                power = boards[policy][self.policies_played[policy]-1]
                if was_played:
                    if power is not None:
                        await self.award_power(self.pres_candidate, power)
                    else:
                        await self.update_tracker_on_success()
                        self.policy_cleanup()
                        await self.nomination_start()
                else:
                    self.policy_cleanup()
                    #await self.nomination_start()

        else:
            print("error bad policy")

    def policy_cleanup(self):
        if len(self.deck) < 3:
            print("deck has fewer than 3 cards, reshuffling")
            for card in self.discard_pile:
                self.deck.append(card)
            shuffle(self.deck)
            print("new deck: " + str(self.deck))

    async def award_power(self, player, power):
        if power == "peek":
            await self.message_seat(self.pres_candidate, "Type .peek to examine the top 3 cards of the deck.")
            #self.status = "await_peek"
        elif power == "inv":
            await self.message_seat(self.pres_candidate, "You must investigate a player. Type .inv 1, for example.")
            #self.status = "await_inv"
        elif power == "SE":
            await self.message_seat(self.pres_candidate, "You must choose a player to be the next president. Type .se 1, for example.")
            #self.status = "await_se"
        elif power == "gun":
            await self.message_seat(self.pres_candidate, "You must choose a player to execute. Type .execute 1, for example.")
            #self.status = "await_gun"

        def check(m):
            player = m.author
            channel = m.channel

            if player not in self.seats_by_player:
                return False
            if channel not in self.seats_by_channel:
                return False
            author = self.seats_by_channel[channel]
            text = m.content
            if not text.startswith("."):
                return False
            return True

        proceed = False
        while not proceed:
            msg = await self.client.wait_for('message', check=check)
            text = msg.content
            player = msg.author
            channel = msg.channel
            author = self.seats_by_channel[channel]
            args = text.split(" ")
            command = args[0]

            if author != self.pres_candidate:
                await self.message_seat(author, "Error: You can't do that.")
                continue
            if power == "peek":
                if command == ".peek" and len(args) == 1:
                    proceed = True
                    self.policy_cleanup()
                    draw_contents = ''.join([(self.fas_emoji if x == "R" else self.lib_emoji) for x in self.deck[0:3]])

                    await self.main_channel.send(self.players_by_seat[author]["player"] + " peeks at the top 3 cards of the deck.")
                    await self.message_seat(author, "You peek at the top of the deck and see the following: " + draw_contents)
                    #self.presidents = [SEdplayer] + self.presidents
            elif power == "inv":
                if command == ".inv" and len(args) == 2:
                    seat_num = int(args[1])
                    if seat_num not in self.presidents or seat_num == author:
                        await self.message_seat(author, "Error: Invalid use of power. Try again.")
                        continue
                    proceed = True
                    invee = self.players_by_seat[seat_num]
                    await self.main_channel.send(self.players_by_seat[author]["player"] + " investigates the role of " + invee["player"] + ".")
                    await self.message_seat(author, "You investigate the role of " + invee["player"] + " and see that they are a " + invee["role"])
                    self.policy_cleanup()
            elif power == "SE":
                if command == ".se" and len(args) == 2:
                    seat_num = int(args[1])
                    if seat_num not in self.presidents or seat_num == author:
                        await self.message_seat(author, "Error: Invalid use of power. Try again.")
                        continue
                    proceed = True
                    SEdplayer = self.players_by_seat[seat_num]
                    await self.main_channel.send(self.players_by_seat[author]["player"] + " chooses to special elect " + SEdplayer["player"])
                    await self.message_seat(author, "You have SE'd " + SEdplayer["player"] + ".")
                    self.presidents = [seat_num] + self.presidents
                    self.policy_cleanup()
            elif power == "gun":
                if command == ".execute" and len(args) == 2:
                    seat_num = int(args[1])
                    if seat_num not in self.presidents or seat_num == author:
                        await self.message_seat(author, "Error: Invalid use of power. Try again.")
                        continue
                    proceed = True
                    executed_player = self.players_by_seat[seat_num]
                    await self.main_channel.send(self.players_by_seat[author]["player"] + " chooses to execute " + executed_player["player"])
                    # TODO remove chat perms
                    if executed_player["role"] == "H":
                        await self.end_game(3)
                        return
                    self.policy_cleanup()

        await self.update_tracker_on_success()
        await self.nomination_start()
        #self.policy_cleanup()
        #await self.nomination_start()

    async def end_game(self, status):
        self.game_over = 1
        if status == 1:
            if self.policies_played["R"] >= len(self.policy_boards["R"]):
                await self.main_channel.send("**Fascists** win the game.")
            if self.policies_played["B"] >= len(self.policy_boards["B"]):
                await self.main_channel.send("**Liberals** win the game.")
        elif status == 2:
            await self.main_channel.send("**Hitler** has been elected chancellor after the third fascist policy was enacted.")
            await self.main_channel.send("**Fascsts** win the game.")
        elif status == 3:
            await self.main_channel.send("**Hitler** has been executed.")
            await self.main_channel.send("**Liberals** win the game.")
        arr = list(self.players_by_seat[p]["player"] + ": " + get_role_name(self.players_by_seat[p]["role"]) for p in self.players_by_seat.keys())
        await self.main_channel.send('\n'.join(arr))

    def init_deck(self):
        self.deck = []
        for i in range(11):
            self.deck.append("R")
        for i in range(6):
            self.deck.append("B")
        shuffle(self.deck)
        print("".join(str(x) for x in self.deck))

    async def init_players(self):
        self.players_by_seat = {}
        self.seats_by_player = {}
        self.playerList = self.participants[:]
        shuffle(self.playerList)
        self.num_players = len(self.playerList)
        for i in range(self.num_players):
            d = {
                "player_reference": self.playerList[i],
                "player": "**" + self.playerList[i].name + " {" + str(i+1) + "}**",
                "role": None,
                "TL_pres": 0,
                "TL_chancellor": 0,
                "alive": 1,
                "has_voted": 0,
                "vote_ja": 1
            }
            self.players_by_seat[i+1] = d
            self.seats_by_player[self.playerList[i]] = i+1
            await self.main_channel.send(d["player"] + " takes seat " + str(i+1))

        print(self.players_by_seat)
        print(self.seats_by_player)
    
    async def assign_roles(self):
        roles = list(x for x in get_base_roles(len(self.playerList)))
        shuffle(roles)

        print("\n\n\nroles:")
        print(roles)

        for i in range(self.num_players):
            self.players_by_seat[i+1]["role"] = roles[i]
            s = "The game begins and you receive the " + get_role_name(roles[i]) + " role."
            if roles[i] == "L":
                await self.message_seat(i+1, s)
            elif roles[i] == "H":
                num_fascists = 0
                for j in range(self.num_players):
                    if roles[j] == "F":
                        num_fascists += 1
                s += "\nThere are **" + str(num_fascists) + " Fascists**, they know who you are."
                await self.message_seat(i+1, s)
            else:
                fascists = ""
                for j in range(self.num_players):
                    if roles[j] == "F" and j != i:
                        fascists += "\nYou see that " + self.players_by_seat[j+1]["player"] + " is also a **Fascist.**"
                for j in range(self.num_players):
                    if roles[j] == "H" and j != i:
                        fascists += "\nYou see that " + self.players_by_seat[j+1]["player"] + " is **Hitler**. They do not know who you are."
                s += fascists
                await self.message_seat(i+1, s)

            #await self.message_seat(i+1, "The game begins and you receive the " + get_role_name(roles[i]) + " role.")
        """for i in range(self.num_players):
            if roles[i] == "F":
                for j in range(self.num_players):
                    await self.message_seat(i+1, "player " + self.players_by_seat[j+1]["player"] + " role: " + self.players_by_seat[j+1]["role"])
        """
        print(self.players_by_seat)