from typing import List
from data.table.database import Database

class RolePostData: 
    class RolePostEntry:
        user: int
        label: str
        id: str
        def __init__(self, user: str, label: int):
            self.user = user
            self.label = label
            self.id = ''
            
    _list: List[RolePostEntry] = []
    
    def __init__(self):
        pass
    
    def append(self, user: int, label: str):
        self._list.append(RolePostData.RolePostEntry(user, label))
        
    def get_entries(self, user: int) -> List[RolePostEntry]:
        result = []
        for entry in self._list:
            if entry.user == user:
                result.append(entry)
                
        return result
    
    def clear(self, user: int):
        for entry in self._list:
            if entry.user == user:
                self._list.remove(entry)
                
    def save(self, db: Database, user: int):
        db.connect()
        try:
            for entry in self.get_entries(user):
                db.query(f'insert into buttons values (\'{entry.id}\', \'{entry.label}\')')
        finally:
            db.disconnect()
        