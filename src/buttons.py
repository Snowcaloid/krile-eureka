import bot
from enum import Enum
from discord.ui import Button
from discord import Interaction, Role, Member
from typing import List
from logger import guild_log_message


class ButtonType(Enum):
    ROLE_SELECTION = "@ROLE@"
    PL_POST = "@PL@"
    MISSEDRUN = "@MISSED@"


import utils


class RoleSelectionButton(Button):
    """Buttons, which add or remove a role from the user who interacts with them"""
    async def callback(self, interaction: Interaction):
        if str(interaction.message.id) in self.custom_id:
            await utils.default_defer(interaction)
            roles: List[Role] = list(filter(lambda role : role.name == self.label, await interaction.guild.fetch_roles()))
            if not roles:
                roles.append(await interaction.guild.create_role(name=self.label))

            role: Role = roles[0]

            if isinstance(interaction.user, Member):
                if interaction.user.get_role(role.id):
                    await interaction.user.remove_roles(role)
                    await utils.default_response(interaction, f'You have removed the role {role.name} from yourself')
                else:
                    await interaction.user.add_roles(role)
                    await utils.default_response(interaction, f'You have been granted the role {role.name}')


class PartyLeaderButton(Button):
    """Buttons, which the intaracting user uses to add or remove themself
    from party leader position of a run."""
    async def callback(self, interaction: Interaction):
        if str(interaction.message.id) in self.custom_id:
            await utils.default_defer(interaction)
            entry = bot.snowcaloid.data.schedule_posts.get_post(interaction.guild_id).get_entry_by_pl_post(interaction.message.id)
            if entry:
                field = 'pl' + self.custom_id[-1] if self.custom_id[-1] != '7' else 'pls'
                index = int(self.custom_id[-1]) - 1
                party_name = self.custom_id[-1] if self.custom_id[-1] != '7' else 'Support'
                current_value = entry.party_leaders[index]
                if not current_value and not interaction.user.id in entry.party_leaders:
                    entry.party_leaders[index] = interaction.user.id
                    bot.snowcaloid.data.db.connect()
                    try:
                        bot.snowcaloid.data.db.query(f'update schedule set {field}={interaction.user.id} where id={entry.id}')
                    finally:
                        bot.snowcaloid.data.db.disconnect()
                    guild_data = bot.snowcaloid.data.guild_data.get_data(interaction.guild_id)
                    await bot.snowcaloid.data.schedule_posts.get_post(interaction.guild_id).update_pl_post(guild_data, entry=entry)
                    await utils.default_response(interaction, f'You have been set as Party Leader for Party {party_name}')
                    run = await entry.to_string(interaction.guild_id)
                    await guild_log_message(interaction.guild_id, f'**{interaction.user.name}** has registered for Party {party_name} on {run}')
                elif current_value and (interaction.user.id == current_value or interaction.user.id == entry.leader):
                    is_party_leader_removing_self = interaction.user.id == current_value
                    entry.party_leaders[index] = 0
                    bot.snowcaloid.data.db.connect()
                    try:
                        bot.snowcaloid.data.db.query(f'update schedule set {field}=0 where id={entry.id}')
                    finally:
                        bot.snowcaloid.data.db.disconnect()
                    guild_data = bot.snowcaloid.data.guild_data.get_data(interaction.guild_id)
                    await bot.snowcaloid.data.schedule_posts.get_post(interaction.guild_id).update_pl_post(guild_data, entry=entry)
                    await utils.default_response(interaction, f'{interaction.guild.get_member(current_value).display_name} has been removed from party {party_name}')

                    run = await entry.to_string(interaction.guild_id)

                    if is_party_leader_removing_self:
                        message = f'**{interaction.user.name}** has removed themselves from Party {party_name} on {run}'
                    else:
                        removed_user = interaction.guild.get_member(current_value)
                        message = f'**{interaction.user.name}** has removed {removed_user.name} from Party {party_name} on {run}'

                    await guild_log_message(interaction.guild_id, message)
                elif current_value and interaction.user.id != current_value:
                    await utils.default_response(interaction, f'Party {party_name} is already taken by {(interaction.guild.get_member(current_value)).display_name}')
                else:
                    await utils.default_response(interaction, f'You\'re already assigned to a party.')
            else:
                await utils.default_response(interaction, 'This run is already over.')


class MissedRunButton(Button):
    """Buttons, which add missed run data.

    Properties
    ----------
    users: :class'`List[int]`
        List of users who already clicked the button
    """
    users: List[int]

    def __init__(self, **kw):
        super().__init__(**kw)
        self.users = []

    async def callback(self, interaction: Interaction):
        if str(interaction.message.id) in self.custom_id:
            await utils.default_defer(interaction)
            if interaction.user.id in self.users:
                return await utils.default_response(interaction, 'You have already been noted. This only works once per post.')
            data = bot.snowcaloid.data
            if data.missed_runs.eligable(interaction.guild_id, interaction.user.id):
                return await utils.default_response(interaction, (
                    'You already reacted 3 times. You are eligable to contact a raid leader '
                    'shortly before their next run to gain access to an early passcode '
                    'at their discretion.'
                    ))
            role_name = data.guild_data.get_data(interaction.guild_id).missed_role
            if role_name:
                for role in interaction.user.roles:
                    if role.name == role_name:
                        break
                else: # if not terminated by break
                    return await utils.default_response(interaction, f'You do not have the role "{role_name}".')
            data.missed_runs.inc(interaction.guild_id, interaction.user.id)
            self.users.append(interaction.user.id)
            await data.missed_runs.update_post(interaction.guild_id)
            if data.missed_runs.eligable(interaction.guild_id, interaction.user.id):
                return await utils.default_response(interaction, (
                    'You reacted 3 times. You are eligible to contact a raid leader '
                    'shortly before their next run to gain access to an early passcode '
                    'at their discretion.'
                    ))
            return await utils.default_response(interaction, (
                'You have been noted. You can notify a raid leader in '
                f'{3-data.missed_runs.get_data(interaction.guild_id, interaction.user.id).amount} runs.'
            ))
