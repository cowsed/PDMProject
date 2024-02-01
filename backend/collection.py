from game import GameID

class CollectionID:
    id: int
class Collection:
    games: [GameID]
    id: CollectionID
    def get_games() -> [GameID]:
        raise NotImplementedError
        return []



def get_collection(col: CollectionID) -> CollectionID:
    raise NotImplementedError
    return 0