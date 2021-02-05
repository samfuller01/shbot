from src.minigames.trivia_component_base import TriviaGameComponent
import random
import asyncio

#
# Sets up a classic game of SH.
#
class TriviaComponentPremiseDefault(TriviaGameComponent):

    async def __init__(self, parent, client):
        super(TriviaComponentPremiseDefault, self).__init__(parent=parent, client=client)
        # ...

    async def Setup(self):
        await self.parent.message_main(content="Starting trivia game in 10 seconds...", delete_after=5)
        _parent_data = self.parent.game_data
        _players = self.parent.players
        _scores = {
        }
        for p in _players:
            _scores[p] = 0
        _parent_data["scores"] = _scores
        _parent_data["num_failed"] = 0

        self.parent.num_questions_to_win = 10
        await asyncio.sleep(10)
        self.parent.UpdateToComponent("question")
        await self.parent.Handle(None)

    async def Handle(self, context):
        pass

    async def Teardown(self):
        pass