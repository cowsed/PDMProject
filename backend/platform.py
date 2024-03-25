from database import cs_database

class PlatformID:
	id: int

class Platform:
	name: str
	id: PlatformID

def get_all_platforms():
	try:
		with cs_database() as db:
			query = 'select P.name from "Platform" P'
			cursor = db.cursor()
			cursor.execute(query)
			result = cursor.fetchall()
			return result
	except Exception as e:
		print(e)
		# No such user found (or database down)
		return None

def add_platform(name: str):
	try:
		with cs_database() as db:
			query = '\
				INSERT INTO "Platform" (name) \
				VALUES (%s) \
			'
			cursor = db.cursor()
			cursor.execute(query, (name,))
			db.commit()
	except Exception as e:
		print(e)