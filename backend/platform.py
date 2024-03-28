from database import cs_database


class PlatformID:
    id: int

    def __init__(self, id: int):
        self.id = id


class Platform:
    name: str
    id: PlatformID

    def __init__(self, name: str, id: PlatformID):
        self.name = name
        self.id = id


def get_all_platforms():
    try:
        with cs_database() as db:
            query = 'select P.name from "Platform" P'
            cursor = db.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            res2 = [v[0] for v in result]
            return res2
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
