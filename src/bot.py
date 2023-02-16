from discord import Intents
from discord.ext.commands import Bot
from data.runtime_data import RuntimeData

class Snowcaloid(Bot):
    """General bot class.

    Properties
    ----------
    data: :class:`RuntimeData` 
        This is where all the data is stored during runtime. 
        The objects stored within this object have the access to the database.
    recreate_view: :class:`coroutine`
        It is called for restoring Button functionality within setup_hook procedure. 
        To recreate the button's functionality, a view is needed to be added to the 
        bot, which includes Buttons with previously existing custom_id's.
    """
    data: RuntimeData
    recreate_view = None
    
    def __init__(self):
        intents = Intents.all()
        intents.message_content = True
        super().__init__(command_prefix='/', intents=intents)
        self.recreate_view = None
        self.data = RuntimeData()
        
    async def setup_hook(self) -> None:
        """A coroutine to be called to setup the bot.
        This method is called after snowcaloid.on_ready event.
        """
        if self.recreate_view:
            views = await self.recreate_view(self)
            for view in views:
                self.add_view(view)
        
snowcaloid = Snowcaloid()    