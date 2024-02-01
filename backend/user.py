from typing import Optional
import datetime

class User:
	"""Class for keeping important details of a user"""
	username: str
	creation_date: datetime.date
	last_online_date: datetime.date

	def __init__(self, username: str):
		self.username = username

	def get_platforms_owned():
		raise NotImplementedError

def get_user(username: str) -> Optional[User]:
	# ask db for a user
	#if username not found in db
		# return None
	return User('exampleuser101')
