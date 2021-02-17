from src.minigames.trivia_component_base import TriviaGameComponent
import random
import asyncio
import math
import discord

#
# Asks a trivia question. Maintains an internal "state"
# that is either:
# "asked" -> question has been asked but no hint has been given
# "hinted" -> a hint has been given
# "failed" -> nobody guessed the question.
# "finished" -> question has been guessed.

class TriviaComponentQuestionDefault(TriviaGameComponent):

    async def __init__(self, parent, client):
        super(TriviaComponentQuestionDefault, self).__init__(parent=parent, client=client)
        # ...

    async def Setup(self):
        self.state = "asked"
        self.question = self.generate_question()
        
        
        self.question_message = await self.parent.message_main(msg_type="embed", content=self.format_question(show_hint=False))
        #print("Question", _text)
        print("Answer", self.question["answer"])
        await asyncio.sleep(15)
        if self.state != "finished":
            self.state = "hinted"
            await self.question_message.edit(embed=self.format_question(show_hint=True))
            await asyncio.sleep(15)
            if self.state != "finished":
                self.state = "failed"
                await self.parent.message_main(msg_type="embed", content=self.format_fail())
                self.parent.game_data["num_failed"] += 1
                if self.parent.game_data["num_failed"] == 15:
                    await self.parent.message_main(content=("```Too many questions failed in a row, stopping```"))
                    return
                await asyncio.sleep(5)
                if self.state != "finished":
                    #print(_category + "updating to next, nobody got it")
                    self.parent.UpdateToComponent("question")
                    await self.parent.Handle(None)
                return

    async def Handle(self, context):
        if context[0] == "message":
            _content = context[1].content
            if _content == ".tl":
                msg = self.build_leaderboard()
                await self.parent.message_main(msg_type="embed", content=msg)
            elif self.state == "asked" or self.state == "hinted":
                if self.is_acceptable_answer(_content, self.question["answer"]):
                    self.state = "finished"
                    _scores = self.parent.game_data["scores"]
                    self.parent.game_data["num_failed"] = 0
                    for participant in _scores:
                        if context[1].author.id == participant.id:
                            _scores[participant] += 1
                            if _scores[participant] == self.parent.num_questions_to_win:
                                await self.parent.message_main(msg_type="embed", content=self.format_question_victory(participant.name, True))
                            else:
                                await self.parent.message_main(msg_type="embed", content=self.format_question_victory(participant.name, False))
                                await asyncio.sleep(5)
                                self.parent.UpdateToComponent("question")
                            break
                    else:
                        _scores[participant] = 1

    async def Teardown(self):
        pass

    def generate_question(self):
        q_pos = random.randrange(0, len(self.parent.question_bank))
        q = self.parent.question_bank[q_pos]
        del self.parent.question_bank[q_pos]
        return q

    def format_question(self, show_hint=False):
        embed = discord.Embed(title="Trivia Game", colour=discord.Colour(0xb04097))
        _question = self.question["question"]
        _category = self.question["category"]
        embed.add_field(name="Category", value=_category, inline=False)
        if show_hint:
            embed.add_field(name="Question", value=(_question + "\n\n" + self.gather_hint(self.question["answer"])), inline=False)
        else:
            embed.add_field(name="Question", value=_question, inline=False)
            
        return embed

    def format_fail(self):
        embed = discord.Embed(title="Trivia Game", colour=discord.Colour(0xFF7777))
        embed.add_field(name="\u200b", value=("Time's up! The answer was: **" + self.question["answer"] + "**"))
        return embed

    def format_question_victory(self, player_name=None, won_the_game=False):
        embed = discord.Embed(title="Trivia Game", colour=discord.Colour(0x77FF77))
        if won_the_game:
            embed.add_field(name="\u200b", value=("**" + player_name + "** guessed it and WON the game! The answer was: **" + self.question["answer"] + "**"))
        else:
            embed.add_field(name="\u200b", value=("**" + player_name + "** guessed it! The answer was: **" + self.question["answer"] + "**"))
        return embed

    def is_acceptable_answer(self, a, b):
        _mod_a = "".join(a.split()).lower()
        _mod_b = "".join(b.split()).lower()
        _lev_dist = self.levenshtein_dist(_mod_a, _mod_b)
        _len_shorter_word = min(len(a), len(b))
        print(_lev_dist)
        return _lev_dist / _len_shorter_word < 0.2

    def gather_hint(self, answer):
        num_filled = int(math.ceil(len(answer) / 3))
        positions = [x for x in range(len(answer))]
        filled_positions = []
        for x in range(num_filled):
            k = random.choice(positions)
            filled_positions.append(k)
            positions.remove(k)

        l = []
        for p in range(len(answer)):
            if answer[p] == " ":
                l.append("   ")
            elif p in filled_positions:
                l.append(answer[p] + " ")
            else:
                l.append("\_ ")
            print(l)
        print(''.join(l))
        return ''.join(l)


    def build_leaderboard(self):
        fields = []

        s = ""
        d = self.parent.game_data["scores"]
        k = list(d.keys())
        k.sort(key=lambda j: d[j], reverse=True)
        for x in k:
            _points = self.parent.game_data["scores"][x]
            s += "**" + x.name + "** has " + str(_points) + (" point" if x == 1 else " points")

        embed = discord.Embed(title="Trivia Game", colour=discord.Colour(0xb04097))

        embed.add_field(name="Leaderboard", value=s)
        return embed

    def get_color_of_embed(self):
        return 255

    # returns the levenshtein distance between two strings a and b
    def levenshtein_dist(self, s1, s2):
        arr = []
        for i in range(len(s1) + 1):
            b = [0 for j in range(len(s2) + 1)]
            arr.append(b)
        for i in range(len(s1) + 1):
            arr[i][0] = i
        for i in range(len(s2) + 1):
            arr[0][i] = i

        for i in range(len(s1)):
            for j in range(len(s2)):
                cost = 0 if s1[i] == s2[j] else 1
                value = min(arr[i][j]+cost, min(arr[i][j+1] + 1, arr[i+1][j] + 1))
                arr[i+1][j+1] = value
        return arr[len(s1)-1][len(s2)-1]
        
