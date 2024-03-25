from backend.player import Player
import backend.platform as platform
from typing import Dict
import urwid


class GamesPage:
    def __init__(self, switch_menu, player: Player, args: Dict):
        self.switch_menu = switch_menu
        self.player = player

        self.title_inp = urwid.Pile([urwid.Edit("Title: ")])
        self.rating_inp = urwid.Pile(
            [urwid.Text("Rating:"), urwid.CheckBox("Everyone"), urwid.CheckBox("Everyone 10+"), urwid.CheckBox("Teen"), urwid.CheckBox("Mature 17+"), urwid.CheckBox("Adults Only"), urwid.CheckBox("Rating Pending")])

        platforms = platform.get_all_platforms()
        self.platform_inp = urwid.Pile(
            [urwid.Text("Platform:")] + [urwid.CheckBox(pname) for pname in platforms])

        self.developer_inp = urwid.Edit("Developer: ")

        self.price_low = urwid.Edit("Low:  $", "0.0")
        self.price_high = urwid.Edit("High: $", "10000.0")
        self.price_inp = urwid.Pile(
            [urwid.Text("Price: "), self.price_low, self.price_high])

        print(platforms)

        parts = [
            urwid.Text("Games"),
            urwid.Divider(),
            urwid.Button("Back", self.pressed, user_data="main"),
            urwid.Divider(),
            urwid.Text("Search:"),
            urwid.GridFlow([self.title_inp, self.rating_inp,
                           self.platform_inp, self.developer_inp, self.price_inp], 20, 1, 1, "left")

        ]

        self.widget = urwid.Filler(urwid.Pile(parts))

    def pressed(self, b: urwid.Button, dat: str):
        self.switch_menu(dat, {})
