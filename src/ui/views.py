from discord.ui import View

class PersistentView(View):
    """Simple View with no timeout."""
    def __init__(self):
        super().__init__(timeout=None)

class TemporaryView(View):
    """Simple View with 180 seconds timeout."""
    def __init__(self):
        super().__init__(timeout=180)