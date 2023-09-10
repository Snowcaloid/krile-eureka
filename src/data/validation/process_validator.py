import bot
from discord import Interaction

from data.runtime_processes import RunTimeProcessType
from utils import default_response


class ProcessValidator:
    NORMAL: 'ProcessValidator'
    RAISING: 'ProcessValidator'

    async def check_another_process_running(self, interaction: Interaction, process_type: RunTimeProcessType) -> bool:
        result = not bot.instance.data.processes.running(interaction.user.id, process_type)
        if self == ProcessValidator.RAISING and not result:
            await default_response(interaction, 'Another process is currently running.')
        return result

    async def check_process_is_running(self, interaction: Interaction, process_type: RunTimeProcessType) -> bool:
        result = bot.instance.data.processes.running(interaction.user.id, process_type)
        if self == ProcessValidator.RAISING and not result:
            await default_response(interaction, 'There is no process running to finish.')
        return result

ProcessValidator.NORMAL = ProcessValidator()
ProcessValidator.RAISING = ProcessValidator()