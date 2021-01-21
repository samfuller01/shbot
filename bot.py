# bot.py
import os

import discord
from dotenv import load_dotenv
from enum import Enum
from random import *

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.reactions = True

client = discord.Client(intents=intents)
global game_id
game_id = 1
games = []

def get_base_roles(num_players):
    if num_players == 5:
        return "LLLFH"
    elif num_players == 6:
        return "LLLLFH" 
    elif num_players == 7:
        return "LLLLFHH"
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

class Game():
    def __init__(self, guild):
        self.participants = []
        self.num_players = 0
        self.guild = guild
        print("here")

    def add_player(self, p):
        self.participants.append(p)
    
    async def handle_input(self, message):
        print("got here")
        print(self.status)
        player = message.author
        channel = message.channel
        if player not in self.seats_by_player:
            print("ur not a player")
            return
        if channel not in self.seats_by_channel:
            print("invalid channel")
            return
        author = self.seats_by_channel[channel]
        #author = self.seats_by_player[player]
        text = message.content
        if not text.startswith("."):
            return
        args = text.split(" ")
        try:
            command = args[0]
        except:
            return
        if self.status == "await_nomination" and (command == ".pick" or command == ".p"):
            if author != self.pres_candidate:
                await self.message_seat(author, "you arent the president.")
                return
            if len(args) == 2 and args[1].isdigit():
                seat = int(args[1])
                if seat in self.players_by_seat and seat != self.pres_candidate:
                    if self.players_by_seat[seat]["alive"] and not self.players_by_seat[seat]["TL_chancellor"]:
                        alive_players = self.num_players - sum([0 if self.players_by_seat[seat]["alive"] else 1])
                        if not self.players_by_seat[seat]["TL_pres"] or alive_players <= 5:
                            await self.receive_nomination(seat)
                        else:
                            await self.message_seat(self.pres_candidate, "illegal pick")
                    else:
                        await self.message_seat(self.pres_candidate, "illegal pick")
                else:
                    await self.message_seat(self.pres_candidate, "u suck, try again")
            else:
                await self.message_seat(author, "invalid format")
        if self.status == "await_pres_discard" and (command == ".discard" or command == ".d"):
            if author != self.pres_candidate:
                await self.message_seat(author, "you arent the president.")
                return
            if len(args) == 2 and args[1].isdigit():
                card = int(args[1])
                if card in [1, 2, 3]:
                    await self.pres_discard(card - 1)
                else:
                    await self.message_seat(author, "bad discard")
            else:
                await self.message_seat(author, "invalid format")
        if self.status == "await_chancellor_play" and (command == ".play" or command == ".p"):
            if author != self.chancellor_candidate:
                await self.message_seat(author, "you arent the chancellor lol")
                return
            if len(args) == 2 and args[1].isdigit():
                card = int(args[1])
                if card in [1, 2]:
                    await self.chancellor_play(card - 1)
                else:
                    await self.message_seat(author, "bad discard")
            else:
                await self.message_seat(author, "invalid format")
        if self.status == "await_votes" and (command == ".vote" or command == ".v"):
            if len(args) == 2 and (args[1].lower() == "ja" or args[1].lower() == "j"):
                await self.receive_vote(author, 1)
            elif len(args) == 2 and (args[1].lower() == "nein" or args[1].lower() == "n"):
                await self.receive_vote(author, 0)
            else:
                await self.message_seat(author, "Bad vote, try again")
        if self.status == "await_votes" and (command == ".j" or command == ".ja"):
            await self.receive_vote(author, 1)
        if self.status == "await_votes" and (command == ".n" or command == ".nein"):
            await self.receive_vote(author, 0)
        if self.status == "await_inv" and (command == ".inv" or command == ".i"):
            if author != self.pres_candidate:
                await self.message_seat(author, "you arent the president.")
                return
            if len(args) == 2 and args[1].isdigit():
                thing = int(args[1])
                if thing not in self.presidents or thing == author:
                    await self.message_seat(author, "invalid use of power, try again")
                    return
                invee = self.players_by_seat[args[1]]
                await self.main_channel.send(self.players_by_seat[author]["player"] + " investigates the role of " + invee["player"])
                await self.message_seat(author, "You investigate the role of " + invee["player"] + " and see that they are a " + invee["role"])
                self.policy_cleanup()
                self.nomination_start()
        if self.status == "await_se" and (command == ".se" or command == ".s" or command == ".pres"):
            if author != self.pres_candidate:
                await self.message_seat(author, "you arent the president.")
                return
            if len(args) == 2 and args[1].isdigit():
                thing = int(args[1])
                if thing not in self.presidents or thing == author:
                    await self.message_seat(author, "invalid use of power, try again")
                    return
                SEdplayer = self.players_by_seat[thing]
                await self.main_channel.send(self.players_by_seat[author]["player"] + " chooses to special elect " + SEdplayer["player"])
                await self.message_seat(author, "You have SE'd " + SEdplayer["player"] + ".")
                self.presidents = [SEdplayer] + self.presidents
                self.policy_cleanup()
                self.nomination_start()
        if self.status == "await_peek" and (command == ".peek" or command == ".p"):
            if author != self.pres_candidate:
                await self.message_seat(author, "you arent the president.")
                return
            if len(args) == 1:
                #SEdplayer = self.players_by_seat[args[1]]
                self.policy_cleanup()
                draw_contents = ''.join([(self.fas_emoji if x == "R" else self.lib_emoji) for x in self.pres_draw])

                await self.main_channel.send(self.players_by_seat[author]["player"] + " peeks at the top 3 cards of the deck.")
                await self.message_seat(author, "You peek at the top of the deck and see the following: " + draw_contents)
                #self.presidents = [SEdplayer] + self.presidents
                self.nomination_start()
        if self.status == "await_gun" and (command == ".execute" or command == ".e" or command == ".kill" or command == ".k"):
            if author != self.pres_candidate:
                await self.message_seat(author, "you arent the president.")
                return
            if len(args) == 2 and args[1].isdigit():
                thing = int(args[1])
                if thing not in self.presidents or thing == author:
                    await self.message_seat(author, "invalid use of power, try again")
                    return
                killed_player = self.players_by_seat[thing]
                await self.main_channel.send(self.players_by_seat[author]["player"] + " chooses to execute " + killed_player["player"])
                # TODO remove chat perms
                if killed_player["role"] == "H":
                    await self.end_game(3)
                    return
        if self.status == "await_chancellor_veto":
            if author != self.chancellor_candidate:
                await self.message_seat(author, "no gtfo")
                return
            if len(args) == 1 and (args[1] == ".ja" or args[1] == ".j"):
                await self.main_channel.send("Chancellor " + self.players_by_seat[author]["player"] + " requests to veto this election.")
                self.status == "await_president_veto"
                await self.message_seat(self.pres_candidate, "Would you like to veto both of the policies you sent the chancellor? Type .ja to veto or .nein to force a policy to be played.")
            elif len(args) == 1 and (args[1] == ".nein" or args[1] == ".n"):
                await self.main_channel.send("Chancellor " + self.players_by_seat[author]["player"] + " chooses not to veto this election.")
                await self.enact_policy(self.played_card, True)
        if self.status == "await_president_veto":
            if author != self.chancellor_candidate:
                await self.message_seat(author, "no gtfo")
                return
            if len(args) == 1 and (args[1] == ".ja" or args[1] == ".j"):
                await self.main_channel.send("President " + self.players_by_seat[author]["player"] + " vetoes this election.")
                await self.government_fail()
            elif len(args) == 1 and (args[1] == ".nein" or args[1] == ".n"):
                await self.main_channel.send("President " + self.players_by_seat[author]["player"] + " chooses not to veto this election.")
                await self.enact_policy(self.played_card, True)
    async def prepare_game(self):
        self.status = "preparing"
        o = {
            self.guild.default_role: discord.PermissionOverwrite(read_messages=False)
        }
        self.main_channel = await self.guild.create_text_channel("game-" + str(game_id) + str("-chat"))
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
        self.HZ_requirement = 3
        self.VZ_requirement = 5
        self.init_deck()
        self.discard_pile = []
        self.ja_emoji = 799071595615748106
        self.nein_emoji = 799071624749907970
        self.fas_emoji = "<:fas:799478022478626826>"
        self.lib_emoji = "<:lib:799478022586892358>"

        await self.assign_roles()
        self.policy_boards = get_base_boards(self.num_players)
        print(self.policy_boards)
        self.policies_played = {
            "R": 0,
            "B": 0
        }
        self.presidents = [(x+1) for x in range(self.num_players)] * 40
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
        await channel.send(content)

    async def nomination_start(self):
        """print("president to select a chancellor")
        votes = {}
        for i in range(num_players):
            votes[i] = 0
        self.status = "await_nomination"
        self.prompt_nomination()"""
        print("president to select a chancellor")
        self.played_card = "nothing"
        await self.main_channel.send("President " + self.pres_name + " to select a chancellor.")
        await self.prompt_nomination()
        # more debug messages prolly

    async def prompt_nomination(self):
        await self.message_seat(self.pres_candidate, "Pick a chancellor (using \".pick 1\", for example):")
        self.status = "await_nomination"

    async def receive_nomination(self, nominee):
        self.status = "finished_nomination"
        self.chancellor_candidate = nominee
        self.chancellor_name = self.players_by_seat[nominee]["player"]
        print("President ", self.pres_name, "has selected chancellor", self.chancellor_candidate)
        self.current_gov_message = await self.main_channel.send("President " + self.pres_name + " has selected chancellor " + self.chancellor_name + ". Vote in player chats.")
        #await self.current_gov_message.add_reaction(self.ja_emoji)
        #await self.current_gov_message.add_reaction(self.nein_emoji)
        #self.vote_queue = Queue()
        await self.init_voting()

    async def init_voting(self):
        for i in self.players_by_seat.keys():
            await self.message_seat(i, "Type .vote (j)a or .vote (n)ein on the following government:\n" + 
                                "President: " + self.pres_name + "\n" + 
                                "Chancellor: " + self.chancellor_name)
            self.players_by_seat[i]["has_voted"] = 0
            self.players_by_seat[i]["vote_ja"] = 0
        self.status = "await_votes"

    async def tally_votes(self):
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
            else:
                return
        message = "Jas: " + ', '.join(jas) + "\nNeins: " + ', '.join(neins)
        passed = ja_votes > nein_votes
        if passed:
            message = "The vote passed by a margin of " + str(ja_votes) + " to " + str(nein_votes) + ".\n" + message
            await self.main_channel.send(message)

            if self.policies_played["R"] >= self.HZ_requirement and self.players_by_seat[self.chancellor_candidate]["role"] == "H":
                await self.end_game(2)
                return

            await self.government_success()
            return
        else:
            message = "The vote failed by a margin of " + str(nein_votes) + " to " + str(ja_votes) + ".\n" + message
            await self.government_fail()
            await self.main_channel.send(message)
            return

    # votes: a dictionary of { seat_number : vote } where vote is "ja" or "nein"
    async def receive_vote(self, seat, vote_ja):
        if self.players_by_seat[seat]["has_voted"]:
            await self.main_channel.send(self.players_by_seat[seat]["player"] + " has revoted.")
        else:
            self.players_by_seat[seat]["has_voted"] = 1
            await self.main_channel.send(self.players_by_seat[seat]["player"] + " has voted.")
        self.players_by_seat[seat]["vote_ja"] = vote_ja
        await self.tally_votes() 
    
    async def government_success(self):
        print("government succeeded.")
        self.status = "government_success"
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
        else:
            self.pres_draw = self.deck[0:3]
            self.deck = self.deck[3:]
            draw_contents = ''.join([(self.fas_emoji if x == "R" else self.lib_emoji) for x in self.pres_draw])
            print(''.join([("F" if x == "R" else "L") for x in self.pres_draw]))
            print(self.pres_draw)
            await self.message_seat(self.pres_candidate, "Your draw: " + draw_contents + "\n" +
                                "Type .discard (1, 2, 3) to choose which one to discard.")
        self.status = "await_pres_discard"

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
        self.status = "await_chancellor_play"
    
    async def chancellor_play(self, card_pos):
        self.played_card = self.pres_draw[card_pos]
        self.discard_pile.append(self.pres_draw[1-card_pos])
        self.status = "finished_chancellor_play"
        print("enacting policy" + str(self.played_card))
        if self.policies_played["R"] >= self.VZ_requirement:
            self.status = "await_chancellor_veto"
            await self.message_seat(self.chancellor_candidate, "Would you like to veto both of these policies? Type .ja to veto or .nein to play your policy.")
        else:
            await self.enact_policy(self.played_card, True)

    async def government_fail(self):
        await self.main_channel.send("The election tracker moves forward. (" + str(self.tracker_position + 1) + "/3).")
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
        await self.nomination_start()

    async def update_tracker_on_success(self):
        self.tracker_position = 0
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
            self.players_by_seat[i]["TL"] = 0
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
            await self.main_channel.send("A " + emoji + " has been enacted. (" + str(self.policies_played[policy]) + "/" + 
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

    async def award_power(self, player, power):
        if power == None:
            self.policy_cleanup()
            await self.nomination_start()
        elif power == "peek":
            await self.message_seat(self.pres_candidate, "Type .peek to examine the top 3 cards of the deck.")
            self.status = "await_peek"
        elif power == "inv":
            await self.message_seat(self.pres_candidate, "You must investigate a player. Type .(i)nv 1, for example.")
            self.status = "await_inv"
        elif power == "SE":
            await self.message_seat(self.pres_candidate, "You must choose a player to be the next president. Type .(s)e 1, for example.")
            self.status = "await_se"
        elif power == "gun":
            await self.message_seat(self.pres_candidate, "You must choose a player to execute. Type .(e)xecute 1, for example.")
            self.status = "await_gun"
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
            await self.main_channel.send("**Hitler** has been executed.")
            await self.main_channel.send("**Liberals** win the game.")
        elif status == 3:
            await self.main_channel.send("**Hitler** has been elected chancellor after the third fascist policy was enacted.")
            await self.main_channel.send("**Fascsts** win the game.")
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

        for i in range(self.num_players):
            self.players_by_seat[i+1]["role"] = roles[i]
            await self.message_seat(i+1, "The game begins and you receive the " + get_role_name(roles[i]) + " role.")
        for i in range(self.num_players):
            if roles[i] == "F":
                for j in range(self.num_players):
                    await self.message_seat(i+1, "player " + self.players_by_seat[j+1]["player"] + " role: " + self.players_by_seat[j+1]["role"])

        print(self.players_by_seat)
        



@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

    for guild in client.guilds:
        #print(guild.members)
        print(client.user, "connected to", guild.name, "!")

        monty = guild.get_member(280471970406072320)
        await cleanup(guild)
        #print(guild.roles)
        print(guild.emojis)
        #g = Game()
        
        #for i in range(7)
        #g.add_player
        
        #g = Game()

async def cleanup(guild):
    c = [x for x in guild.channels if (x.name.startswith("game") or x.name.startswith("seat"))]
    for a in c:
        await a.delete()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == "clear":
        deleted = await message.channel.purge(limit=100)

    for game in games:
        await game.handle_input(message)

    if message.content.startswith(".game"):
        players = []
        text = message.content
        while 1:
            start = text.find("<")
            end = text.find(">")
            if start < 0 or end < 0:
                break
            player_id = text[start+3:end]
            #print("searching for", int(player_id))
            member = message.guild.get_member(int(player_id))
            players.append(member)
            print("found", member)
            text = text[end+1:]
        g = Game(message.guild)
        for p in players:
            g.add_player(p)
        games.append(g)
        global game_id
        game_id += 1
        await g.prepare_game()
        await g.start_game()
    
    if message.content == "cleanup":
        await cleanup(message.guild)
    #print(message.mentions)
    #print(message.content)

client.run(TOKEN)
#g = Game()
#for i in range(7):
#    g.add_player("player" + str(i+1))
#
#g.start_game()
