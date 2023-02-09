import discord

class RoleSelectionButton(discord.ui.Button):
    async def callback(self, interaction: discord.Interaction):
        roles = list(filter(lambda role : role.name == self.label, await interaction.guild.fetch_roles()))
        if not roles:
            roles.append(await interaction.guild.create_role(name=self.label))
           
        if isinstance(interaction.user, discord.Member):
            await interaction.user.add_roles(roles[0])
        
        await interaction.response.send_message(
            embed=discord.Embed(title='Success', description=f'You have been granted the role {roles[0].name}'), 
            ephemeral=True)