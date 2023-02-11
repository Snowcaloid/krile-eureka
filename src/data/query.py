from typing import List

class QueryType:
    NONE = 0
    ROLE_POST = 1

class QueryData:
    user: int
    type: QueryType
    
    def __init__(self, user: int, type: QueryType) -> None:
        self.user = user
        self.type = type
        
class QueryOwner:
    def finish_query(self, user: int, type: QueryType) -> None:
        pass
    
class Query:
    _list: List[QueryData] 
    _owner: QueryOwner
    
    def __init__(self, owner: QueryOwner):
        self._owner = owner
        self._list = []
    
    def start(self, user: int, type: QueryType) -> bool:
        if user in self._list:
            return False
        else:
            self._list.append(QueryData(user, type))
        return True
    
    def running(self, user: int, type: QueryType) -> bool:
        for data in self._list:
            if data.user == user and data.type == type:
                return True
            
        return False
            
    def stop(self, user: int, type: QueryType) -> bool:
        if self.running(user, type):
            for data in self._list:
                if data.user == user and data.type == type:
                    self._list.remove(data)
                    
            self._owner.finish_query(user, type)
        else:
            return False
        return True
