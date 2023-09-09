import bot
from enum import Enum
from discord import Interaction

from data.runtime_processes import RunTimeProcessType
from utils import default_response


class ProcessValidator(Enum):
    NORMAL = 0
    RAISING = 1

    @classmethod
    async def check_another_process_running(cl, interaction: Interaction, process_type: RunTimeProcessType) -> bool:
        result = not bot.instance.data.processes.running(interaction.user.id, process_type)
        if cl == ProcessValidator.RAISING and not result:
            await default_response(interaction, 'Another process is currently running.')
        return result

    @classmethod
    async def check_process_is_running(cl, interaction: Interaction, process_type: RunTimeProcessType) -> bool:
        result = bot.instance.data.processes.running(interaction.user.id, process_type)
        if cl == ProcessValidator.RAISING and not result:
            await default_response(interaction, 'There is no process running to finish.')
        return result