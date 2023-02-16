from typing import List
from data.table.database import Database

class RolePostData: 
    """Runtime data object containing temporary data for creating a role post.
    This object has no equivalent database entity.

    Properties
    ----------
    _list: :class:`List[RolePostEntry]`
        List of all role post entries (requested buttons for a role post).
    """
    class RolePostEntry:
        """Helper class for role post entries."""
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
        """Adds an entry for a role post

        Args:
            user (int): querying user id
            label (str): Role label
        """
        self._list.append(RolePostData.RolePostEntry(user, label))
        
    def get_entries(self, user: int) -> List[RolePostEntry]:
        """Gets all the entries requested by the user

        Args:
            user (int): querying user id
        """
        result = []
        for entry in self._list:
            if entry.user == user:
                result.append(entry)
                
        return result
    
    def clear(self, user: int):
        """Removes all entries requested by the user

        Args:
            user (int): querying user id
        """
        for entry in self._list:
            if entry.user == user:
                self._list.remove(entry)
                
    def save(self, db: Database, user: int):
        """Saves the created Role buttons to the database.

        Args:
            db (Database): remove this please
            user (int): querying user id
            
        TODO:
            Remove db parameter.
        """
        db.connect()
        try:
            for entry in self.get_entries(user):
                db.query(f'insert into buttons values (\'{entry.id}\', \'{entry.label}\')')
        finally:
            db.disconnect()
        