import datetime
from enum import Enum
import random
import string
from database import cs_database

class GameID:
	id: int

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

class ESRBRating(Enum):
	EVERYONE=1
	EVERYONE_10_PLUS = 2
	TEEN = 3
	ADULTS_ONLY=4
	RATING_PENDING=5
	RATING_PENDING_MATURE=6

class Game:
	name: str
	id: GameID
	rating: ESRBRating

def search_games(title="", platform="", release_date_range=(datetime.date(1800, 1, 1), datetime.date.today()), developers="", price_range=(0.0, float('inf')), genre=""):
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

	Returns
	-------
	list
		A list of each matched game's name, platforms, developers, publisher, playtime, and ratings.
		Each game release on a different platform is considered a different game and listed separately.
	"""

	try:
		with cs_database() as db:
			# TODO get reviews, and playtime
			query = '\
				SELECT G.title, \
					   (SELECT name FROM "Platform" WHERE platformid=GOP.platformid) AS platform, \
					   ARRAY(SELECT developer FROM "Development" WHERE gameid=G.gameid) AS developers, \
					   G.publisher, \
					   G.esrb_rating \
				FROM "Game" G \
				NATURAL JOIN "GameOnPlatform" GOP \
				WHERE UPPER(G.title) LIKE UPPER(%s) \
				  AND UPPER((SELECT name FROM "Platform" WHERE platformid=GOP.platformid)) LIKE UPPER(%s) \
				  AND GOP.release_date >= %s AND GOP.release_date <= %s \
				  AND UPPER(ARRAY_TO_STRING(ARRAY(SELECT developer FROM "Development" WHERE gameid=G.gameid), \',\')) LIKE UPPER(%s) \
				  AND GOP.price >= %s AND GOP.price <= %s \
				  AND UPPER(ARRAY_TO_STRING(ARRAY(SELECT genre_name FROM "Genre" Ge WHERE G.gameid=Ge.gameid), \',\')) LIKE UPPER(%s) \
			'
			cursor = db.cursor()
			cursor.execute(query, ('%' + title + '%', 
						  		   '%' + platform + '%', 
								   release_date_range[0],
								   release_date_range[1],
								   '%' + developers + '%',
								   price_range[0],
								   price_range[1],
								   '%' + genre + '%'))
			result = cursor.fetchall()
			return result
	except Exception as e:
		print(e)
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
				cursor.execute(query, (game_id, platform_id, price, release_date))
				db.commit()
			elif game_title != "" and platform_title != "":
				query = '\
					INSERT INTO "GameOnPlatform" (gameid, platformid, price, release_date) \
					VALUES ((SELECT gameid FROM "Game" WHERE title=%s LIMIT 1), \
				            (SELECT platformid FROM "Platform" WHERE name=%s LIMIT 1), %s, %s) \
				'
				cursor = db.cursor()
				cursor.execute(query, (game_title, platform_title, price, release_date))
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