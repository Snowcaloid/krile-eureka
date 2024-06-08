
from enum import Enum
from typing import Dict

class NotoriousMonster(Enum):
    PAZUZU = 'PAZUZU'
    KING_ARTHRO = 'CRAB'
    CASSIE = 'CASSIE'
    LOUHI = 'LOUHI'
    LAMEBRIX = 'LAME'
    YING_YANG = 'YY'
    SKOLL = 'SKOLL'
    PENTHESILEA = 'PENNY'
    MOLECH = 'MOLECH'
    GOLDEMAR = 'GOLDEMAR'
    CETO = 'CETO'
    PROVENANCE_WATCHER = 'PW'
    SUPPORT = 'SUPPORT'

NOTORIOUS_MONSTERS: Dict[NotoriousMonster, str] = {
    NotoriousMonster.PAZUZU: 'Pazuzu',
    NotoriousMonster.KING_ARTHRO: 'King Arthro',
    NotoriousMonster.CASSIE: 'Copycat Cassie',
    NotoriousMonster.LOUHI: 'Louhi',
    NotoriousMonster.LAMEBRIX: 'Lamebrix Strikebocks',
    NotoriousMonster.YING_YANG: 'Ying-Yang',
    NotoriousMonster.SKOLL: 'Skoll',
    NotoriousMonster.PENTHESILEA: 'Penthesilea',
    NotoriousMonster.MOLECH: 'Molech',
    NotoriousMonster.GOLDEMAR: 'King Goldemar',
    NotoriousMonster.CETO: 'Ceto',
    NotoriousMonster.PROVENANCE_WATCHER: 'Provenance Watcher',
    NotoriousMonster.SUPPORT: 'Support FATE',
}