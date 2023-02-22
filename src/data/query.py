from typing import List

class QueryType:
    """TODO: change this to an enum"""
    NONE = 0
    EMBED = 1

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
    """Runtime data object for the user's queries.
    This object has no equivalent database entity.

    Properties
    ----------
    _list: :class:`List[QueryData]`
        List of active queries. This is seperated by user and query type.
    _owner: :class:`QueryOwner`
        Runtime data object that can run code when a query is finished.
    """
    _list: List[QueryData]
    _owner: QueryOwner

    def __init__(self, owner: QueryOwner):
        self._owner = owner
        self._list = []

    def start(self, user: int, type: QueryType) -> bool:
        """Starts a runtime query

        Args:
            user (int): user id.
            type (QueryType): Query type.

        Returns:
            Success?
        """
        if user in self._list:
            return False
        else:
            self._list.append(QueryData(user, type))
        return True

    def running(self, user: int, type: QueryType) -> bool:
        """Is the user running a <type> query?

        Args:
            user (int): user id.
            type (QueryType): Query type.
        """
        for data in self._list:
            if data.user == user and data.type == type:
                return True

        return False

    def stop(self, user: int, type: QueryType) -> bool:
        """Finish a <type> query.

        Args:
            user (int): user id.
            type (QueryType): Query type.

        Returns:
            Success?
        """
        if self.running(user, type):
            for data in self._list:
                if data.user == user and data.type == type:
                    self._list.remove(data)

            self._owner.finish_query(user, type)
        else:
            return False
        return True
