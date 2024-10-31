from uuid import uuid4
from discord import ButtonStyle, Embed, Message, TextChannel
from data.guilds.guild_channel import GuildChannel
from data.guilds.guild_message_functions import GuildMessageFunction
from data.guilds.guild_pings import GuildPingType
import data.cache.message_cache as cache
import bot
from data.events.event import EventCategory
from data.guilds.guild_channel_functions import GuildChannelFunction
from data.ui.buttons import LeaveSignupButton, PartyLeaderButton, SendPLGuideButton, SignUpAsMemberButton, SignUpAsPLButton, delete_buttons, save_buttons
from data.ui.views import PersistentView

class UISignupRecruitment:
    """Signup Recruitment."""
    async def create(self, guild_id: int, id: int) -> None:
        guild_data = bot.instance.data.guilds.get(guild_id)
        event = guild_data.schedule.get(id)
        if event is None or not event.is_signup or not event.use_pl_posts: return
        channel_id = event.signup.template.recruitment_channel
        if not channel_id: return
        channel: TextChannel = bot.instance.get_channel(channel_id)
        if channel is None: return
        message = await channel.send(f'Signup Recruitment post #{str(id)}')
        event.pl_post_id = message.id
        message = await self.rebuild(guild_id, id, True)
        guild_data.messages.add(message.id, channel.id, GuildMessageFunction.PL_POST)
        if event.use_pl_post_thread:
            await message.create_thread(name=event.pl_post_thread_title)


    async def rebuild(self, guild_id: int, id: int, recreate_view: bool = False) -> Message:
        guild_data = bot.instance.data.guilds.get(guild_id)
        guild = bot.instance.get_guild(guild_id)
        event = guild_data.schedule.get(id)
        if event is None or not event.is_signup or not event.use_pl_posts: return
        channel_id = event.signup.template.recruitment_channel
        if channel_id is None: return
        channel: TextChannel = bot.instance.get_channel(channel_id)
        message = await cache.messages.get(event.pl_post_id, channel)
        if message is None: return
        embed = Embed(title=event.pl_post_title, description=event.pl_post_text)
        parties_embed = Embed(title='Parties')
        for i in range(1, event.signup.template.party_count + 1):
            party_composition = ''
            for j, slot_template in enumerate(event.signup.template.slots.for_party(i)):
                slot = event.signup.slots.get(slot_template)
                username = 'TBD' if slot is None else _(guild.get_member(slot.user_id)).display_name or f'<error at user {slot.user_id}>'
                pl = ' (PL)' if not slot is None and slot.user_id in event.users.party_leaders else ''
                party_composition += f'{j}. {slot_template.name} - {username}{pl}\n'
            parties_embed.add_field(name=f'Party {event.pl_button_texts(i-1)}',
                                    value=party_composition, inline=False)
        if recreate_view:
            delete_buttons(event.pl_post_id)
            view = PersistentView()
            bot.instance.data.ui.view.view_list.append(view)
            view.add_item(SignUpAsPLButton(
                        label='Sign up as Party Leader',
                        custom_id=str(uuid4()),
                        row=1,
                        index=0,
                        style=ButtonStyle.primary))
            view.add_item(SignUpAsMemberButton(
                        label='Sign up as Member',
                        custom_id=str(uuid4()),
                        row=1,
                        index=1,
                        style=ButtonStyle.primary))
            view.add_item(LeaveSignupButton(
                        label='Leave',
                        custom_id=str(uuid4()),
                        row=1,
                        index=2,
                        style=ButtonStyle.danger))
            message = await message.edit(embeds=[embed, parties_embed], view=view)
            save_buttons(message, view)
        else:
            message = await message.edit(embeds=[embed, parties_embed])
        return message


    async def remove(self, guild_id: int, event_id: int) -> GuildChannel:
        guild_data = bot.instance.data.guilds.get(guild_id)
        event = guild_data.schedule.get(event_id)
        if event is None: return
        channel_data = guild_data.channels.get(GuildChannelFunction.PL_CHANNEL, event.type)
        if channel_data is None: return
        channel: TextChannel = bot.instance.get_channel(channel_data.id)
        message = await cache.messages.get(event.pl_post_id, channel)
        if message is None: return
        await message.delete()