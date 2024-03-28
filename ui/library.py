from backend.player import Player
from backend.game import get_owned_games, get_game, GID
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

        self.games = get_owned_games(self.player.username)

        for g in self.games:
            parts.append(urwid.Button(g.name, self.pressed, g.id))

        self.back_btn = urwid.Button("Back", self.backpressed)
        parts += [urwid.Divider(), self.back_btn]

        self.widget = urwid.Filler(urwid.Pile(parts))

    def backpressed(self, b: urwid.Button):
        self.switch_menu("back", {})

    def pressed(self, b: urwid.Button, dat: GID):
        self.switch_menu("library.onegame", {"gameid": dat})


class ViewOnePage:
    def __init__(self, switch_menu, player: Player, args: Dict):
        self.switch_menu = switch_menu
        self.player = player

        self.gameid = args["gameid"]
        self.game = get_game(self.gameid)
        self.back_btn = urwid.Button("Back", self.pressed)
        self.record_time = urwid.Button("Record Playtime", self.pressed)

        parts = [
            self.back_btn,
            urwid.Text("Game: "+self.game.name),
            urwid.Divider(),
            self.record_time,
        ]

        self.widget = urwid.Filler(urwid.Pile(parts))

    def pressed(self, b: urwid.Button):
        if b == self.back_btn:
            self.switch_menu("library", {})
        elif b == self.record_time:
            self.switch_menu("library.onegame.record_time",
                             {"game": self.game, "gid": self.game.id})
