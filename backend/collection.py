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


def get_games(id: CollectionID) -> List[Tuple[str, GID]]:
    query = 'select G.title, G.gameid from "Game" G natural join "CollectionContains" CC  where G.gameid = CC.gameid  and CC.collectionid = %s order by G.title'
    with cs_database() as db:
        cursor = db.cursor()
        cursor.execute(query, [id.id])
        result = cursor.fetchall()
        return [(r[0], GID(r[1])) for r in result]


def get_owned_collections(username: str) -> List[Collection]:
    query = 'select C.title, C.collectionid, C.username, C.visible from "Collection" C where C.username = %s'
    with cs_database() as db:
        cursor = db.cursor()
        cursor.execute(query, [username])
        result = cursor.fetchall()
        return [Collection(r[0], CollectionID(r[1]), r[2], r[3]) for r in result]


def create_collection(username: str, title: str, visible: bool):
    try:
        with cs_database() as db:
            data = (username, title, visible)
            query = 'INSERT INTO "Collection" (username, title, visible) VALUES (%s, %s, %s)'

            cursor = db.cursor()
            cursor.execute(query, data)
            db.commit()

    except Exception as e:
        print("create collection error", e)
        return


def get_collection(id: CollectionID) -> List[Collection]:
    query = 'select C.title, C.collectionid, C.username, C.visible from "Collection" C where C.collectionid = %s'
    with cs_database() as db:
        cursor = db.cursor()
        cursor.execute(query, [id.id])
        r = cursor.fetchone()
        return Collection(r[0], CollectionID(r[1]), r[2], r[3])


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

            cursor.execute(query2, [player, col.id])
            playtime = cursor.fetchone()[0]
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
            query = '''insert into "CollectionContains" (collectionid, gameid) values (%s, %s)'''
            cursor = db.cursor()
            cursor.execute(query, (col.id, game.id))
            db.commit()
    except Exception as e:
        print("addgame", e)
        return


def delete_game(col: CollectionID, game: GID):
    try:
        with cs_database() as db:
            query = '''delete from "CollectionContains" where collectionID=%s and gameID=%s'''
            cursor = db.cursor()
            cursor.execute(query, (col.id, game.id))
            db.commit()
    except Exception as e:
        raise (e)
        return


def change_title(col: CollectionID, new_title: str):
    try:
        with cs_database() as db:
            query = '''update "Collection" set title=%s where collectionID=%s'''
            cursor = db.cursor()
            cursor.execute(query, [new_title, col.id])
            db.commit()
    except Exception as e:
        print(e)
        return


def delete_collection(col: CollectionID):
    try:
        with cs_database() as db:
            CCquery = '''delete from "CollectionContains" where collectionID=%s'''
            Cquery = '''delete from "Collection" where collectionID=%s'''
            cursor = db.cursor()
            cursor.execute(CCquery, [col.id])
            cursor.execute(Cquery, [col.id])
            db.commit()
    except Exception as e:
        print(e)
        return
