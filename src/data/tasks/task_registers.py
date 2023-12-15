
from data.tasks.update_status_1 import Task_UpdateStatus
from data.tasks.send_pl_passcodes_2 import Task_SendPLPasscodes
from data.tasks.remove_old_run_3 import Task_RemoveOldRun
from data.tasks.remove_old_message_4 import Task_RemoveOldMessage
from data.tasks.post_main_passcode_5 import Task_PostMainPasscode
from data.tasks.post_support_passcode_6 import Task_PostSupportPasscode
from data.tasks.update_missed_runs_list_7 import Task_UpdateMissedRunsList
from data.tasks.remove_buttons_8 import Task_RemoveButtons
from data.tasks.update_weather_posts_9 import Task_UpdateWeatherPosts


class TaskRegisters:
    @classmethod
    def register_all(cl) -> None:
        Task_UpdateStatus.register()
        Task_SendPLPasscodes.register()
        Task_RemoveOldRun.register()
        Task_RemoveOldMessage.register()
        Task_PostMainPasscode.register()
        Task_PostSupportPasscode.register()
        Task_UpdateMissedRunsList.register()
        Task_RemoveButtons.register()
        Task_UpdateWeatherPosts.register()