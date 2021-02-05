from src.minigames.trivia_component_base import TriviaGameComponent
import random
import asyncio
import math
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
        
        _category = self.question["category"]
        _text = self.question["question"]
        _message_text = "```Category: " + _category + "\n" + _text
        self.question_message = await self.parent.message_main(content=(_message_text + "```"))
        print("Question", _text)
        print("Answer", self.question["answer"])
        await asyncio.sleep(15)
        if self.state != "finished":
            self.state = "hinted"
            await self.question_message.edit(content=(_message_text + "\n" + self.gather_hint(self.question["answer"]) + "```"))
            await asyncio.sleep(15)
            if self.state != "finished":
                self.state = "failed"
                await self.parent.message_main(content=("```Times up! The correct answer was: " + self.question["answer"]) + "```")
                self.parent.game_data["num_failed"] += 1
                if self.parent.game_data["num_failed"] == 15:
                    await self.parent.message_main(content=("```Too many questions failed in a row, stopping```"))
                    return
                await asyncio.sleep(5)
                if self.state != "finished":
                    print(_category + "updating to next, nobody got it")
                    self.parent.UpdateToComponent("question")
                    await self.parent.Handle(None)
                return

    async def Handle(self, context):
        if context[0] == "message":
            _content = context[1].content
            if _content == ".tl":
                msg = self.build_leaderboard()
                await self.parent.message_main(content=msg)
            elif self.state == "asked" or self.state == "hinted":
                if self.is_acceptable_answer(_content, self.question["answer"]):
                    self.state = "finished"
                    _scores = self.parent.game_data["scores"]
                    self.parent.game_data["num_failed"] = 0
                    for participant in _scores:
                        if context[1].author.id == participant.id:
                            _scores[participant] += 1
                            if _scores[participant] == self.parent.num_questions_to_win:
                                self.win(participant)
                            else:
                                _msg = self.question["category"] + "**" + participant.name + "** got it! The answer was: " + self.question["answer"]
                                await self.parent.message_main(content=_msg)
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

    def is_acceptable_answer(self, a, b):
        return "".join(a.split()).lower() == "".join(b.split()).lower()

    def gather_hint(self, answer):
        num_filled = int(math.ceil(len(answer) / 3))
        positions = [x for x in range(len(answer))]
        filled_positions = []
        for x in range(num_filled):
            k = random.choice(positions)
            filled_positions.append(k)
            positions.remove(k)
        return ''.join([answer[p] if (p in filled_positions or answer[p] == " ") else "_" for p in range(len(answer))])


    def build_leaderboard(self):
        s = "```Leaderboard:"
        d = self.parent.game_data["scores"]
        k = list(d.keys())
        k.sort(key=lambda j: d[j], reverse=True)
        for x in k:
            s += "\n" + x.name + ": " + str(self.parent.game_data["scores"][x])
        s += "```"
        return s