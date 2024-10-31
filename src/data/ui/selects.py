from typing import List, Tuple
import aiohttp
from nullsafe import _
from discord import ButtonStyle, Interaction, Message, ScheduledEvent, SelectOption
from discord.ui import Button, Select

import bot
from data.eureka_info import EurekaTrackerZone
from data.events.event import ScheduledEvent
from data.guilds.guild_channel_functions import GuildChannelFunction
from data.guilds.guild_pings import GuildPingType
from data.ui.modals import EurekaTrackerModal
from data.ui.views import TemporaryView
from logger import feedback_and_log, guild_log_message
from utils import default_defer, default_response


class EurekaTrackerZoneSelect(Select):
    def __init__(self, *, generate: bool = False):
        self.generate = generate
        self.message: Message = None
        options = [
            SelectOption(label='Anemos', value=str(EurekaTrackerZone.ANEMOS.value)),
            SelectOption(label='Pagos', value=str(EurekaTrackerZone.PAGOS.value)),
            SelectOption(label='Pyros', value=str(EurekaTrackerZone.PYROS.value)),
            SelectOption(label='Hydatos', value=str(EurekaTrackerZone.HYDATOS.value))
        ]
        super().__init__(placeholder="Select Eureka Instance",
                         options=options)


    async def generate_url(self, zone: EurekaTrackerZone) -> Tuple[str, str]:
        async with aiohttp.ClientSession() as session:
            async with session.post('https://ffxiv-eureka.com/api/instances', json=
                {
                    "data": {
                        "attributes": {
                            "copy-from": None,
                            "data-center-id": None,
                            "instance-id": None,
                            "created-at": None,
                            "updated-at": None,
                            "zone-id": str(zone.value)
                        },
                        "type": "instances"
                    }
                }) as resp:
                json = await resp.json()
                if json and json["data"] and json["data"]["id"]:
                    if json["data"]["attributes"] and json["data"]["attributes"]["password"]:
                        return f'https://ffxiv-eureka.com/{json["data"]["id"]}', json["data"]["attributes"]["password"]
                return '', ''


    async def callback(self, interaction: Interaction):
        # check if user has access to send messages to channel
        zone = EurekaTrackerZone(int(self.values[0]))
        if self.generate:
            await default_defer(interaction)
            url, passcode = await self.generate_url(zone)
            eureka = bot.instance.data.eureka_info
            if next((tracker for tracker in eureka._trackers if tracker.url == url), None) is not None:
                eureka.remove(url)
            bot.instance.data.eureka_info.add(url, zone)
            await bot.instance.data.ui.eureka_info.rebuild(interaction.guild_id)
            view = TemporaryView()
            view.add_item(Button(url=url, label='Visit the tracker', style=ButtonStyle.link))
            await interaction.followup.send(content=f'Successfully generated {zone.name} tracker. Passcode: {passcode}', view=view, ephemeral=True)
            await interaction.user.send(f'Successfully generated {zone.name} tracker. Passcode: {passcode}', view=view)
            await guild_log_message(interaction.guild_id, f'{interaction.user.display_name} has added a tracker for {zone.name} - `{url}`.')
            guild = bot.instance.data.guilds.get(interaction.guild_id)
            if guild:
                notification_channel = guild.channels.get(GuildChannelFunction.EUREKA_TRACKER_NOTIFICATION, str(zone.value))
                if notification_channel:
                    channel = interaction.guild.get_channel(notification_channel.id)
                    mentions = await guild.pings.get_mention_string(GuildPingType.EUREKA_TRACKER_NOTIFICATION, str(zone.value))
                    await channel.send(f'{mentions} Tracker {url} has been added for {zone.name} by {interaction.user.mention}.')
        else:
            await interaction.response.send_modal(EurekaTrackerModal(zone=zone))
        if self.message:
            await self.message.delete()

class PartyPositionSelect(Select):
    def __init__(self, *, event: ScheduledEvent, party: int, as_party_leader: bool = False):
        options = []
        self.event = event
        self.as_party_leader = as_party_leader
        self.party = party
        for slot in event.signup.template.slots.for_party(party):
            if not event.signup.slots.get(slot):
                options.append(SelectOption(label=f'{slot.position + 1}. {slot.name}', value=slot.position))
        super().__init__(placeholder="Select Position",
                         options=options)

    async def callback(self, interaction: Interaction):
        await default_defer(interaction)
        position = int(self.values[0])
        slot_template = self.event.signup.template.slots.for_party(self.party)[position]
        slot = self.event.signup.slots.get(slot_template)
        if slot:
            return await default_response(interaction, f'This slot is already taken by {_(bot.instance.get_guild(
                interaction.guild_id).get_member(slot.user_id)).mention}.')
        self.event.signup.slots.add(slot_template, interaction.user.id)
        if self.as_party_leader:
            self.event.users.party_leaders[self.party] = interaction.user.id
        await bot.instance.data.ui.signup_recruitment.rebuild(interaction.guild_id, self.event.id)
        pl = ' (Party leader)' if self.as_party_leader else ''
        await feedback_and_log(interaction, f'signed up for {await self.event.to_string()} as {slot_template.name}{pl}.')
        await interaction.delete_original_response()

class PartySelect(Select):
    def __init__(self, *, event: ScheduledEvent, parties: List[int], as_party_leader: bool = False):
        options = []
        self.event = event
        self.as_party_leader = as_party_leader
        for i in parties:
            options.append(SelectOption(label=f'Party {event.pl_button_texts(i)}', value=str(i)))
        super().__init__(placeholder="Select Party",
                         options=options)

    async def callback(self, interaction: Interaction):
        await default_defer(interaction)
        party = int(self.values[0])
        view = TemporaryView()
        view.add_item(PartyPositionSelect(event=self.event, party=party, as_party_leader=self.as_party_leader))
        await interaction.followup.send(f'Select a position in party {self.event.pl_button_texts(party)}.',
                                        view=view)
        await interaction.delete_original_response()