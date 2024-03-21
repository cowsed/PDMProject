import datetime
from enum import Enum
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

def search_games(title: str):
	# SEARCH BY: name, platform, release date, developers, price, and genre
	# RETURNS: name, platforms, the developers, the publisher, the playtime, and the ratings
	try:
		print("search moment")
		with cs_database() as db:
			# TODO get reviews, and playtime
			query = '\
				SELECT G.title, \
					   (SELECT name FROM "Platform" WHERE platformid=GOP.platformid), \
					   array(SELECT developer FROM "Development" WHERE gameid=G.gameid), \
					   G.publisher, \
					   G.esrb_rating \
				FROM "Game" G \
				NATURAL JOIN "GameOnPlatform" GOP \
				WHERE UPPER(title) LIKE UPPER(%s) \
			'
			cursor = db.cursor()
			cursor.execute(query, ('%' + title + '%',))
			result = cursor.fetchall()
			return result
	except Exception as e:
		print(e)
		# No such user found (or database down)
		return None

def get_all_games():
	try:
		with cs_database() as db:
			query = 'select G.title, G.esrb_rating, G.publisher from "Game" G'
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
					VALUES ((SELECT gameid FROM "Game" WHERE title=%s), \
				            (SELECT platformid FROM "Platform" WHERE name=%s), %s, %s) \
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
					VALUES ((SELECT gameid FROM "Game" WHERE title=%s), %s) \
				'
				cursor = db.cursor()
				cursor.execute(query, (game_title, developer_name))
				db.commit()
	except Exception as e:
		print(e)