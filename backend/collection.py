from backend.game import GID
from typing import List, Tuple
from database import cs_database


class CollectionID:
    id: int

    def __init__(self, id: int):
        self.id = id


class Collection:
    id: CollectionID
    owner: str
    title: str
    visible: bool

    def __init__(self, title: str,  id: CollectionID, owner: str, visible: bool):
        self.id = id
        self.owner = owner
        self.title = title
        self.visible = visible

    def get_games() -> List[GID]:
        raise NotImplementedError
        return []


def get_owned_collections(username: str) -> List[Collection]:
    query = 'select C.title, C.collectionid, C.username, C.visible from "Collection" C where C.username = %s'
    with cs_database() as db:
        cursor = db.cursor()
        cursor.execute(query, [username])
        result = cursor.fetchall()
        return [Collection(r[0], CollectionID(r[1]), r[2], r[3]) for r in result]


def create_collection(id: int, username: str, title: str, visible: bool):
    try:
        with cs_database() as db:
            data = (id, username, title, visible)
            query = "INSERT INTO Collection VALUES (%s, %s, %s, %s)"
            cursor = db.cursor()
            cursor.execute(query, data)
            result = cursor.fetchone()
            return result
    except Exception as e:
        print(e)
        return


def get_collection_data(col: CollectionID, player: str) -> Tuple[int, float]:
    try:
        with cs_database() as db:
            query = '''select count(*) as num_of_games from "CollectionContains" CC where CC.collectionID=%s'''
            query2 = '''select sum(PG.end_time - PG.start_time) as play_time from "PlaysGame" PG 
                            where PG.username=%s and PG.gameID in 
                            (select CC.gameID from "CollectionContains" CC where CC.collectionID=%s)'''
            cursor = db.cursor()
            cursor.execute(query, [col.id])
            num_games = cursor.fetchone()[0]
            print(num_games)

            cursor.execute(query2, [player, col.id])
            playtime = cursor.fetchone()[0]
            print(playtime)
            if playtime == None:
                playtime = 0
            return (num_games, playtime)
    except Exception as e:
        print("get collecton data error", e)
        # cs_database.rollback()
        return


def add_game(col: CollectionID, game: GID):
    try:
        with cs_database() as db:
            query = '''insert into CollectionContains values %d %d'''
            cursor = db.cursor()
            cursor.execute(query, col, game)
            db.commit()
    except Exception as e:
        print(e)
        return


def delete_game(col: CollectionID, game: GID):
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
