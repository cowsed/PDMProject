from typing import Dict
from backend.player import Player
import urwid

class CollectionsPage:
    def __init__(self ,switch_menu, player: Player, args: Dict):
        self.switch_menu = switch_menu
        self.player = player

        self.back_button = urwid.Button("Back", self.pressed, "")

        collections = ["todo", "load", "actual", "collections"]
        
        parts = [
            urwid.Text("Collections"),
            urwid.Divider(),
        ]
        for c in collections:
            parts.append(urwid.Button(c, self.pressed, c))


        parts.append(urwid.Divider())
        parts.append(self.back_button)

        pile = urwid.Pile(parts)

        self.widget= urwid.Filler(pile)
    def pressed(self, b: urwid.Button, dat: str):
        if b == self.back_button:
            self.switch_menu("main", {})
        pass