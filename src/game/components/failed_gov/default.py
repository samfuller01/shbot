from src.game.components.component_base import SHGameComponent
from src.utils import message as msg

class SHGameComponentFailedGovDefault (SHGameComponent):

    async def __init__(self, parent, client):
        super( parent, client )
        # ...

    async def Setup(self, parent, client):
        parent.message_main("The election fails.")
        # TODO call tracker to update with a failed gov response.