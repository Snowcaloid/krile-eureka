from datetime import datetime
from typing import Dict, Optional
from utils import DiscordTimestampType, get_discord_timestamp
from data.weather.zone_info import data as ZoneInfo
from data.weather.weather_rates import data as WeatherRate

class EurekaZones: # no deriving from Enum for prettier access (instead of EurekaZones.ANEMOS.value)
    ANEMOS = 732
    PAGOS = 763
    PYROS = 795
    HYDATOS = 827

class EurekaWeathers: # no deriving from Enum for prettier access
    GALES = 'Gales'
    SHOWERS = 'Showers'
    FAIR_SKIES = 'Fair Skies'
    SNOW = 'Snow'
    HEATWAVES = 'Heat Waves'
    THUNDER = 'Thunder'
    BLIZZARDS = 'Blizzards'
    FOG = 'Fog'
    UMBRAL_WIND = 'Umbral Wind'
    THUNDERSTORMS = 'Thunderstorms'
    GLOOM = 'Gloom'

weather_emoji: Dict[str, str] = {
    EurekaWeathers.GALES: ':cloud_tornado:',
    EurekaWeathers.SHOWERS: ':cloud_rain:',
    EurekaWeathers.FAIR_SKIES: ':white_sun_small_cloud:',
    EurekaWeathers.SNOW: ':snowman:',
    EurekaWeathers.HEATWAVES: ':sunny:',
    EurekaWeathers.THUNDER: ':zap:',
    EurekaWeathers.BLIZZARDS: ':snowflake:',
    EurekaWeathers.FOG: ':fog:',
    EurekaWeathers.UMBRAL_WIND: ':cloud_tornado:',
    EurekaWeathers.THUNDERSTORMS: ':zap:',
    EurekaWeathers.GLOOM: ':skull:'
}

def get_time_ms(time_normal: datetime) -> int:
    return time_normal.timestamp() * 1000

def get_weather_chance_value(time_ms: int) -> int:
    unix = time_ms // 1000
    # Get Eorzea hour for weather start
    bell = unix / 175
    # Do the magic 'cause for calculations 16:00 is 0, 00:00 is 8, and 08:00 is 16
    increment = (bell + 8 - bell % 8) % 24

    # Take Eorzea days since unix epoch
    total_days = unix // 4200

    # The following math all needs to be done as unsigned integers.
    calc_base = int(total_days * 0x64 + increment)

    step1 = (calc_base << 0xB ^ calc_base)
    step2 = (step1 >> 8 ^ step1)

    return step2 % 0x64

def get_weather(time_ms: int, zone_id: int) -> Optional[str]:
    chance = get_weather_chance_value(time_ms)

    # See weather_rate.py and territory_type.py for details.
    rate_idx = ZoneInfo.get(zone_id, {}).get("weatherRate")
    if rate_idx is None:
        return None
    entry = WeatherRate.get(rate_idx)
    if entry is None:
        return None

    idx = 0
    for rate in entry["rates"]:
        if chance < rate:
            return entry["weathers"][idx]
        idx += 1

def floor_time_to_start_of_weather(time_ms: int) -> int:
    eight_hours = 1000 * 8 * 175
    return (time_ms // eight_hours) * eight_hours

def find_next_weather(
    time: datetime, zone_id: int, search_weather: str, max_time_ms: Optional[int] = None
) -> Optional[int]:
    time_ms = get_time_ms(time)
    max_time_ms = (max_time_ms or 1000 * 60 * 1000) + time_ms

    while time_ms < max_time_ms:
        weather = get_weather(time_ms, zone_id)
        if weather == search_weather:
            return floor_time_to_start_of_weather(time_ms)
        time_ms += 8 * 175 * 1000

    return None

def find_next_weather_multiple(
    time: int, zone_id: int, search_weather: str, count: int, max_time_ms: Optional[int] = None
) -> Optional[int]:
    time_ms = get_time_ms(time)
    max_time_ms = (max_time_ms or 10000 * 60 * 1000) + time_ms

    found_count = 0
    result = None
    while time_ms < max_time_ms:
        weather = get_weather(time_ms, zone_id)
        if weather == search_weather:
            found_count = found_count + 1
            if found_count == count:
                return result
            else:
                result = floor_time_to_start_of_weather(time_ms)
        else:
            found_count = 0

        time_ms += 8 * 175 * 1000

    return None

def current_weather(zone: int) -> str:
    weather = get_weather(get_time_ms(datetime.utcnow()), zone)
    emoji = weather_emoji[weather]
    return f'{emoji} {weather}'

def next_weather(zone: int, weather: str, count: int = 0) -> str:
    if count:
        time_ms = find_next_weather_multiple(datetime.utcnow(), zone, weather, count)
    else:
        time_ms = find_next_weather(datetime.utcnow(), zone, weather)

    return get_discord_timestamp(datetime.fromtimestamp(time_ms / 1000), DiscordTimestampType.LONG_DATE_TIME)

def find_next_hour(time_ms: int, search_hour: int) -> int:
    one_hour = 1000 * 175
    full_day = 24 * one_hour
    start_of_day = (time_ms // full_day) * full_day
    time_val = start_of_day + search_hour * one_hour
    if time_val < time_ms:
        time_val += full_day
    return time_val

def find_next_night(time_ms: int) -> int:
    return find_next_hour(time_ms, 19)

def find_next_day(time_ms: int) -> int:
    return find_next_hour(time_ms, 6)

def to_eorzea_time(date: datetime):
    EORZEA_MULTIPLIER = 3600 / 175
    epoch_ticks = (date - datetime(1970, 1, 1)).total_seconds()
    eorzea_ticks = int(epoch_ticks * EORZEA_MULTIPLIER)
    eorzea_datetime = datetime.utcfromtimestamp(eorzea_ticks)
    return eorzea_datetime

def is_night_time(time_ms: int) -> bool:
    hour = time_ms / 1000 / 175 % 24
    return hour < 6 or hour > 19

def is_day_time(time_ms: int) -> bool:
    return not is_night_time(time_ms)