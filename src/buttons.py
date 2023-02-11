from discord.ui import Button
from discord import Interaction, Embed, Role, Member
from typing import List
class RoleSelectionButton(Button):
    async def callback(self, interaction: Interaction):
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
        