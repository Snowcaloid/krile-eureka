from datetime import datetime
from typing import override
from discord import Embed
from utils.basic_types import TaskType
from data.events.schedule import Schedule
from tasks.task import TaskTemplate
from utils.logger import GuildLogger


class Task_SendPLPasscodes(TaskTemplate):
    from bot import Bot
    @Bot.bind
    def bot(self) -> Bot: ...

    @override
    def type(self) -> TaskType: return TaskType.SEND_PL_PASSCODES

    @override
    def description(self, data: dict, timestamp: datetime) -> str:
        return f'Send Party Leader Passcodes for event {data["entry_id"]} at {timestamp.strftime("%Y-%m %H:%M ST")}'

    @override
    async def execute(self, obj: dict) -> None:
        if obj and obj["guild"] and obj["entry_id"]:
            event = Schedule(obj["guild"]).get(obj["entry_id"])
            if event:
                member = self.bot.get_member(event.guild_id, event.users.raid_leader)
                if member:
                    await member.send(embed=Embed(
                        title=event.dm_title,
                        description=event.raid_leader_dm_text))
                for i in range(0, 6):
                    user = event.users.party_leaders[i]
                    if user and user != event.users.raid_leader:
                        member = self.bot.get_member(event.guild_id, user)
                        try:
                            await member.send(embed=Embed(
                                title=event.dm_title,
                                description=event.party_leader_dm_text(i)
                            ))
                        except Exception as e:
                            GuildLogger(event.guild_id).log(
                                f'Failed to send Party Leader DM to {member.mention}: {e}'
                            )
                if event.use_support:
                    member =  self.bot.get_member(event.guild_id, event.users.party_leaders[6])
                    if member:
                        try:
                            await member.send(embed=Embed(
                                title=event.dm_title,
                                description=event.support_party_leader_dm_text
                            ))
                        except Exception as e:
                            GuildLogger(event.guild_id).log(
                                f'Failed to send Party Leader DM to {member.mention}: {e}'
                            )

