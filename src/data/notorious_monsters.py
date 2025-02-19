
from enum import Enum
from typing import Dict, List

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

NM_ALIASES: Dict[NotoriousMonster, List[str]] = {
    NotoriousMonster.KING_ARTHRO: ['Roi Arthro', 'König Athro', 'Crab'],
    NotoriousMonster.LOUHI: ['Luigi'],
    NotoriousMonster.CASSIE: ['Cassie la copieuse', 'Kopierende Cassie', 'Cassie'],
    NotoriousMonster.PENTHESILEA: ['Penthésilée', 'Penny'],
    NotoriousMonster.GOLDEMAR: ['Roi Goldemar', 'Goldemar'],
    NotoriousMonster.PROVENANCE_WATCHER: ['PW', 'Gardien de Provenance', 'Kristallwächter'],
    NotoriousMonster.LAMEBRIX: ['Wüterix-Söldner'],
    NotoriousMonster.SKOLL: ['Skalli']
}