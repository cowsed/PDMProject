from game import GameID
from typing import List
from database import cs_database

class CollectionID:
    id: int

class Collection:
    games: List[GameID]
    id: CollectionID
    def get_games() -> List[GameID]:
        raise NotImplementedError
        return []



def get_collection(col: CollectionID) -> CollectionID:
    try:
        with cs_database() as db:
            query = '''select C.title, 
                       (select count(*) as num_of_games from CollectionContains CC where CC.collectionID=%s), 
                       (select sum(PG.endtime - PG.starttime) as play_time from PlaysGame PG 
                            where PG.username=%s and PG.gameID in 
                            (select CC.gameID from CollectionContains CC where CC.collectionID=%s))''', col, "", col
            cursor = db.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            return result
    except:
        return