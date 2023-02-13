from discord import Intents
from discord.ext.commands import Bot
from data.runtime_data import RuntimeData

class Snowcaloid(Bot):
    data: RuntimeData
    recreate_view = None
    
    def __init__(self):
        intents = Intents.all()
        intents.message_content = True
        super().__init__(command_prefix='/', intents=intents)
        self.recreate_view = None
        self.data = RuntimeData()
        
    async def setup_hook(self) -> None:
        if self.recreate_view:
            view = await self.recreate_view(self)
            self.add_view(view)
        
snowcaloid = Snowcaloid()    