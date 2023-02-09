from bot import snowcaloid
from discord import InteractionResponse, Embed
from discord.channel import TextChannel
from discord.ui import View, Button
from buttons import RoleSelectionButton
from views import PersistentView
from data.query import QueryType

@snowcaloid.tree.command(name = "role_post_create", description = "Make a reaction post.")
async def role_post_create(interaction: InteractionResponse):
    snowcaloid.data.query.start(interaction.user.id, QueryType.ROLE_POST)
    await interaction.response.send_message(
        embed=Embed(title='Use /role_post_add to add roles to the post.'),
        ephemeral=True)

@snowcaloid.tree.command(name = "role_post_finish", description = "Make a reaction post.")
async def role_post_finish(interaction: InteractionResponse, channel: TextChannel):
    if not snowcaloid.data.query.running(interaction.user.id, QueryType.ROLE_POST):
        await interaction.response.send_message(
            embed=Embed(title='Use /role_post_create to start the creation process.'),
            ephemeral=True)
        return
    
    view = PersistentView()
    for entry in snowcaloid.data.role_post_data.get_entries(interaction.user.id):
        view.add_item(RoleSelectionButton(label=entry.label, custom_id=entry.id))

    await interaction.response.send_message(f'A message will been sent to #{channel.name}.', ephemeral=True)
    channels = await interaction.guild.fetch_channels()
    for ch in channels:
        if ch == channel:
            message = await channel.send(view=view, embed=Embed(title='You can press on the buttons to get roles.'))
            print(f'Message ID: {message.id}, Channel ID: {message.channel.id}, Guild ID: {message.guild.id}')

    snowcaloid.data.query.stop(interaction.user.id, QueryType.ROLE_POST)
    
@snowcaloid.tree.command(name = "role_post_add", description = "Make a reaction post.")
async def role_post_add(interaction: InteractionResponse, name: str):
    if not snowcaloid.data.query.running(interaction.user.id, QueryType.ROLE_POST):
        await interaction.response.send_message(
            embed=Embed(title='Use /role_post_create to start the creation process.'),
            ephemeral=True)
        return
    
    if name in snowcaloid.data.role_post_data.get_entries(interaction.user.id):
        await interaction.response.send_message(
            embed=Embed(title=f'{name} is already in the list. Try another name.'),
            ephemeral=True)
        return
    
    view = View()
    id = str(interaction.guild_id) + str(interaction.user.id) + name
    snowcaloid.data.role_post_data.append(interaction.user.id, name, id)
    for entry in snowcaloid.data.role_post_data.get_entries(interaction.user.id):
        view.add_item(Button(label=entry.label, disabled=True))
        
    await interaction.response.send_message(
        embed=Embed(title='Use /role_post_create to add more roles, or /role_post_finish to finish.'), 
        view=view,
        ephemeral=True)
    

    
def so_that_import_works():
    return