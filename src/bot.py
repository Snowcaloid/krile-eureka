from discord import Intents
from discord.ext.commands import Bot
from views import PersistentView
from buttons import RoleSelectionButton
from data.runtime_data import RuntimeData

class Snowcaloid(Bot):
    data: RuntimeData
    
    def __init__(self):
        intents = Intents.all()
        intents.message_content = True
        super().__init__(command_prefix='/', intents=intents)
        self.data = RuntimeData()
        
    async def setup_hook(self) -> None:
        view = PersistentView()
        for buttondata in self.data._loaded_view:
            view.add_item(RoleSelectionButton(label=buttondata.label, custom_id=buttondata.button_id))
            
        self.add_view(view)
        
snowcaloid = Snowcaloid()    