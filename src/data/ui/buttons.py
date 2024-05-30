from abc import abstractmethod
import bot
from enum import Enum
from discord.ui import Button, View
from discord import ButtonStyle, Embed, Emoji, Interaction, Message, PartialEmoji, Role, Member, TextChannel
from typing import Dict, List, Optional, Tuple, Type, Union
from data.validation.permission_validator import PermissionValidator
from logger import guild_log_message
from utils import default_defer, default_response, sql_int
import data.cache.message_cache as cache


class ButtonType(Enum):
    ROLE_SELECTION = 1
    ROLE_DISPLAY = 2
    PL_POST = 3
    MISSEDRUN = 4


class ButtonBase(Button):
    def __init__(self,
                 *,
                 style: ButtonStyle = ButtonStyle.secondary,
                 label: Optional[str] = None,
                 disabled: bool = False,
                 custom_id: Optional[str] = None,
                 url: Optional[str] = None,
                 emoji: Optional[Union[str, Emoji, PartialEmoji]] = None,
                 row: Optional[int] = None,
                 index: Optional[int] = None,
                 role: Optional[Role] = None,
                 pl: Optional[int] = None,
                 message: Optional[Message] = None):
        self.index: int = index
        self.role: Role = role
        self.pl: int = pl
        self.message: Message = message
        super().__init__(style=style,label=label,disabled=disabled,custom_id=custom_id,url=url,row=row,emoji=emoji)

    @abstractmethod
    def button_type(self) -> ButtonType: pass


class RoleSelectionButton(ButtonBase):
    """Buttons, which add or remove a role from the user who interacts with them"""

    def button_type(self) -> ButtonType: return ButtonType.ROLE_SELECTION

    async def callback(self, interaction: Interaction):
        if interaction.message == self.message:
            await default_defer(interaction)
            if isinstance(interaction.user, Member):
                if interaction.user.get_role(self.role.id):
                    await interaction.user.remove_roles(self.role)
                    await guild_log_message(interaction.guild_id, f'{interaction.user.mention} has removed their role **{self.role.name}**.')
                    await default_response(interaction, f'You have removed the role {self.role.name} from yourself')
                else:
                    await interaction.user.add_roles(self.role)
                    await guild_log_message(interaction.guild_id, f'{interaction.user.mention} has taken the role **{self.role.name}**.')
                    await default_response(interaction, f'You have been granted the role {self.role.name}')
            else:
                await default_response(interaction, f'Role buttons don''t work outside of a server setting.')


class RoleDisplayButton(ButtonBase):
    """Buttons, which display roles to the person who clicks them"""

    def button_type(self) -> ButtonType: return ButtonType.ROLE_DISPLAY

    async def callback(self, interaction: Interaction):
        if interaction.message == self.message:
            await default_defer(interaction)
            roles: List[Role] = interaction.user.roles

            embed = Embed(title='Below, you will see your current roles')
            description = ''
            for role in roles:
                description += f'{role.mention}\n'

            embed.description = description
            await interaction.followup.send('', wait=True, embed=embed)


class PartyLeaderButton(ButtonBase):
    """Buttons, which the intaracting user uses to add or remove themself
    from party leader position of a run."""

    def button_type(self) -> ButtonType: return ButtonType.PL_POST

    async def callback(self, interaction: Interaction):
        if interaction.message == self.message:
            await default_defer(interaction)
            id = int(interaction.message.content.split('#')[1])
            guild_data = bot.instance.data.guilds.get(interaction.guild_id)
            event = guild_data.schedule.get(id)
            if event:
                index = self.pl
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


class MissedRunButton(ButtonBase):
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
        if interaction.message == self.message:
            await default_defer(interaction)
            if not PermissionValidator.allowed_to_react_to_missed_post(interaction.user, self.event_category):
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


BUTTON_CLASSES: Dict[ButtonType, Type[ButtonBase]] = {
    ButtonType.ROLE_SELECTION: RoleSelectionButton,
    ButtonType.ROLE_DISPLAY: RoleDisplayButton,
    ButtonType.PL_POST: PartyLeaderButton,
    ButtonType.MISSEDRUN: MissedRunButton
}


def save_buttons(message: Message, view: View):
    if bot.instance.data.ready:
        db = bot.instance.data.db
        db.connect()
        try:
            for button in view.children:
                btn: ButtonBase = button
                btn.message = message
                role = btn.role.id if btn.role else 0
                pl = 'null' if btn.pl is None else str(btn.pl)
                db.query((
                    'insert into buttons (button_type, style, label, button_id, row, index, '
                    f"role, pl, channel_id, message_id) values ({sql_int(btn.button_type().value)}, {sql_int(btn.style.value)}, '{btn.label}',"
                    f"'{btn.custom_id}', {sql_int(btn.row)}, {sql_int(btn.index)}, {sql_int(role)}, {pl}, {sql_int(message.channel.id)}, {sql_int(message.id)})"
                ))
        finally:
            db.disconnect()


def delete_button(button_id: str) -> None:
    db = bot.instance.data.db
    db.connect()
    try:
        db.query(f"delete from buttons where button_id = '{button_id}'")
    finally:
        db.disconnect()


async def get_guild_button_data(button_id: str, channel_id: int, message_id: int, role_id: int) -> Tuple[Message, Role]:
    channel: TextChannel = bot.instance.get_channel(channel_id)
    if channel is None: channel = await bot.instance.fetch_channel(channel_id)
    if channel:
        message = await cache.messages.get(message_id, channel)
        if message:
            if role_id:
                return message, channel.guild.get_role(role_id)
            else:
                return message, None
        else:
            delete_button(button_id)
            return None, None
    else:
        delete_button(button_id)
        return None, None


async def load_button(button_id: str) -> ButtonBase:
    db = bot.instance.data.db
    db.connect()
    try:
        for record in db.query(f'select button_type, style, label, row, index, role, pl, channel_id, message_id from buttons where button_id=\'{button_id}\''):
            message, role = await get_guild_button_data(button_id, record[7], record[8], record[5])
            return BUTTON_CLASSES[ButtonType(record[0])](
                style=ButtonStyle(record[1]),
                label=record[2],
                custom_id=button_id,
                row=record[3],
                index=record[4],
                role=role,
                message=message,
                pl=record[6]
            )
    finally:
        db.disconnect()
    return None