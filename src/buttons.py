import bot as buttons_bot
from enum import Enum
from discord.ui import Button
from discord import Interaction, Embed, Role, Member
from typing import List

class ButtonType(Enum):
    ROLE_POST = "@ROLE@"
    PL_POST = "@PL@"

class RoleSelectionButton(Button):
    """Buttons, which add or remove a role from the user who interacts with them"""
    async def callback(self, interaction: Interaction):
        if str(interaction.message.id) in self.custom_id:
            roles: List[Role] = list(filter(lambda role : role.name == self.label, await interaction.guild.fetch_roles()))
            if not roles:
                roles.append(await interaction.guild.create_role(name=self.label))
            
            role: Role = roles[0]
            
            if isinstance(interaction.user, Member):
                if interaction.user.get_role(role.id):
                    await interaction.user.remove_roles(role)
                    await interaction.response.send_message(
                        embed=Embed(title='Success', description=f'You have removed the role {role.name} from yourself'), 
                        ephemeral=True)
                else:
                    await interaction.user.add_roles(role)
                    await interaction.response.send_message(
                        embed=Embed(title='Success', description=f'You have been granted the role {role.name}'), 
                        ephemeral=True)

class PartyLeaderButton(Button):
    """Buttons, which the intaracting user uses to add or remove themself 
    from party leader position of a run."""
    async def callback(self, interaction: Interaction):
        if str(interaction.message.id) in self.custom_id:
            entry = buttons_bot.snowcaloid.data.schedule_posts.get_post(interaction.guild_id).get_entry_by_pl_post(interaction.message.id)
            field = 'pl' + self.custom_id[-1] if self.custom_id[-1] != '7' else 'pls'
            index = int(self.custom_id[-1]) - 1
            party_name = self.custom_id[-1] if self.custom_id[-1] != '7' else 'Support'
            current_value = entry.party_leaders[index]
            if not current_value and not interaction.user.id in entry.party_leaders:
                entry.party_leaders[index] = interaction.user.id
                buttons_bot.snowcaloid.data.db.connect()
                try:
                    buttons_bot.snowcaloid.data.db.query(f'update schedule set {field}={interaction.user.id} where id={entry.id}')
                finally:
                    buttons_bot.snowcaloid.data.db.disconnect()
                guild_data = buttons_bot.snowcaloid.data.guild_data.get_data(interaction.guild_id)
                await buttons_bot.snowcaloid.data.schedule_posts.get_post(interaction.guild_id).update_pl_post(guild_data, entry=entry)
                await interaction.response.send_message(f'You have been set as Party leader for party {party_name}', ephemeral=True)
            elif current_value and (interaction.user.id == current_value or interaction.user.id == entry.owner):
                entry.party_leaders[index] = 0
                buttons_bot.snowcaloid.data.db.connect()
                try:
                    buttons_bot.snowcaloid.data.db.query(f'update schedule set {field}=0 where id={entry.id}')
                finally:
                    buttons_bot.snowcaloid.data.db.disconnect()
                guild_data = buttons_bot.snowcaloid.data.guild_data.get_data(interaction.guild_id)
                await buttons_bot.snowcaloid.data.schedule_posts.get_post(interaction.guild_id).update_pl_post(guild_data, entry=entry)
                await interaction.response.send_message(f'{(await interaction.guild.fetch_member(current_value)).display_name} has been removed from party {party_name}', ephemeral=True)
            elif current_value and interaction.user.id != current_value:
                await interaction.response.send_message(f'Party {party_name} is already taken by {(await interaction.guild.fetch_member(current_value)).display_name}', ephemeral=True)
            else:
                await interaction.response.send_message(f'You\'re already assigned to a party.', ephemeral=True)
                
            
                