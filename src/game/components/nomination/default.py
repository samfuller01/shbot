from src.game.components.component_base import SHGameComponent

class SHGameComponentNominationDefault (SHGameComponent):

    async def __init__(self, parent, client):
        super( parent, client )
        # ...

    async def Setup(self, parent, client):
        # whatever your private state is, set it to default
        # 
