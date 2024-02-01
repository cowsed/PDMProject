from enum import Enum
class GID:
	id: int

class ESRBRating(Enum):
	EVERYONE=1
	EVERYONE_10_PLUS = 2
	TEEN = 3
	ADULTS_ONLY=4
	RATING_PENDING=5
	RATING_PENDING_MATURE=6

class Game:
	name: str
	id: GID
	rating: ESRBRating
