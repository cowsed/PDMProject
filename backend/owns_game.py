from database import cs_database
from backend.game import Game, GID


class owns_game:
    game: GID
    username: str
    star_rating: int
    review_text: str

    def __init__(self, game: GID, username: str, rating: int, review: str):
        self.game = game
        self.username = username
        self.star_rating = rating
        self.review_text = review

def user_owns_game(game: Game, username):
    try:
        with cs_database() as db:
            data = (game.id, username)
            query = 'select * from "OwnsGame" where gameid=%s and username=%s'
            cursor = db.cursor()
            cursor.execute(query, data)
            db.commit()
            rows = cursor.rowcount
            if rows == 0:
                return False
            return True
    except Exception as e:
        print("owns game error", e)
        return

def add_rating(game: GID, username: str, rating: int, review: str):
    if 0 < rating < 6:
        try:
            with cs_database() as db:
                data = (rating, review, game.id, username)
                query = 'UPDATE "OwnsGame" SET star_rating=%s, review_text=%s \
                         WHERE gameid=%s AND username=%s'
                cursor = db.cursor()
                cursor.execute(query, data)
                db.commit()
        except Exception as e:
            print("add rating error", e)
            return
    else:
        return


def delete_rating(game: Game, username: str):
    try:
        with cs_database() as db:
            data = (game.id, username)
            query = 'UPDATE "OwnsGame" SET star_rating=NULL, review_text=NULL \
                     WHERE gameid=%s AND username=%s'
            cursor = db.cursor()
            cursor.execute(query, data)
            db.commit()
    except Exception as e:
        print("delete rating error", e)
        return


def get_ratings(game: Game, username: str) -> owns_game:
    query = 'SELECT O.star_rating, O.review_text \
             from "OwnsGame" O WHERE O.gameid = %s AND O.username = %s'
    with cs_database() as db:
        data = (game.id, username)
        cursor = db.cursor()
        cursor.execute(query, data)
        res = cursor.fetchone()
        if res == None:
            raise Exception("No ratings found for game", GID.id)
        return owns_game(game, username, res[0], res[1])
