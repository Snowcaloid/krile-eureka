from discord.ui import View

class PersistentView(View):
    def __init__(self):
        super().__init__(timeout=None)
        