
from centralized_data import Bindable
from utils.basic_types import NOTORIOUS_MONSTERS, EurekaTrackerZone


class EurekaTypesService(Bindable):
    def is_nm_type(self, notorious_monster: str) -> bool:
        return notorious_monster in NOTORIOUS_MONSTERS.values()

    def notorious_monster_name_to_type_str(self, notorious_monster: str) -> str:
        for nm_type, nm_name in NOTORIOUS_MONSTERS.items():
            if nm_name == notorious_monster:
                return nm_type.value
        return notorious_monster

    def is_eureka_zone(self, eureka_instance: str) -> bool:
        return eureka_instance.upper() in EurekaTrackerZone.values()

    def eureka_zone_name_to_value_str(self, eureka_instance: str) -> str:
        for intance in EurekaTrackerZone._value2member_map_:
            if intance.name == eureka_instance.upper():
                return str(intance.value)
        if isinstance(eureka_instance, int):
            return str(eureka_instance)
        return eureka_instance