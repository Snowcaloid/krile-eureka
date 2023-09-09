
from data.tasks.post_main_passcode_5 import Task_PostMainPasscode
from data.tasks.post_support_passcode_6 import Task_PostSupportPasscode
from data.tasks.remove_missed_run_post_7 import Task_RemoveMissedRunPost
from data.tasks.remove_old_pl_posts_4 import Task_RemoveOldPLPosts
from data.tasks.remove_old_run_3 import Task_RemoveOldRun
from data.tasks.send_pl_passcodes_2 import Task_SendPLPasscodes
from data.tasks.update_status_1 import Task_UpdateStatus


class TaskRegisters:
    @classmethod
    def register_all(cl) -> None:
        Task_UpdateStatus.register()
        Task_SendPLPasscodes.register()
        Task_RemoveOldRun.register()
        Task_RemoveOldPLPosts.register()
        Task_PostMainPasscode.register()
        Task_PostSupportPasscode.register()
        Task_RemoveMissedRunPost.register()