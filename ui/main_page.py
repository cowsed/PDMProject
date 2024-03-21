import datetime
import urwid
from backend import player, game, platform

def begin():
	print("starting")
	print(game.search_games("p"))
	#print(game.get_all_games())