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


class UIHelp:
    """Various help posts"""

    async def ba_portals(self, message: Message) -> Message:
        return await UIHelpPost_BAPortals().post(message)

    async def ba_rooms(self, message: Message) -> Message:
        return await UIHelpPost_BARooms().post(message)

    async def ba_raiden(self, message: Message) -> Message:
        return await UIHelpPost_BARaiden().post(message)

    async def ba_ozma(self, message: Message) -> Message:
        msg = await UIHelpPost_BAOzma().post(message)
        await message.channel.send('_ _', embeds=[
            Embed(title='Meteors').set_image(url='https://i.ibb.co/SJJk9SP/Meteor-Impact.gif'),
            Embed(title='Acceleration Bomb').set_image(url='https://i.ibb.co/yBN7ZBd/Acceleration-Bomb.gif')
        ])
        return msg
