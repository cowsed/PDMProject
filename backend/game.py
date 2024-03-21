from enum import Enum
from database import cs_database


class GID:
    id: int


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
    rating: ESRBRating


def get_game(id: GID):
    try:
        with cs_database() as db:
            query = 'SELECT name, rating from "Game" where G.id=%s'
            cursor = db.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            return result
    except Exception as e:
        # no game found
        print(e)
        return None


def add_game(name: str, id: GID, rating: ESRBRating):
    try:
        with cs_database() as db:
            query = 'INSERT INTO "Game" (name, id, rating)'
            cursor = db.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            return result
    except Exception as e:
        print(e)
        return None
