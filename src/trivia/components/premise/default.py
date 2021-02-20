from src.trivia.components.trivia_component_base import TriviaGameComponent
import random
import asyncio

#
# Sets up a classic game of SH.
#
class TriviaGameComponentPremiseDefault(TriviaGameComponent):

    async def __init__(self, parent, client):
        super(TriviaGameComponentPremiseDefault, self).__init__(parent=parent, client=client)
        # ...

    async def Setup(self):
        await self.parent.message_main(content="Starting trivia game in 3 seconds...", delete_after=3)
        
        _players = self.parent.players
        _scores = {
        }
        for p in _players:
            _scores[p] = 0
        self.parent.set("scores", _scores)
        self.parent.set("num_failed", 0)

        await asyncio.sleep(3)
        self.parent.UpdateToComponent("question", refresh=True)
        await self.parent.Handle(None)

    async def Handle(self, context):
        pass

    async def Teardown(self):
        pass