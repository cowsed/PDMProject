import urwid
from backend import player


def begin():
	p = player.get_player("gamer5")
	print("p", p)
	print(p.get_emails())