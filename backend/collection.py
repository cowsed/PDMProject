from game import GameID
from typing import List

class CollectionID:
    id: int

class Collection:
    id: CollectionID
    def get_games() -> List[GameID]:
        raise NotImplementedError
        return []



def get_collection(col: CollectionID) -> CollectionID:
    raise NotImplementedError
    return 0