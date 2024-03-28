from typing import Optional
import datetime
from backend.owned_game import OwnedGame
from database import cs_database

class Player:
	"""Class for keeping important details of a user"""
	username: str
	first_name: str
	last_name: str
	creation_date: datetime.date
	last_online_date: datetime.date

	def __init__(self, username: str, first_name: str, last_name: str):
		self.username = username
		self.first_name = first_name
		self.last_name = last_name

	def get_platforms_owned():
		raise NotImplementedError
	
	def get_owned_games(self):
		try:
			with cs_database() as db:
				query = 'SELECT gid, username, star_rating, review_text FROM owned_games WHERE username=%s'
				cursor = db.cursor()
				cursor.execute(query, (self.username,))
				results = cursor.fetchall()
				ret = []
				for result in results:
					owned_game = OwnedGame(result[0], result[1], result[2], result[3])
					ret.append(owned_game)
				return ret
		except Exception as e:
			print(e)
			# No such user found (or database down)
			return None

def get_user(username: str) -> Optional[Player]:
	try:
		with cs_database() as db:
			query = 'select P.first_name, P.last_name, P.creation_date from "Player" P where P.username=%s'
			cursor = db.cursor()
			cursor.execute(query, (username,))
			result = cursor.fetchone()
			return result
	except Exception as e:
		print(e)
		# No such user found (or database down)
		return None


def add_user(username: str, first_name: str, last_name: str, password: str):
	creation_date = datetime.datetime.now()
