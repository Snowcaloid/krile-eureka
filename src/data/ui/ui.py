from data.ui.ui_eureka_info import UIEurekaInfoPost
from data.ui.ui_embed_builder import UI_Embed_Builder
from data.ui.ui_pl_post import UIPLPost
from data.ui.ui_schedule import UISchedule
from data.ui.ui_signup_recruitment import UISignupRecruitment
from data.ui.ui_view import UIView
from data.ui.ui_weather_info import UIWeatherPost
from data.ui.ui_help import UIHelp


class UI:
    schedule: UISchedule = UISchedule()
    pl_post: UIPLPost = UIPLPost()
    signup_recruitment: UISignupRecruitment = UISignupRecruitment()
    view: UIView = UIView()
    weather_post: UIWeatherPost = UIWeatherPost()
    help: UIHelp = UIHelp()
    embed: UI_Embed_Builder = UI_Embed_Builder()
    eureka_info: UIEurekaInfoPost = UIEurekaInfoPost()

    async def load(self) -> None:
        await self.view.load()