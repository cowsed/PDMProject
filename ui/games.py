from backend.player import Player
import backend.platform as platform
from typing import Dict
import urwid


class GameResultsPage:
    def __init__(self, player: Player, args: Dict):
        self.gamelist = args["games"]
        body = []
        for game in self.gamelist:
            body.append(urwid.Button(game, self.pressed, game))
        pile = urwid.Pile(body)
        self.widget = urwid.Filler(pile)


class GamesPage:
    def __init__(self, switch_menu, player: Player, args: Dict):
        self.switch_menu = switch_menu
        self.player = player

        self.title_inp = urwid.Pile([urwid.Edit("Title: ")])
        rgroup = []
        self.rating_inp = urwid.Pile(
            [urwid.Text("Rating:"), urwid.RadioButton(rgroup, "Everyone"), urwid.RadioButton(rgroup, "Everyone 10+"), urwid.RadioButton(rgroup, "Teen"), urwid.RadioButton(rgroup, "Mature 17+"), urwid.RadioButton(rgroup, "Adults Only"), urwid.RadioButton(rgroup, "Rating Pending")])

        platforms = platform.get_all_platforms()
        pgroup = []
        self.platform_inp = urwid.Pile(
            [urwid.Text("Platform:")] + [urwid.RadioButton(pgroup, pname) for pname in platforms])

        self.developer_inp = urwid.Edit("Developer: ")

        self.price_low = urwid.Edit("Low:  $", "0.0")
        self.price_high = urwid.Edit("High: $", "10000.0")
        self.price_inp = urwid.Pile(
            [urwid.Text("Price: "), self.price_low, self.price_high])

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
