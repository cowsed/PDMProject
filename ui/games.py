from backend.player import Player
from typing import Dict
import urwid

class GamesPage:
    def __init__(self, switch_menu, player: Player, args: Dict):
        self.switch_menu = switch_menu
        self.player = player

        parts = [
            urwid.Text("Games"),
            urwid.Divider(),
            urwid.Button("Search Games", self.pressed, user_data="games.search"),
            urwid.Button("Back", self.pressed, user_data="main")
        ]

        self.widget = urwid.Filler(urwid.Pile(parts))

    def pressed(self, b: urwid.Button, dat: str):
        self.switch_menu(dat, {})