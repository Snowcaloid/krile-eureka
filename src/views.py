from discord.ui import View

class PersistentView(View):
    """Simple View with no timeout."""
    def __init__(self):
        super().__init__(timeout=None)
        