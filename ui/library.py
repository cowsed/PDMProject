from backend.player import Player
from typing import Dict
import urwid


class LibraryPage:
    def __init__(self, switch_menu, player: Player, args: Dict):
        self.switch_menu = switch_menu
        self.player = player

        parts = [
            urwid.Text(player.username + "'s Library"),
            urwid.Divider(),
            urwid.Text("Games:"),
        ]
        games = ["link game", "mario game"]
        for g in games:
            parts.append(urwid.Button(g, self.pressed, g))

        self.back_btn = urwid.Button("Back", self.pressed, "")
        parts += [urwid.Divider(), self.back_btn]

        self.widget = urwid.Filler(urwid.Pile(parts))

    def pressed(self, b: urwid.Button, dat: str):
        if b == self.back_btn:
            self.switch_menu("back", {})
        self.switch_menu("library.onegame", {"game": dat, "gameid": 123})


class ViewOnePage:
    def __init__(self, switch_menu, player: Player, args: Dict):
        self.switch_menu = switch_menu
        self.player = player

        self.back_btn = urwid.Button("Back", self.pressed, "")
        self.record_time = urwid.Button("Record Playtime", self.pressed, "")

        parts = [
            urwid.Text("Game: gamename"),
            urwid.Divider(),
        ]
        games = ["link game", "mario game"]
        for g in games:
            parts.append(urwid.Button(g, self.pressed, g))

        self.widget = urwid.Filler(urwid.Pile(parts))

    def pressed(self, b: urwid.Button, dat: str):
        if b == self.back_btn:
            self.switch_menu("library", {})
        elif b == self.record_time:
            self.switch_menu("library.onegame.record_time",
                             {"game": dat, "gameid": 123})
