import urwid
from typing import Dict
from backend.player import Player

class AccountPage:
	def __init__(self, switch_menu, player: Player, args: Dict):
		self.switch_menu = switch_menu
		self.player = player
		body = [urwid.Text("Account"), urwid.Divider()]

		for c in ["Change Name", "Back"]:
			button = urwid.Button(c)
			urwid.connect_signal(button, "click", self.item_chosen, c)
			body.append(urwid.AttrMap(button, None, focus_map="reversed"))

		body.append(urwid.Divider())
		body.append(urwid.Text("Press Enter to select an option"))
		self.list =  urwid.ListBox(urwid.SimpleFocusListWalker(body))		
		
		self.widget = urwid.Padding(self.list)

	def item_chosen(self, button: urwid.Button, choice: str):
		if (choice == "Back"):
			self.switch_menu("main", {})
		elif choice == "Change Name":
			self.switch_menu("account.changename", {})

class ChangeNamePage:
	def __init__(self, switch_menu, player: Player, args: Dict):
		self.switch_menu = switch_menu
		self.login_titile = urwid.Text(u"Change Name", align=urwid.CENTER)

		self.fname = urwid.Edit("First Name: ", player.first_name)
		self.lname = urwid.Edit("Last Name: ", player.last_name)

		self.submit_button = urwid.Button("Submit", on_press=self.item_chosen, user_data="Submit")
		self.back_button = urwid.Button("Back", on_press=self.item_chosen, user_data="Back")

		parts = [
			self.login_titile,
			urwid.Divider(),
			self.fname,
			self.lname,
			urwid.Divider(),
			self.submit_button,
			urwid.Divider(),
			self.back_button,
		]
		pile = urwid.Pile(parts)
		self.widget = urwid.Filler(pile)
	def item_chosen(self, button: urwid.Button, choice: str) -> None:
		
		if choice == "Back":
			self.switch_menu("account", {})
		elif choice == "Submit":
			raise NotImplementedError("change name from menu")

