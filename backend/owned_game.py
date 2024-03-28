# from backend.player import Player, get_user
from database import cs_database
from backend.game import GID, Game

class OwnedGame:
    gid: GID
    username: str
    star_rating: int
    review_text: str

    def __init__(self, gid, username, star_rating, review_text) -> None:
        self.gid = gid
        self.username = username
        self.star_rating = star_rating
        self.review_text = review_text

    # def get_player(self) -> Player:
    #     return get_user(self.username)
    
    def get_game(self) -> Game:
        return Game.get_game(self.gid)

    def save(self) -> None:
        try:
            with cs_database() as db:
                query = "UPDATE owns_game as og SET star_rating=%s, review_text=%s WHERE og.gid=%d and og.username=%s"
                cursor = db.cursor()
                cursor.execute(query, (self.star_rating, self.review_text, self.gid, self.username))
        except Exception as e:
            # No such user found (or database down)
            print(e)
            

    def set_rating(self, star_rating, review_text) -> None:
        self.star_rating = star_rating
        self.review_text = review_text
        self.save()


        