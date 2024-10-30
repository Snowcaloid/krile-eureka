from api.api_webserver import ApiRequestRegister
from api.channels import ChannelsRequest
from api.discord.channels import DiscordChannelsRequest
from api.guilds import GuildsRequest
from api.login import LoginRequest
from api.pings import PingsRequest
from api.roles import RolesRequest

def register_api_handlers() -> None:
    ApiRequestRegister.register(LoginRequest)
    ApiRequestRegister.register(RolesRequest)
    ApiRequestRegister.register(GuildsRequest)
    ApiRequestRegister.register(ChannelsRequest)
    ApiRequestRegister.register(PingsRequest)
    ApiRequestRegister.register(DiscordChannelsRequest)