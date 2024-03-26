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

def create_collections(title: str, visble: bool, games: List[GameID]):
    try:
        return
    except Exception as e:
        print(e)
        return

def get_collection(col: CollectionID) -> CollectionID:
    try:
        with cs_database() as db:
            query = '''select C.title, 
                       (select count(*) as num_of_games from CollectionContains CC where CC.collectionID=%d), 
                       (select sum(PG.endtime - PG.starttime) as play_time from PlaysGame PG 
                            where PG.username=%s and PG.gameID in 
                            (select CC.gameID from CollectionContains CC where CC.collectionID=%d))'''
            cursor = db.cursor()
            cursor.execute(query, col, "", col)
            result = cursor.fetchone()
            return result
    except Exception as e:
        print(e)
        # cs_database.rollback()
        return
    
def add_game(col: CollectionID, game: GameID):
    try:
        with cs_database() as db:
            query = '''insert into CollectionContains values %d %d'''
            cursor = db.cursor()
            cursor.execute(query, col, game)
            db.commit()
    except Exception as e:
        print(e)
        return
    
def remove_game(col: CollectionID, game: GameID):
    try:
        with cs_database() as db:
            query = '''delete from CollectionContains where collectionID=%d and gameID=%d'''
            cursor = db.cursor()
            cursor.execute(query, col, game)
            db.commit()
    except Exception as e:
        print(e)
        return
    
def change_title(col: CollectionID, new_title: str):
    try:
        with cs_database() as db:
            query = '''update Collection set title=%s where collectionID=%s'''
            cursor = db.cursor()
            cursor.execute(query, new_title, col)
            db.commit()
    except Exception as e:
        print(e)
        return
    
def delete_collection(col: CollectionID):
    try:
        with cs_database() as db:
            CCquery = '''delete from CollectionContains where collectionID=%d'''
            Cquery = '''delete from Collection where collectionID=%d''' 
            cursor = db.cursor()
            cursor.execute(CCquery, col)
            cursor.execute(Cquery, col)
            db.commit()
    except Exception as e:
        print(e)
        return
    
def testing():
    get_collection(2)
    # add_game(2, 163)
    # remove_game(2, 163)
    # change_title(2, 'New Title')
    # delete_collection(2)