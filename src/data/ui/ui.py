import bot
from data.ui.ui_missed_run_post import UIMissedRunPost
from data.ui.ui_missed_runs_list import UIMissedRunsList
from data.ui.ui_pl_post import UIPLPost
from data.ui.ui_schedule import UISchedule
from data.ui.ui_view import UIView


class UI:
    schedule: UISchedule = UISchedule()
    missed_runs_list: UIMissedRunsList = UIMissedRunsList()
    missed_run_post: UIMissedRunPost = UIMissedRunPost()
    pl_post: UIPLPost = UIPLPost()
    view: UIView = UIView()

    def load(self) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            self.view.load()
        finally:
            db.disconnect()