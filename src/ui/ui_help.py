from abc import abstractmethod
from typing import List
from centralized_data import Bindable
from discord import Embed, Emoji, Message
from discord.utils import get

class UIHelpPost:
    def __init__(self, emojis: List[Emoji] = []):
        self.embeds = [Embed()]
        self.emojis = emojis
        self.rebuild(self.embeds[0])

    @abstractmethod
    def rebuild(self, embed: Embed) -> None: pass

    async def post(self, message: Message) -> Message:
        return await message.edit(embeds=self.embeds)


class UIHelpPost_BAPortals(UIHelpPost):
    def rebuild(self, embed: Embed) -> None:
        embed.title = 'BA Portals'
        embed.set_image(url='https://i.ibb.co/ZzXtmHc/ba-portals.png')
        embed.description = (
            '/macrolock\n'
            '/p Portal 1: <1>\n'
            '/p Portal 2: <2>\n'
            '/p Portal 3: <3>\n'
            '/p Portal 4: <4>\n'
            '/p Portal 5: <5>\n'
            '/p Portal 6: <6>\n'
            '/p Portal 7: <7>\n'
            '/p Portal 8: <8>\n'
            '/p ========================\n'
            '/p We are party [Party Number]!\n'
            '/p #ba-chat has the portal Map\n'
            '/p ========================'
        )

class UIHelpPost_BARaiden(UIHelpPost):
    def rebuild(self, embed: Embed) -> None:
        embed.title = 'BA Raiden Waymarks'
        embed.set_image(url='https://i.ibb.co/nzV2SFq/ba-raiden.png')

class UIHelpPost_BAAV(UIHelpPost):
    def rebuild(self, embed: Embed) -> None:
        embed.title = 'BA AV Waymarks'
        embed.set_image(url='https://media.discordapp.net/attachments/1283355147292119040/1284561609074937950/01a09e1bf1e64667dbb62fe73f020197.png')

class UIHelpPost_BARooms(UIHelpPost):
    def rebuild(self, embed: Embed) -> None:
        embed.title = 'BA Rooms'
        embed.set_image(url='https://i.ibb.co/QY2jcjn/ba-rooms.png')

class UIHelpPost_BAOzma(UIHelpPost):
    def rebuild(self, embed: Embed) -> None:
        embed.title = 'Proto Ozma Waymarks'
        embed.set_image(url='https://i.ibb.co/DW7LJcT/ba-ozma.jpg')
        embed.description = (
            '/macrolock\n'
            '/p -----------------------------------------------------\n'
            '/p We are party [Party Number]\n'
            '/p Our main platform is [Platform Letter]\n'
            '/p Blackhole buffer is [Black Hole Buffer Waymark]\n'
            '/p Meteors are placed on 1 and 2\n'
            '/p -----------------------------------------------------\n'
            '/p /magiaauto off\n'
            '/p Offensive Element: Earth\n'
            '/p Defensive Element: Lightning\n'
            '/p -----------------------------------------------------'
        )
        self.embeds = [embed,
            Embed(title='Example markers for platform A').set_image(
                url='https://media.discordapp.net/attachments/1283355147292119040/1283356822333292577/ozma-markers.webp'),
            Embed(title='Meteors').set_image(
                url='https://media.discordapp.net/attachments/1283355147292119040/1283356983185117244/Meteor-Impact.gif'),
            Embed(title='Acceleration Bomb').set_image(
                url='https://media.discordapp.net/attachments/1283355147292119040/1283357159052279931/Acceleration-Bomb.gif')
        ]

class UIHelpPost_BAFairy(UIHelpPost):
    def rebuild(self, embed: Embed) -> None:
        embed.title = 'BA Fairy Guide'
        embed.set_image(url='https://i.ibb.co/FHMKfSL/Untitled.png')
        embed.description = (
            '* Don''t shout out fairy locations.\n'
            '* Place down waymarks on them and post them in #ba-chat.\n'
            '* **There can be up to 3 fairies at the same time and they have limited charges.**\n'
            '* **We get the fairy buff at 5 minutes remaining on our Ovni buff (after killing Ovni).**'
        )

class UIHelpPost_BATrapping(UIHelpPost):
    def rebuild(self, embed: Embed) -> None:
        embed.title = 'BA Trapping Guide'
        embed.set_image(url='https://media.discordapp.net/attachments/1283355147292119040/1283355389525753856/ba-trapping.png')

class UIHelpPost_BAEntrance(UIHelpPost):
    def rebuild(self, embed: Embed) -> None:
        embed.title = 'BA Entrance Guide'
        embed.set_image(url='https://media.discordapp.net/attachments/1283355147292119040/1283355574188113995/ba-entrance.png')

class UIHelpPost_LogosCrafting(UIHelpPost):
    def rebuild(self, embed: Embed) -> None:
        embed.title = 'Crafting explanations - click to zoom in'
        embed.set_image(url='https://media.discordapp.net/attachments/1283355147292119040/1283355687606554624/image.png')

class UIHelpPost_LogosWisdoms(UIHelpPost):
    def rebuild(self, embed: Embed) -> None:
        embed.title = 'Spirit + Wisdoms - click to zoom in'
        embed.set_image(url='https://media.discordapp.net/attachments/1283355147292119040/1283355817323794455/logoswisdoms.png')

class UIHelpPost_LogosActions(UIHelpPost):
    def rebuild(self, embed: Embed) -> None:
        embed.title = 'Logos actions - click to zoom in'
        embed.set_image(url='https://media.discordapp.net/attachments/1283355147292119040/1283355992398237730/logosexplanations.png')

class UIHelpPost_LogosTank(UIHelpPost):
    def rebuild(self, embed: Embed) -> None:
        embed.title = 'Tank logos actions - click to zoom in'
        embed.set_image(url='https://media.discordapp.net/attachments/1283355147292119040/1283356115995852820/logostanks.png')

class UIHelpPost_LogosHealer(UIHelpPost):
    def rebuild(self, embed: Embed) -> None:
        embed.title = 'Healer logos actions - click to zoom in'
        embed.set_image(url='https://media.discordapp.net/attachments/1283355147292119040/1283356242538004573/logoshealers.png')

class UIHelpPost_LogosMelee(UIHelpPost):
    def rebuild(self, embed: Embed) -> None:
        embed.title = 'Melee DPS logos actions - click to zoom in'
        embed.set_image(url='https://media.discordapp.net/attachments/1283355147292119040/1283356338134716490/logosmelee.png')

class UIHelpPost_LogosRanged(UIHelpPost):
    def rebuild(self, embed: Embed) -> None:
        embed.title = 'Ranged Physical DPS / Mage logos actions - click to zoom in'
        embed.set_image(url='https://media.discordapp.net/attachments/1283355147292119040/1283356448268484711/logosranged.png')

class UIHelpPost_LogosUtility(UIHelpPost):
    def rebuild(self, embed: Embed) -> None:
        embed.title = 'Utility logos actions - click to zoom in'
        embed.set_image(url='https://media.discordapp.net/attachments/1283355147292119040/1283356569454776360/logosutility.png')

class UIHelpPost_LogosWebsite(UIHelpPost):
    def rebuild(self, embed: Embed) -> None:
        embed.title = 'Website for crafting combinations of Logos actions'
        embed.url ='https://ffxiv-eureka.com/logograms'

class UIHelpPost_BAPartyLeader(UIHelpPost):
    def rebuild(self, embed: Embed) -> None:
        tank = get(self.emojis, name='tank') or 'Tank'
        healer = get(self.emojis, name='healer') or 'Healer'
        dps = get(self.emojis, name='dps') or 'DPS'
        flex = get(self.emojis, name='flex') or 'Flex'
        embed.title = 'Responsibilites during a Run'
        embed.description = (
            '* Creating the Party Finder for your party, ideally this should be up 10m before the passcodes are posted (let the RL know if it will be later)\n'
            '* Placing waymarks (please use the ones provided by us)\n'
            '* Checking Logos Actions of party members prior to jumping down\n'
            '* Bringing or appointing someone to get Protect L / Shell L and cast this on your party at the entrance of BA\n'
        )
        next_embed = Embed()
        self.embeds.append(next_embed)
        next_embed.title = 'Party setup and actions'
        next_embed.description = (
            f'* The PF should have the following setup: {tank} {healer} (shield) {healer} {dps} {dps} {dps} {flex} {flex}\n'
            '* One healer should have Refresh L\n'
            '* All members should have Spirit of the Remembered and an appropriate wisdom active\n'
            '* The tank should have a defensive Wisdom for Ozma (Guardian or Indomitable)\n'
        )
        next_embed = Embed()
        self.embeds.append(next_embed)
        next_embed.title = 'Support Party Extras'
        next_embed.description = (
            f'* The PF should have the following setup:  {tank} {healer} {flex} {flex} {flex} {flex} {flex} {flex} {flex}\n'
            '* Ensure multiple people have Dispel L for Ovni and Support FATE\n'
            '* Explain that Shock Spikes and Mighty Strike need to be Dispelled\n'
            '* Explain how support portals work\n'
        )
        next_embed = Embed()
        self.embeds.append(next_embed)
        next_embed.title = 'Waymarks and commands'
        next_embed.description = (
            'The waymarks can be found in https://discord.com/channels/1066841758752837745/1171185956204843080 .\n'
            'Following commands can help you and the raid leader in the run. Do not be afraid to use them.\n'
            '`/ba fairy` - fairy scouting guide\n'
            '`/ba portals` - portal assignments\n'
            '`/ba entrance` - BA entrance reminders\n'
            '`/ba trapping` - trapping guide\n'
            '`/ba raiden` - raiden waymarks\n'
            '`/ba rooms` - room assignments\n'
            '`/ba av` - AV waymarks\n'
            '`/ba ozma` - ozma waymarks and mechanics\n'
        )


class UIHelp(Bindable):
    """Various help posts"""

    async def ba_portals(self, message: Message) -> Message:
        return await UIHelpPost_BAPortals(message.guild).post(message)

    async def ba_rooms(self, message: Message) -> Message:
        return await UIHelpPost_BARooms(message.guild).post(message)

    async def ba_raiden(self, message: Message) -> Message:
        return await UIHelpPost_BARaiden(message.guild).post(message)

    async def ba_av(self, message: Message) -> Message:
        return await UIHelpPost_BAAV(message.guild).post(message)

    async def ba_fairy(self, message: Message) -> Message:
        return await UIHelpPost_BAFairy(message.guild).post(message)

    async def ba_trapping(self, message: Message) -> Message:
        return await UIHelpPost_BATrapping(message.guild).post(message)

    async def ba_entrance(self, message: Message) -> Message:
        return await UIHelpPost_BAEntrance(message.guild).post(message)

    async def ba_ozma(self, message: Message) -> Message:
        return await UIHelpPost_BAOzma(message.guild).post(message)

    async def logos_crafting(self, message: Message) -> Message:
        return await UIHelpPost_LogosCrafting(message.guild).post(message)

    async def logos_wisdoms(self, message: Message) -> Message:
        return await UIHelpPost_LogosWisdoms(message.guild).post(message)

    async def logos_actions(self, message: Message) -> Message:
        return await UIHelpPost_LogosActions(message.guild).post(message)

    async def logos_tank(self, message: Message) -> Message:
        return await UIHelpPost_LogosTank(message.guild).post(message)

    async def logos_healer(self, message: Message) -> Message:
        return await UIHelpPost_LogosHealer(message.guild).post(message)

    async def logos_melee(self, message: Message) -> Message:
        return await UIHelpPost_LogosMelee(message.guild).post(message)

    async def logos_ranged(self, message: Message) -> Message:
        return await UIHelpPost_LogosRanged(message.guild).post(message)

    async def logos_utility(self, message: Message) -> Message:
        return await UIHelpPost_LogosUtility(message.guild).post(message)

    async def logos_website(self, message: Message) -> Message:
        return await UIHelpPost_LogosWebsite(message.guild).post(message)

    async def ba_party_leader(self, message: Message, emojis: List[Emoji]) -> Message:
        return await UIHelpPost_BAPartyLeader(emojis).post(message)
