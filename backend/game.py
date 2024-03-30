import datetime
from enum import Enum
from database import cs_database
from typing import List, Tuple
from backend.platform import Platform, PlatformID

"""
ESRB RATINGS:

Everyone
Everyone 10+
Teen
Mature 17+
Adults Only 18+
Rating Pending
Rating Pending
Likely Mature 17+
"""


class GID:
    id: int

    def __init__(self, n: int):
        self.id = n


class ESRBRating(Enum):
    EVERYONE = 1
    EVERYONE_10_PLUS = 2
    TEEN = 3
    MATURE = 4
    ADULTS_ONLY = 5
    RATING_PENDING = 6
    RATING_PENDING_MATURE = 7


class Game:
    name: str
    id: GID
    publisher: str
    rating: ESRBRating

    def __init__(self, name, id: GID, pub: str, r: ESRBRating):
        self.name = name
        self.id = id
        self.publisher = pub
        self.rating = r


def get_game(gid: GID) -> Game:
    query = 'select G.title, G.publisher, G.esrb_rating from "Game" G where gameid = %s'
    with cs_database() as db:
        cur = db.cursor()
        cur.execute(query, [gid.id])
        res = cur.fetchone()
        if res == None:
            raise Exception("No Game found with gameid", gid.id)
        return Game(res[0], gid, res[1], res[2])

def play_game(gid: GID, username: str, start_time: datetime, end_time: datetime):
    try:
        query = 'insert into "PlaysGame" values (%s, %s, %s, %s)'
        with cs_database() as db:
            cursor = db.cursor()
            cursor.execute(query, [gid.id, username, start_time, end_time])
            db.commit()
    except Exception as e:
        print("play random game error", e)
        return

def get_owned_games(username: str) -> List[Game]:
    query = 'select G.title, G.gameid, G.publisher, G.esrb_rating from "Game" G natural  join "OwnsGame" O where O.username = %s order by G.title'
    with cs_database() as db:
        cur = db.cursor()
        cur.execute(query, [username])
        result = cur.fetchall()
        res2 = [Game(g[0], GID(g[1]), g[2], g[3]) for g in result]
        return res2


def purchase_game(username: str, gid: GID):
    with cs_database() as db:
        cur = db.cursor()
        cur.execute('insert into "OwnsGame" (gameid, username, star_rating, review_text) VALUES (%s, %s, NULL, NULL)', [
                    gid.id, username])

        db.commit()


def do_i_own_game(username: str, gid: GID) -> bool:
    query = 'select * from "OwnsGame" where username = %s and gameid = %s'
    with cs_database() as db:
        cur = db.cursor()
        cur.execute(query, [username, gid.id])
        res = cur.fetchall()
        if res == None or len(res) == 0:
            return False
        return True


def game_platforms(gid: GID) -> List[Tuple[Platform, float, datetime.date]]:
    # list of platforms the game is on with the price and release date
    query = 'select P.name, P.platformid, GOP.price, GOP.release_date from "Platform" P natural join  "GameOnPlatform" GOP WHERE GOP.gameid = %s'
    with cs_database() as db:
        cur = db.cursor()
        cur.execute(query, [gid.id])
        res = cur.fetchall()
        if res == None:
            raise Exception("No Game found with gameid", gid.id)

        return [(Platform(r[0], PlatformID(r[1])), r[2], r[3]) for r in res]


def search_games(
        title="",
        platform="",
        release_date_range=(datetime.date(1800, 1, 1), datetime.date.today()),
        developers="",
        price_range=(0.0, float('inf')),
        genre="",
        esrb="Everyone",
        rating=0,
        sort_column="G.title",
        sort_order="ASC"
    ) -> List[Tuple[Game, str, str, str]]:
    """
    Returns every game that matches the provided search criteria.

    Parameters
----------
title : str, default: ""
    The search string to compare to each video game title.
    platform : str, default: ""
            The search string to compare to each platform title.
    release_date_range : tuple, default: ( datetime.date(1800, 1, 1), datetime.date.today() )
    The range each returned games' release date must fall into.
    developers : str, default: ""
            The search string to compare to each developer each game has.
    price_range : tuple, default: (0.0, float('inf'))
            The range each returned games' price must fall into (varies by platform release).
    genre : str, default: ""
            The search string to compare to each genre each game falls into.
    esrb : str, default: "Everyone"
            The ESRB rating to include in the search results.
    rating: int, default: 0
            The minimum rating to include in the search results.
    sort_column: str, default: "G.title"
            The column by which to sort the search results.
    sort_order: str, default: "ASC"
            The direction in which to sort the search results.

    Returns
    -------
    list
            A list of each matched game's name, platforms, developers, publisher, playtime, and ratings.
            Each game release on a different platform is considered a different game and listed separately.
    """

    try:
        with cs_database() as db:
            # TODO get reviews, and playtime
            query = """
                WITH UR AS (
                    SELECT
                        gameid,
                        AVG(star_rating) as avg_rating
                        
                    FROM "OwnsGame"
                    GROUP BY gameid
                )
                SELECT G.title,
                        G.gameid,
                       (SELECT name FROM "Platform" WHERE platformid=GOP.platformid) AS platform,
                       ARRAY(SELECT developer FROM "Development" WHERE gameid=G.gameid) AS developers,
                       G.publisher,
                       G.esrb_rating,
                       UR.avg_rating
                FROM "Game" G
                JOIN "GameOnPlatform" GOP ON GOP.gameid=G.gameid
                JOIN UR ON UR.gameid=G.gameid
                WHERE UPPER(G.title) LIKE UPPER(%s)
                  AND UPPER((SELECT name FROM "Platform" WHERE platformid=GOP.platformid)) LIKE UPPER(%s)
                  AND GOP.release_date >= %s AND GOP.release_date <= %s
                  AND UPPER(ARRAY_TO_STRING(ARRAY(SELECT developer FROM "Development" WHERE gameid=G.gameid), \',\')) LIKE UPPER(%s)
                  AND GOP.price >= %s AND GOP.price <= %s
                  AND UPPER(ARRAY_TO_STRING(ARRAY(SELECT genre_name FROM "Genre" Ge WHERE G.gameid=Ge.gameid), \',\')) LIKE UPPER(%s)
                  AND COALESCE(UR.avg_rating, 0.0) >= %s
                  AND UPPER(G.esrb_rating) LIKE UPPER(%s)
            """
            # This does not play nicely with parameterization, so it is a dynamic query
            order_clause = 'ORDER BY ' + sort_column + ' ' + sort_order + ', GOP.release_date ASC'
            query += order_clause
            cursor = db.cursor()
            cursor.execute(query, ('%' + title + '%',
                                   '%' + platform + '%',
                                   release_date_range[0],
                                   release_date_range[1],
                                   '%' + developers + '%',
                                   price_range[0],
                                   price_range[1],
                                   '%' + genre + '%',
                                   rating,
                                   esrb,
                                   ))
            result = cursor.fetchall()
            res2 = [
                (
                    Game(g[0], GID(g[1]), g[4], g[5]),
                    g[2],
                    g[3],
                    g[6]
                )
                for g in result
            ]
            return res2
    except Exception as e:
        print(e)
        raise e
        # No such user found (or database down)
        return None


def get_all_games():
    try:
        with cs_database() as db:
            # query = 'select G.title, G.esrb_rating, G.publisher from "Game" G'
            query = 'select G.title from "Game" G'
            cursor = db.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            return result
    except Exception as e:
        print(e)
        # No such user found (or database down)
        return None


def find_game_by_title(title: str):
    try:
        with cs_database() as db:
            query = 'select G.title, G.esrb_rating, G.publisher from "Game" G where G.title=%s'
            cursor = db.cursor()
            cursor.execute(query, (title,))
            result = cursor.fetchone()
            return result
    except Exception as e:
        print(e)
        # No such user found (or database down)
        return None


def get_all_development():
    try:
        with cs_database() as db:
            query = 'SELECT (SELECT title FROM "Game" G WHERE D.gameid=G.gameid), \
                            developer \
                     FROM "Development" D'
            cursor = db.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            return result
    except Exception as e:
        print(e)
        # No such user found (or database down)
        return None


def get_all_game_on_platform():
    try:
        with cs_database() as db:
            query = 'SELECT (SELECT name FROM "Platform" P WHERE P.platformid=GOP.gameid), \
                            (SELECT title FROM "Game" G WHERE G.gameid=GOP.gameid) \
                     FROM "GameOnPlatform" GOP'
            query = 'SELECT * FROM "GameOnPlatform"'
            cursor = db.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            return result
    except Exception as e:
        print(e)
        # No such user found (or database down)
        return None


def add_game(title: str, esrb_rating: str, publisher: str):
    try:
        with cs_database() as db:
            query = '\
                INSERT INTO "Game" (title, esrb_rating, publisher) \
                VALUES (%s, %s, %s) \
            '
            cursor = db.cursor()
            cursor.execute(query, (title, esrb_rating, publisher))
            db.commit()
    except Exception as e:
        print(e)


def add_game_to_platform(game_id="", game_title="", platform_id="", platform_title="", price=0.00, release_date=datetime.date(2000, 1, 1)):
    """
    Adds an entry to "GameOnPlatform" for the game with the specified id/title and the specified platform.

    Parameters
----------
game_id : str, default: ""
    If specified, the method adds the entry based on ID.
    game_title : str, default: ""
            If specified and game_id not specified, the method adds the entry based on the game title.
    platform_id : str, default: ""
    If specified, the method adds the entry based on ID.
    platform_title : str, default: ""
            If specified and platform_id not specified, the method adds the entry based on the platform title.
    price : float, default: 0.00
            The price of the game on this platform.
    release_date : datetime.date, default: datetime.date(2000, 1, 1)
            The date the game was released on this platform.
    """

    try:
        with cs_database() as db:
            if game_id != "" and platform_id != "":
                query = '\
                    INSERT INTO "GameOnPlatform" (gameid, platformid, price, release_date) \
                    VALUES (%s, %s, %s, %s) \
                '
                cursor = db.cursor()
                cursor.execute(
                    query, (game_id, platform_id, price, release_date))
                db.commit()
            elif game_title != "" and platform_title != "":
                query = '\
                    INSERT INTO "GameOnPlatform" (gameid, platformid, price, release_date) \
                    VALUES ((SELECT gameid FROM "Game" WHERE title=%s LIMIT 1), \
                            (SELECT platformid FROM "Platform" WHERE name=%s LIMIT 1), %s, %s) \
                '
                cursor = db.cursor()
                cursor.execute(
                    query, (game_title, platform_title, price, release_date))
                db.commit()
            else:
                print("Failed to insert. You must enter either both 'gameid' and 'platformid' or both 'game_title' and 'platform_title'.")
    except Exception as e:
        print(e)


def add_developer_to_game(game_id="", game_title="", developer_name=""):
    """
    Adds an entry to "Development" for the game with the specified id/title and the specified developer.

    Parameters
----------
game_id : str, default: ""
    If specified, the method adds the entry based on ID.
    game_title : str, default: ""
            If specified and game_id not specified, the method adds the entry based on the game title.
    developer_name : str, default: ""
            The name of the developer to be assigned to the game.
    """

    try:
        with cs_database() as db:
            if game_id != "":
                query = '\
                    INSERT INTO "Development" (gameid, developer) \
                    VALUES (%s, %s) \
                '
                cursor = db.cursor()
                cursor.execute(query, (game_id, developer_name))
                db.commit()
            else:
                query = '\
                    INSERT INTO "Development" (gameid, developer) \
                    VALUES ((SELECT gameid FROM "Game" WHERE title=%s LIMIT 1), %s) \
                '
                cursor = db.cursor()
                cursor.execute(query, (game_title, developer_name))
                db.commit()
    except Exception as e:
        print(e)


def add_genre_to_game(game_id="", game_title="", genre=""):
    """
    Adds an entry to "Genre" for the game with the specified id/title and the specified genre.

    Parameters
----------
game_id : str, default: ""
    If specified, the method adds the entry based on ID.
    game_title : str, default: ""
            If specified and game_id not specified, the method adds the entry based on the game title.
    genre : str, default: ""
            The name of the genre to be assigned to the game.
    """

    try:
        with cs_database() as db:
            if game_id != "":
                query = '\
                    INSERT INTO "Genre" (gameid, genre_name) \
                    VALUES (%s, %s) \
                '
                cursor = db.cursor()
                cursor.execute(query, (game_id, genre))
                db.commit()
            else:
                query = '\
                    INSERT INTO "Genre" (gameid, genre_name) \
                    VALUES ((SELECT gameid FROM "Game" WHERE title=%s LIMIT 1), %s) \
                '
                cursor = db.cursor()
                cursor.execute(query, (game_title, genre))
                db.commit()
    except Exception as e:
        print(e)

# Remove game with passed id


def remove_game(id: GID):
    try:
        with cs_database() as db:
            query = 'DELETE FROM Game WHERE id = id'
            cursor = db.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            return result
    except Exception as e:
        print(e)
        return None
