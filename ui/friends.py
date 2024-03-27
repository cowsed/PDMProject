from typing import Dict
from backend.player import Player, change_names
import urwid


class FriendsPage:
    def __init__(self, switch_menu, player: Player, args: Dict):
        self.switch_menu = switch_menu
        self.player = player
        self.email_inp = urwid.Edit("Email")
        body = [
            urwid.Button("Back", self.back_pressed),
            urwid.Text("Search for Friends"),
            urwid.Divider(),
            self.email_inp,
            urwid.Button("Submit", self.submit_pressed)
        ]

        pile = urwid.Pile(body)
        self.widget = urwid.Filler(pile)

    def back_pressed(self, button: urwid.Button):
        self.switch_menu("back", {})

    def submit_pressed(self, button: urwid.Button):
        self.switch_menu("main", {})


class FriendResultsPage:
    def __init__(self, switch_menu, player: Player, args: Dict):
        self.switch_menu = switch_menu
        self.player = player
        self.email_inp = urwid.Edit("Email")
        body = [
            urwid.Button("Back", self.back_pressed),
            urwid.Text("Users"),
            urwid.Divider(),
        ]

        pile = urwid.Pile(body)
        self.widget = urwid.Filler(pile)
