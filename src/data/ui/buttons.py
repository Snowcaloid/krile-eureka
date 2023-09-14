import bot
from enum import Enum
from discord.ui import Button
from discord import Interaction, Message, Role, Member
from typing import List
from data.validation.permission_validator import PermissionValidator
from logger import guild_log_message
from utils import default_defer, default_response


class ButtonType(Enum):
    ROLE_SELECTION = "@ROLE@"
    PL_POST = "@PL@"
    MISSEDRUN = "@MISSED@"

def button_custom_id(id: str, message: Message, type: ButtonType) -> str:
    """Generate custom_id for a button."""
    return f'{message.id}-{type.value}-{id}'

def save_buttons(message: Message):
    if bot.instance.data.ready:
        db = bot.instance.data.db
        db.connect()
        try:
            for action_row in message.components:
                for item in action_row.children:
                    db.query(f'insert into buttons (button_id, message_id, label) values (\'{item.custom_id}\', {message.id}, \'{item.label}\')')
        finally:
            db.disconnect()

class RoleSelectionButton(Button):
    """Buttons, which add or remove a role from the user who interacts with them"""
    async def callback(self, interaction: Interaction):
        if str(interaction.message.id) in self.custom_id:
            await default_defer(interaction)
            roles: List[Role] = list(filter(lambda role : role.name == self.label, await interaction.guild.fetch_roles()))
            if not roles:
                roles.append(await interaction.guild.create_role(name=self.label))

            role: Role = roles[0]

            if isinstance(interaction.user, Member):
                if interaction.user.get_role(role.id):
                    await interaction.user.remove_roles(role)
                    await default_response(interaction, f'You have removed the role {role.name} from yourself')
                else:
                    await interaction.user.add_roles(role)
                    await default_response(interaction, f'You have been granted the role {role.name}')


class PartyLeaderButton(Button):
    """Buttons, which the intaracting user uses to add or remove themself
    from party leader position of a run."""
    async def callback(self, interaction: Interaction):
        if str(interaction.message.id) in self.custom_id:
            await default_defer(interaction)
            id = int(interaction.message.content.split('#')[1])
            guild_data = bot.instance.data.guilds.get(interaction.guild_id)
            event = guild_data.schedule.get(id)
            if event:
                index = int(self.custom_id[-1]) - 1
                party_name = event.pl_button_texts[index]
                current_party_leader = event.users.party_leaders[index]
                if not current_party_leader and not interaction.user.id in event.users._party_leaders:
                    event.users.party_leaders[index] = interaction.user.id
                    await bot.instance.data.ui.pl_post.rebuild(interaction.guild_id, event.id)
                    await default_response(interaction, f'You have been set as Party Leader for Party {party_name}')
                    run = await event.to_string()
                    await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}** has registered for Party {party_name} on {run}')
                elif current_party_leader and (interaction.user.id == current_party_leader or interaction.user.id == event.users.raid_leader):
                    is_party_leader_removing_self = interaction.user.id == current_party_leader
                    event.users.party_leaders[index] = 0
                    await bot.instance.data.ui.pl_post.rebuild(interaction.guild_id, event.id)
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


class MissedRunButton(Button):
    """Buttons, which add missed run data.

    Properties
    ----------
    users: :class'`List[int]`
        List of users who already clicked the button
    """
    users: List[int]
    event_category: str

    def __init__(self, **kw):
        super().__init__(**kw)
        self.users = []
        self.event_category = ''

    async def callback(self, interaction: Interaction):
        if str(interaction.message.id) in self.custom_id:
            await default_defer(interaction)
            if PermissionValidator.allowed_to_react_to_missed_post(interaction.user, self.event_category):
                return await default_response(interaction, 'You are not eligable for this function.')
            if interaction.user.id in self.users:
                return await default_response(interaction, 'You have already been noted. This only works once per post.')
            guild_data = bot.instance.data.guilds.get(interaction.guild_id)
            if guild_data is None: return await default_response(interaction, 'Something went wrong.')
            if guild_data.missed_runs.eligable(interaction.user.id, self.event_category):
                return await default_response(interaction, (
                    'You already reacted 3 times. You are eligable to contact a raid leader '
                    'shortly before their next run to gain access to an early passcode '
                    'at their discretion.'))
            if guild_data.missed_runs.member_allowed(interaction.user, self.event_category):
                return await default_response(interaction, f'Your roles do not allow you to react to this post.')
            guild_data.missed_runs.inc(interaction.user.id, self.event_category)
            self.users.append(interaction.user.id)
            if guild_data.missed_runs.eligable(interaction.user.id, self.event_category):
                return await default_response(interaction, (
                    'You reacted 3 times. You are eligible to contact a raid leader '
                    'shortly before their next run to gain access to an early passcode '
                    'at their discretion.'
                    ))
            return await default_response(interaction, (
                'You have been noted. You can notify the raid leader in '
                f'{3-guild_data.missed_runs.get(interaction.user.id, self.event_category).amount} runs.'
            ))
