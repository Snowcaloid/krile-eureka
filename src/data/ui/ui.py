import bot
from data.ui.ui_eureka_info import UIEurekaInfoPost
from data.ui.ui_embed_builder import UI_Embed_Builder
from data.ui.ui_missed_run_post import UIMissedRunPost
from data.ui.ui_missed_runs_list import UIMissedRunsList
from data.ui.ui_pl_post import UIPLPost
from data.ui.ui_schedule import UISchedule
from data.ui.ui_view import UIView
from data.ui.ui_weather_info import UIWeatherPost
from data.ui.ui_help import UIHelp


class UI:
    schedule: UISchedule = UISchedule()
    missed_runs_list: UIMissedRunsList = UIMissedRunsList()
    missed_run_post: UIMissedRunPost = UIMissedRunPost()
    pl_post: UIPLPost = UIPLPost()
    view: UIView = UIView()
    weather_post: UIWeatherPost = UIWeatherPost()
    help: UIHelp = UIHelp()
    embed: UI_Embed_Builder = UI_Embed_Builder()
    eureka_info: UIEurekaInfoPost = UIEurekaInfoPost()

    async def load(self) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            await self.view.load()
        finally:
            db.disconnect()