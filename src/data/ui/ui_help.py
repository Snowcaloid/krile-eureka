from abc import abstractmethod
from typing import List
from discord import Embed, File, Message

class UIHelpPost:
    def __init__(self):
      self.embed = Embed()
      self.rebuild(self.embed)

    @abstractmethod
    def rebuild(self, embed: Embed) -> None: pass

    async def post(self, message: Message) -> Message:
        return await message.edit(embed=self.embed)


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


class UIHelp:
    """Various help posts"""

    async def ba_portals(self, message: Message) -> Message:
        return await UIHelpPost_BAPortals().post(message)

    async def ba_rooms(self, message: Message) -> Message:
        return await UIHelpPost_BARooms().post(message)

    async def ba_raiden(self, message: Message) -> Message:
        return await UIHelpPost_BARaiden().post(message)

    async def ba_av(self, message: Message) -> Message:
        return await UIHelpPost_BAAV().post(message)

    async def ba_fairy(self, message: Message) -> Message:
        return await UIHelpPost_BAFairy().post(message)

    async def ba_trapping(self, message: Message) -> Message:
        return await UIHelpPost_BATrapping().post(message)

    async def ba_entrance(self, message: Message) -> Message:
        return await UIHelpPost_BAEntrance().post(message)

    async def ba_ozma(self, message: Message) -> Message:
        msg = await UIHelpPost_BAOzma().post(message)
        await message.channel.send('_ _', embeds=[
            Embed(title='Example markers for platform A').set_image(url='https://media.discordapp.net/attachments/1283355147292119040/1283356822333292577/ozma-markers.webp'),
            Embed(title='Meteors').set_image(url='https://media.discordapp.net/attachments/1283355147292119040/1283356983185117244/Meteor-Impact.gif'),
            Embed(title='Acceleration Bomb').set_image(url='https://media.discordapp.net/attachments/1283355147292119040/1283357159052279931/Acceleration-Bomb.gif')
        ])
        return msg

    async def logos_crafting(self, message: Message) -> Message:
        return await UIHelpPost_LogosCrafting().post(message)

    async def logos_wisdoms(self, message: Message) -> Message:
        return await UIHelpPost_LogosWisdoms().post(message)

    async def logos_actions(self, message: Message) -> Message:
        return await UIHelpPost_LogosActions().post(message)

    async def logos_tank(self, message: Message) -> Message:
        return await UIHelpPost_LogosTank().post(message)

    async def logos_healer(self, message: Message) -> Message:
        return await UIHelpPost_LogosHealer().post(message)

    async def logos_melee(self, message: Message) -> Message:
        return await UIHelpPost_LogosMelee().post(message)

    async def logos_ranged(self, message: Message) -> Message:
        return await UIHelpPost_LogosRanged().post(message)

    async def logos_utility(self, message: Message) -> Message:
        return await UIHelpPost_LogosUtility().post(message)

    async def logos_website(self, message: Message) -> Message:
        return await UIHelpPost_LogosWebsite().post(message)
