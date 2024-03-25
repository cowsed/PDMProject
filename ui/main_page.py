from ui.login_page import LoginPage
import urwid
from backend.player import Player
from typing import Hashable, Callable, Any, Iterable, Dict

from ui.account import AccountPage, ChangeNamePage
from ui.games import GamesPage
from ui.collection import CollectionsPage





class MainPage():
	player: Player
	def __init__(self, switch_menu, player: Player):
		self.switch_menu = switch_menu
		self.player = player

		body = [urwid.Text("Menu: "+player.username), urwid.Divider()]

		for c in ["Account", "Games", "Collections", "Quit"]:
			button = urwid.Button(c)
			urwid.connect_signal(button, "click", self.item_chosen, c)
			body.append(urwid.AttrMap(button, None, focus_map="reversed"))

		body.append(urwid.Divider())
		body.append(urwid.Text("Press Enter to select an option"))
		self.list =  urwid.ListBox(urwid.SimpleFocusListWalker(body))		
		
		self.widget = urwid.Padding(self.list)

	def item_chosen(self, button: urwid.Button, choice: str) -> None:
		match choice:
			case "Account":
				switch_menu("account", {})
			case "Games":
				switch_menu("games", {})
			case "Collections":
				switch_menu("collections", {})
			case "Quit":
				switch_menu("quit", {})
		pass

next_menu = "main"
next_args = {}
def switch_menu(towhat: str, args: Dict):
	global next_menu, next_args
	next_menu = towhat
	next_args = args
	raise urwid.ExitMainLoop()

def begin():
	lp = LoginPage()
	loop = urwid.MainLoop(urwid.Filler(urwid.Padding(lp.widget, urwid.CENTER)))
	loop.run()
      
	if lp.user == None:
		print("Quitting...")
		return


	menu = MainPage(switch_menu, lp.user)
	choices = {
		"main" : lambda args : MainPage(switch_menu, lp.user),
		"account": lambda args: AccountPage(switch_menu, lp.user, args),
		"account.changename": lambda args: ChangeNamePage(switch_menu, lp.user, args),
		"games": lambda args: GamesPage(switch_menu, lp.user, args),
		"collections":lambda args: CollectionsPage(switch_menu, lp.user, args) 
	}


	while(1):
		if next_menu == "quit":
			return
		try:
			menu = choices[next_menu]
		except KeyError:
			return


		new_widget = menu(next_args).widget
		loop = urwid.MainLoop(new_widget)
		loop.run()


		