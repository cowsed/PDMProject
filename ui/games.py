from backend.player import Player
import backend.platform as platform
from backend.platform import Platform
from typing import Dict
import urwid
import datetime

from backend.game import Game, GID
import backend.game as game
from typing import List, Tuple


class AllGameDataPage:

    def __init__(self, switch_menu, player: Player, args: Dict):
        self.player = player
        self.switch_menu = switch_menu
        self.gid = args["gid"]

        self.game = game.get_game(self.gid)

        self.back_btn = urwid.Button("Back to search", self.pressed,
                                     "back")

        ps: List[Tuple[Platform, float, datetime.datetime]
                 ] = game.game_platforms(self.game.id)

        def to_button(t: Tuple[Platform, float, datetime.datetime]): return urwid.Button(
            f"%s - $%s - %s  %s" % (t[0].name, t[1], t[2], "✅" if True else "🚫"), self.pressed, t[0].id)

        platform_info = [to_button(r) for r in ps]

        platform_pile = urwid.Pile(platform_info)

        body = [self.back_btn,
                urwid.Divider(),
                urwid.Text("Game: "+self.game.name),
                urwid.Text("Publisher: "+self.game.publisher),
                urwid.Divider(),
                urwid.Text(
                    "✅ you do own this platform 🚫 you don't own this platform"),
                urwid.Divider(),
                urwid.Text("Select a version for more options: "),
                platform_pile]

        pile = urwid.Pile(body)
        self.widget = urwid.Filler(pile)

    def pressed(self, b: urwid.Button, dat: str):
        if b == self.back_btn:
            self.switch_menu("games", {})


class GameResultsPage:
    def __init__(self, switch_menu, player: Player, args: Dict):
        self.player = player
        self.switch_menu = switch_menu
        self.back_btn = urwid.Button("Back to search", self.pressed,
                                     "back")
        self.gamelist: List[Game] = args["games"]

        body = [self.back_btn, urwid.Divider()]
        for game in self.gamelist:
            body.append(urwid.Button(game.name, self.pressed, str(game.id.id)))
        pile = urwid.Pile(body)
        self.widget = urwid.Filler(pile)

    def pressed(self, b: urwid.Button, dat: str):
        if b == self.back_btn:
            self.switch_menu("games", {})

        self.switch_menu("games.data", {"gid": GID(int(dat))})


class GamesPage:
    def __init__(self, switch_menu, player: Player, args: Dict):
        self.switch_menu = switch_menu
        self.player = player

        self.title_inp = urwid.Edit("Title: ")
        rgroup = []
        self.rating_inp = urwid.Pile(
            [urwid.Text("Rating:"), urwid.RadioButton(rgroup, "Everyone"), urwid.RadioButton(rgroup, "Everyone 10+"), urwid.RadioButton(rgroup, "Teen"), urwid.RadioButton(rgroup, "Mature 17+"), urwid.RadioButton(rgroup, "Adults Only"), urwid.RadioButton(rgroup, "Rating Pending")])

        self.platform_inp = urwid.Edit("Platform: ")
        self.developer_inp = urwid.Edit("Developer: ")
        self.genre_inp = urwid.Edit("Genre: ")

        self.price_low = urwid.Edit("Low:  $", "0.0")
        self.price_high = urwid.Edit("High: $", "10000.0")
        self.price_inp = urwid.Pile(
            [urwid.Text("Price: "), self.price_low, self.price_high])

        self.date_low = urwid.Edit("Start:  ", "1/1/1970")
        self.date_high = urwid.Edit("End: ", "1/1/2024")
        self.date_inp = urwid.Pile(
            [urwid.Text("Release Date Range: "), self.date_low, self.date_high])

        self.error_text = urwid.Text("")
        parts = [
            urwid.Text("Games"),
            self.error_text,
            urwid.Button("Back", self.pressed, user_data="main"),
            urwid.Button("Submit", self.pressed, user_data="submit"),
            urwid.Divider(),
            urwid.Text("Search:"),
            urwid.GridFlow([self.title_inp, self.rating_inp,
                           self.platform_inp, self.developer_inp, self.price_inp, self.date_inp], 20, 1, 1, "left")

        ]

        self.widget = urwid.Filler(urwid.Pile(parts))

    def pressed(self, b: urwid.Button, dat: str):
        if dat == "main":
            self.switch_menu("main", {})
        elif dat == "submit":
            self.do_query()

    def do_query(self):
        date_start = datetime.datetime.now()
        date_end = datetime.datetime.now()

        date_start_str = self.date_low.get_edit_text()
        date_end_str = self.date_high.get_edit_text()

        try:
            date_start = datetime.datetime.strptime(
                date_start_str, "%m/%d/%Y").date()
            date_end = datetime.datetime.strptime(
                date_end_str, "%m/%d/%Y").date()
        except Exception as e:
            self.error_text.set_text("Date range error: "+repr(e))
            return

        price_low = 0
        price_high = float('inf')

        try:
            price_low = float(self.price_low.get_edit_text())
            price_high = float(self.price_high.get_edit_text())
        except:
            self.error_text.set_text("Price Parse Error")

        title = self.title_inp.get_edit_text()
        developer = self.developer_inp.get_edit_text()
        platform = self.platform_inp.get_edit_text()
        genre = self.genre_inp.get_edit_text()

        games = game.search_games(title, platform, (date_start, date_end),
                                  developer, (price_low, price_high), genre)
        self.switch_menu("games.results", {"games": games})
