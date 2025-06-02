from typing import override
from data.events.schedule import Schedule
from ui.base_button import BaseButton, ButtonTemplate
from utils.basic_types import ButtonType
from utils.logger import feedback_and_log, guild_log_message
from utils.functions import default_defer, default_response

from discord import Interaction

class PartyLeaderButton(ButtonTemplate):
    """Buttons, which the intaracting user uses to add or remove themself
    from party leader position of a run."""
    event_id: int

    from ui.ui_recruitment_post import UIRecruitmentPost
    @UIRecruitmentPost.bind
    def ui_recruitment_post(self) -> UIRecruitmentPost: ...

    def button_type(self) -> ButtonType: return ButtonType.PL_POST

    @override
    async def callback(self, interaction: Interaction, button: BaseButton):
        await default_defer(interaction)
        id = button.event_id
        event = Schedule(interaction.guild_id).get(id)
        if event:
            party_name = event.pl_button_texts[button.pl]
            current_party_leader = event.users.party_leaders[button.pl]
            if not current_party_leader and not interaction.user.id in event.users._party_leaders:
                event.users.party_leaders[button.pl] = interaction.user.id
                await self.ui_recruitment_post.rebuild(interaction.guild_id, event.id)
                run = await event.to_string()
                await feedback_and_log(interaction, f'applied as Party Leader for Party {party_name} on {run}')
            elif current_party_leader and (interaction.user.id == current_party_leader or interaction.user.id == event.users.raid_leader):
                is_party_leader_removing_self = interaction.user.id == current_party_leader
                event.users.party_leaders[button.pl] = 0
                await self.ui_recruitment_post.rebuild(interaction.guild_id, event.id)
                await default_response(interaction, f'{interaction.guild.get_member(current_party_leader).display_name} has been removed from party {party_name}')

                run = await event.to_string()

                if is_party_leader_removing_self:
                    message = f'**{interaction.user.display_name}** has removed themselves from Party {party_name} on {run}'
                else:
                    removed_user = interaction.guild.get_member(current_party_leader)
                    message = f'**{interaction.user.display_name}** has removed {removed_user.display_name} from Party {party_name} on {run}'

                await guild_log_message(interaction.guild_id, message)
            elif current_party_leader and interaction.user.id != current_party_leader:
                await default_response(interaction, f'Party {party_name} is already taken by {(interaction.guild.get_member(current_party_leader)).display_name}')
            else:
                await default_response(interaction, f'You\'re already assigned to a party.')
        else:
            await default_response(interaction, 'This run is already over.')