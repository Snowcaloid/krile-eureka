
from data.tasks.update_status import Task_UpdateStatus
from data.tasks.send_pl_passcodes import Task_SendPLPasscodes
from data.tasks.remove_old_run import Task_RemoveOldRun
from data.tasks.remove_old_message import Task_RemoveOldMessage
from data.tasks.post_main_passcode import Task_PostMainPasscode
from data.tasks.post_support_passcode import Task_PostSupportPasscode
from data.tasks.remove_buttons import Task_RemoveButtons
from data.tasks.update_eureka_info_posts import Task_UpdateEurekaInfoPosts


class TaskRegisters:
    @classmethod
    def register_all(cl) -> None:
        Task_UpdateStatus.register()
        Task_SendPLPasscodes.register()
        Task_RemoveOldRun.register()
        Task_RemoveOldMessage.register()
        Task_PostMainPasscode.register()
        Task_PostSupportPasscode.register()
        Task_RemoveButtons.register()
        Task_UpdateEurekaInfoPosts.register()