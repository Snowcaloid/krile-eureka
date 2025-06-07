from user_input._base import SimpleUserInput
from utils.basic_types import NM_ALIASES, NotoriousMonster

class NotoriousMonsterUserInput(SimpleUserInput[NotoriousMonster]):
    def validate_and_fix(self, value: any) -> NotoriousMonster:
        if isinstance(value, NotoriousMonster):
            return value
        if isinstance(value, str):
            for nm, alias_list in NM_ALIASES:
                for alias in alias_list:
                    if value.lower() == alias.lower():
                        return nm
            for nm, nm_name in NotoriousMonster.items():
                if nm_name.lower() == value.lower():
                    return nm
        assert False, f"Invalid notorious monster name: {value}"