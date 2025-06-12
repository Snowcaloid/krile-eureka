from typing import override

from utils.basic_types import TaskExecutionType
from tasks.task import TaskTemplate


class Task_RunAsyncMethod(TaskTemplate):
    @override
    def type(self) -> TaskExecutionType: return TaskExecutionType.RUN_ASYNC_METHOD

    @override
    def runtime_only(self) -> bool: return True

    @override
    async def execute(self, obj: object) -> None:
        if obj.get("method"):
            method: callable = obj["method"]
            args = obj.get("args", [])
            kwargs = obj.get("kwargs", {})
            await method(*args, **kwargs)


