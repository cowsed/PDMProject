import urwid
from backend import user


def begin():
	print("strartiing")
	print(user.get_user("u").username)
