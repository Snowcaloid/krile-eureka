from typing import override
from discord import Embed
from basic_types import TaskExecutionType
import bot
from data.events.schedule import Schedule
from data.tasks.task import TaskTemplate


class Task_SendPLPasscodes(TaskTemplate):
    @override
    def type(self) -> TaskExecutionType: return TaskExecutionType.SEND_PL_PASSCODES

    @override
    async def execute(self, obj: object) -> None:
        if obj and obj["guild"] and obj["entry_id"]:
            event = Schedule(obj["guild"]).get(obj["entry_id"])
            if event:
                guild = bot.instance.get_guild(event.guild_id)
                member = guild.get_member(event.users.raid_leader)
                if member:
                    await member.send(embed=Embed(
                        title=event.dm_title,
                        description=event.raid_leader_dm_text))
                for i in range(0, 6):
                    user = event.users.party_leaders[i]
                    if user and user != event.users.raid_leader:
                        member = guild.get_member(user)
                        await member.send(embed=Embed(
                            title=event.dm_title,
                            description=event.party_leader_dm_text(i)
                        ))
                if event.use_support:
                    member = guild.get_member(event.users.party_leaders[6])
                    if member:
                        await member.send(embed=Embed(
                            title=event.dm_title,
                            description=event.support_party_leader_dm_text
                        ))

