from typing import Callable, override

from utils.basic_types import TaskType
from tasks.task import TaskTemplate


class Task_RunAsyncMethod(TaskTemplate):
    @override
    def type(self) -> TaskType: return TaskType.RUN_ASYNC_METHOD

    @override
    def runtime_only(self) -> bool: return True

    @override
    async def execute(self, obj: dict) -> None:
        if obj.get("method"):
            method: Callable[...] = obj["method"]
            args = obj.get("args", [])
            kwargs = obj.get("kwargs", {})
            await method(*args, **kwargs)


