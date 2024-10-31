from api.api_webserver import ApiRequestRegister
from api.channels import ChannelsRequest
from api.discord.channels import DiscordChannelsRequest
from api.discord.roles import DiscordRolesRequest
from api.guilds import GuildsRequest
from api.login import LoginRequest
from api.pings import PingsRequest
from api.roles import RolesRequest
from api.signup_templates import SignupTemplatesRequest

def register_api_handlers() -> None:
    ApiRequestRegister.register(LoginRequest)
    ApiRequestRegister.register(RolesRequest)
    ApiRequestRegister.register(GuildsRequest)
    ApiRequestRegister.register(ChannelsRequest)
    ApiRequestRegister.register(PingsRequest)
    ApiRequestRegister.register(DiscordChannelsRequest)
    ApiRequestRegister.register(DiscordRolesRequest)
    ApiRequestRegister.register(SignupTemplatesRequest)