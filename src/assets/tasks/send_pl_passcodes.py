from typing import override
from discord import Embed
import bot
from data.guilds.guild import Guilds
from data.tasks.task import TaskExecutionType, TaskTemplate


class Task_SendPLPasscodes(TaskTemplate):
    @Guilds.bind
    def guilds(self) -> Guilds: ...

    @override
    def type(self) -> TaskExecutionType: return TaskExecutionType.SEND_PL_PASSCODES

    @override
    async def execute(self, obj: object) -> None:
        if obj and obj["guild"] and obj["entry_id"]:
            event = self.guilds.get(obj["guild"]).schedule.get(obj["entry_id"])
            if event:
                guild = bot.instance.get_guild(obj["guild"])
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

