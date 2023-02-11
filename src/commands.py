from bot import snowcaloid
from discord import Interaction, InteractionResponse, Embed
from discord.channel import TextChannel
from discord.ui import View, Button
from discord.app_commands import check
from buttons import RoleSelectionButton
from views import PersistentView
from data.query import QueryType

def permission_admin(interaction: Interaction):
    for role in interaction.user.roles:
        if role.permissions.administrator:
            return True
    return False

###################################################################################
# role_post
###################################################################################

@snowcaloid.tree.command(name = "role_post_create", description = "Initialize creation process of a role reaction post.")
@check(permission_admin)
async def role_post_create(interaction: InteractionResponse):
    snowcaloid.data.query.start(interaction.user.id, QueryType.ROLE_POST)
    await interaction.response.send_message(
        embed=Embed(title='Use /role_post_add to add roles to the post.'),
        ephemeral=True)

@snowcaloid.tree.command(name = "role_post_finish", description = "Finish and post the role reaction post.")
@check(permission_admin)
async def role_post_finish(interaction: InteractionResponse, channel: TextChannel):
    if not snowcaloid.data.query.running(interaction.user.id, QueryType.ROLE_POST):
        await interaction.response.send_message(
            embed=Embed(title='Use /role_post_create to start the creation process.'),
            ephemeral=True)
        return
    
    view = PersistentView()
    for entry in snowcaloid.data.role_posts.get_entries(interaction.user.id):
        view.add_item(RoleSelectionButton(label=entry.label, custom_id=entry.id))

    await interaction.response.send_message(f'A message will been sent to #{channel.name}.', ephemeral=True)
    channels = await interaction.guild.fetch_channels()
    for ch in channels:
        if ch == channel:
            message = await channel.send(view=view, embed=Embed(title='You can press on the buttons to get roles.'))
            print(f'Message ID: {message.id}, Channel ID: {message.channel.id}, Guild ID: {message.guild.id}')

    snowcaloid.data.query.stop(interaction.user.id, QueryType.ROLE_POST)
    
@snowcaloid.tree.command(name = "role_post_add", description = "Add roles to the reaction post.")
@check(permission_admin)
async def role_post_add(interaction: InteractionResponse, name: str):
    if not snowcaloid.data.query.running(interaction.user.id, QueryType.ROLE_POST):
        await interaction.response.send_message(
            embed=Embed(title='Use /role_post_create to start the creation process.'),
            ephemeral=True)
        return
    
    if name in snowcaloid.data.role_posts.get_entries(interaction.user.id):
        await interaction.response.send_message(
            embed=Embed(title=f'{name} is already in the list. Try another name.'),
            ephemeral=True)
        return
    
    view = View()
    id = str(interaction.guild_id) + str(interaction.user.id) + name
    snowcaloid.data.role_posts.append(interaction.user.id, name, id)
    for entry in snowcaloid.data.role_posts.get_entries(interaction.user.id):
        view.add_item(Button(label=entry.label, disabled=True))
        
    await interaction.response.send_message(
        embed=Embed(title='Use /role_post_create to add more roles, or /role_post_finish to finish.'), 
        view=view,
        ephemeral=True)
    
###################################################################################
# schedule
###################################################################################

@snowcaloid.tree.command(name = "schedule_post_create", description = "Create a static post that will be used as a schedule list. Up to 1 per server.")
@check(permission_admin)
async def schedule_post_create(interaction: InteractionResponse, channel: TextChannel):
    if snowcaloid.data.schedule_posts.contains(interaction.guild_id):
        await interaction.response.send_message('This guild already contains a schedule post.', ephemeral=True)
    else:    
        message = await channel.send('This post contains an embed containing the schedule.', 
                                    embed=Embed(title='Schedule'))
        snowcaloid.data.schedule_posts.save(snowcaloid.data.db, interaction.guild_id, channel.id, message.id)
        await interaction.response.send_message(f'Schedule has been created in #{channel.name}', ephemeral=True)
    
###################################################################################
# permission error handling
###################################################################################

async def handle_permission_admin(interaction: Interaction):
    await interaction.response.send_message('Using this command requires administrator privileges.', ephemeral=True)
    
@role_post_create.error
async def error_role_post_create(interaction: Interaction, error):
    await handle_permission_admin(interaction)
    
@role_post_add.error
async def error_role_post_add(interaction: Interaction, error):
    await handle_permission_admin(interaction)
    
@role_post_finish.error
async def error_role_post_finish(interaction: Interaction, error):
    await handle_permission_admin(interaction)
    
@schedule_post_create.error
async def error_schedule_post_create(interaction: Interaction, error):
    await handle_permission_admin(interaction)

def so_that_import_works():
    return