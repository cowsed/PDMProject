from typing import Optional
import datetime
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
