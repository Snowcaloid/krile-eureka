
from random import randint


class EventPasscodeGenerator:
    @classmethod
    def generate(cl) -> int:
        return int(''.join(str(randint(0, 9)) for _ in range(4)))
