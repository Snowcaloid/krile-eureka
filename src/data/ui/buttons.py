from abc import abstractmethod
import bot
from discord.ui import Button, View
from discord import ButtonStyle, Embed, Emoji, Interaction, Message, PartialEmoji, Role, Member, TextChannel
from typing import Dict, List, Optional, Tuple, Type, Union
from data.db.sql import SQL, Record
from data.ui.constants import BUTTON_STYLE_DESCRIPTIONS, BUTTON_TYPE_DESCRIPTIONS, ButtonType
from data.ui.selects import EurekaTrackerZoneSelect
from data.ui.views import TemporaryView
from logger import feedback_and_log, guild_log_message
from utils import default_defer, default_response
from data.cache.message_cache import MessageCache


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
                if self.role is None:
                    await feedback_and_log(interaction, f'tried using button <{self.label}> in message <{self.message.jump_url}> but role is not loaded. Contact your administrators.')
                elif interaction.user.get_role(self.role.id):
                    await interaction.user.remove_roles(self.role)
                    await feedback_and_log(interaction, f'removed role **{self.role.name}** from {interaction.user.mention}.')
                else:
                    await interaction.user.add_roles(self.role)
                    await feedback_and_log(interaction, f'taken the role **{self.role.name}**.')
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
    event_id: int

    def button_type(self) -> ButtonType: return ButtonType.PL_POST

    async def callback(self, interaction: Interaction):
        if interaction.message == self.message:
            await default_defer(interaction)
            id = self.event_id
            guild_data = bot.instance.data.guilds.get(interaction.guild_id)
            event = guild_data.schedule.get(id)
            if event:
                index = self.pl
                party_name = event.pl_button_texts[index]
                current_party_leader = event.users.party_leaders[index]
                if not current_party_leader and not interaction.user.id in event.users._party_leaders:
                    event.users.party_leaders[index] = interaction.user.id
                    await bot.instance.data.ui.pl_post.rebuild(interaction.guild_id, event.id)
                    run = await event.to_string()
                    await feedback_and_log(interaction, f'applied as Party Leader for Party {party_name} on {run}')
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


class AssignTrackerButton(ButtonBase):
    """Buttons which show a modal for url of a tracker"""

    def button_type(self) -> ButtonType: return ButtonType.ASSIGN_TRACKER

    async def callback(self, interaction: Interaction):
        if interaction.message == self.message:
            view = TemporaryView()
            select = EurekaTrackerZoneSelect(generate=False)
            view.add_item(select)
            select.message = await interaction.response.send_message('Select a Eureka region, then paste the tracker ID.', view=view, ephemeral=True)


class GenerateTrackerButton(ButtonBase):
    """Buttons which generates a new url for a tracker"""

    def button_type(self) -> ButtonType: return ButtonType.GENERATE_TRACKER

    async def callback(self, interaction: Interaction):
        if interaction.message == self.message:
            view = TemporaryView()
            select = EurekaTrackerZoneSelect(generate=True)
            view.add_item(select)
            select.message = await interaction.response.send_message('Select a Eureka region.', view=view, ephemeral=True)

class SendPLGuideButton(ButtonBase):
    """Buttons which sends a party leading guide to the user"""

    def button_type(self) -> ButtonType: return ButtonType.SEND_PL_GUIDE

    async def callback(self, interaction: Interaction):
        if interaction.message == self.message:
            await default_defer(interaction)
            message = await interaction.user.send('_ _')
            await bot.instance.data.ui.help.ba_party_leader(message, interaction.guild.emojis)
            await default_response(interaction, 'The guide has been sent to your DMs.')


BUTTON_CLASSES: Dict[ButtonType, Type[ButtonBase]] = {
    ButtonType.ROLE_SELECTION: RoleSelectionButton,
    ButtonType.ROLE_DISPLAY: RoleDisplayButton,
    ButtonType.PL_POST: PartyLeaderButton,
    ButtonType.ASSIGN_TRACKER: AssignTrackerButton,
    ButtonType.GENERATE_TRACKER: GenerateTrackerButton,
    ButtonType.SEND_PL_GUIDE: SendPLGuideButton
}


def buttons_as_text(buttons: List[ButtonBase]) -> str:
    buttons.sort(key=lambda btn: btn.row * 10 + btn.index)
    result = ''
    last_row = 0
    for button in buttons:
        newline = '\n' if last_row < button.row else ''
        color = BUTTON_STYLE_DESCRIPTIONS[button.style]
        type = BUTTON_TYPE_DESCRIPTIONS[button.button_type()]
        result = result + f'[ Button {button.emoji} "{button.label}" Color: "{color}" Type: "{type}" ]{newline}'
        last_row = button.row
    return result


def save_buttons(message: Message, view: View):
    if bot.instance.data.ready:
        query = Record() # Prevent multiple connects and disconnects
        for button in view.children:
            btn: ButtonBase = button
            btn.message = message
            role = btn.role.id if btn.role else 0
            emoji = None if btn.emoji is None else str(btn.emoji)
            SQL('buttons').insert(Record(button_type=btn.button_type().value,
                                         style=btn.style.value,
                                         emoji=emoji,
                                         label=btn.label,
                                         button_id=btn.custom_id,
                                         row=btn.row,
                                         index=btn.index,
                                         role=role,
                                         pl=btn.pl,
                                         channel_id=message.channel.id,
                                         message_id=message.id,
                                         event_id=btn.event_id if isinstance(btn, PartyLeaderButton) else None))
        del query


def delete_button(button_id: str) -> None:
    SQL('buttons').delete(f"button_id='{button_id}'")


def delete_buttons(message_id: str) -> None:
    SQL('buttons').delete(f'message_id={message_id}')


async def get_guild_button_data(button_id: str, channel_id: int, message_id: int, role_id: int) -> Tuple[Message, Role]:
    channel: TextChannel = bot.instance.get_channel(channel_id)
    if channel is None: channel = await bot.instance.fetch_channel(channel_id)
    if channel:
        message = await MessageCache().get(message_id, channel)
        if message:
            if role_id:
                role = channel.guild.get_role(role_id)
                if role:
                    return message, role
                else:
                    roles = await channel.guild.fetch_roles()
                    return message, next((role for role in roles if role.id == role_id), None)
            else:
                return message, None
        else:
            delete_button(button_id)
            return None, None
    else:
        delete_button(button_id)
        return None, None


async def load_button(button_id: str) -> ButtonBase:
    for record in SQL('buttons').select(fields=['button_type', 'style', 'label',
                                                'row', 'index', 'role', 'pl',
                                                'channel_id', 'message_id', 'emoji', 'event_id'],
                                        where=f"button_id='{button_id}'",
                                        all=True):
        message, role = await get_guild_button_data(button_id, record['channel_id'], record['message_id'], record['role'])
        button = BUTTON_CLASSES[ButtonType(record['button_type'])](
            style=ButtonStyle(record['style']),
            label=record['label'],
            custom_id=button_id,
            row=record['row'],
            index=record['index'],
            role=role,
            message=message,
            pl=record['pl'],
            emoji=record['emoji']
        )
        if isinstance(button, PartyLeaderButton):
            button.event_id = record['event_id']
        return button
    return None

async def buttons_from_message(message: Message) -> List[ButtonBase]:
    result = []
    query = Record() # Prevent multiple connects and disconnects
    for record in SQL('buttons').select(fields=['button_id'],
                                        where=f'message_id={message.id}',
                                        all=True):
        result.append(await load_button(record[0]))
    del query
    return result