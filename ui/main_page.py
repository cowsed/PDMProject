import datetime
import urwid
from backend import player, game, platform

def begin():
	print("starting")
	games = game.search_games(title="vermintide", genre="Co-op")
	for vgame in games:
		print(vgame)

	# developers = game.get_all_development()
	# for developer in developers:
	# 	print(developer)
	
	# platforms = platform.get_all_platforms()
	# for pform in platforms:
	# 	print(pform)

	# games = game.get_all_games()
	# for vgame in games:
	# 	print(vgame)

	# platforms = game.get_all_game_on_platform()
	# for game_on_platform in platforms:
	# 	print(game_on_platform)