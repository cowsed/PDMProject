import random

from backend.player import Player, get_top_genre, get_top_developer
import backend.platform as platform
from backend.platform import Platform
from typing import Dict
import urwid
import datetime

from backend.game import Game, GID, purchase_game, get_game, play_game, get_random_genre, get_random_developer
import backend.game as game
import backend.collection as collection
import backend.owns_game as owns_game
from typing import List, Tuple


class LogGameTime:
    def __init__(self, switch_menu, player: Player, args: Dict):
        self.player = player
        self.switch_menu = switch_menu
        self.gid = args["gid"]

        self.game = get_game(self.gid)

        self.back_btn = urwid.Button(
            "Back to search", self.back_pressed)

        self.error_text = urwid.Text("")

        self.start_time = urwid.Edit("Start Time: ", "3/28/2024 12:01 pm")
        self.minute_inp = urwid.Edit("Minutes: ", "0")

        self.widget = urwid.Filler(urwid.Pile([self.back_btn,
                                               self.error_text,
                                               urwid.Divider(),
                                               urwid.Text(self.game.name),
                                               urwid.Divider(),
                                               self.start_time,
                                               urwid.Text(
                                                   "How long did you play for?"),
                                               self.minute_inp,
                                               urwid.Button("Submit", self.submit_pressed)]))

    def back_pressed(self, b: urwid.Button):
        self.switch_menu("back", {})

    def submit_pressed(self, b: urwid.Button):
        playtime = 0
        try:
            playtime = float(self.minute_inp.get_edit_text())
        except:
            self.error_label.set_text("Could not parse number of minutes")
            return

        date_start = datetime.datetime.now()
        # try:
        #     date_start_str = self.start_time.get_edit_text()
        #     date_start = datetime.datetime.strptime(
        #         date_start_str, "%m/%d/%Y %I:%M %p").date()
        # except:
        #     self.error_label.set_text(
        #         "Could not parse time started. Should be in format '3/28/2024 12:01 pm'")
        #     return

        date_end = date_start + datetime.timedelta(minutes=int(playtime))
        print(date_start, " ", date_end)
        play_game(self.gid, self.player.username, date_start, date_end)


class AddGameToCollection:
    def __init__(self, switch_menu, player: Player, args: Dict):
        self.player = player
        self.switch_menu = switch_menu

        self.game: Game = args["game"]
        self.gamelist: List[Game] = args["prevgames"]

        self.library = game.get_owned_games(self.player.username)
        collections = collection.get_owned_collections(self.player.username)
        collection_buttons = [urwid.Button(
            c.title, self.col_selected, c.id) for c in collections]

        self.back_btn = urwid.Button("Back to Game", self.back_pressed,
                                     "back")

        body = [self.back_btn,
                urwid.Text(f"Add %s to collection" % (self.game.name)),
                urwid.Divider(),
                urwid.Pile(collection_buttons)
                ]

        pile = urwid.Pile(body)
        self.widget = urwid.Filler(pile)

    def back_pressed(self, b: urwid.Button, dat: str):
        self.switch_menu("back", {})

    def col_selected(self, b: urwid.Button, col: collection.CollectionID):
        # do we own the game?
        is_owned = owns_game.user_owns_game(self.game.id, self.player.username)
        if is_owned:
            collection.add_game(col, self.game.id)
            print("Game has been added to the collect.")
            # self.switch_menu(
            #     "games.data", {"gid": self.game.id, "prev_gamelist": self.gamelist})
        else:
            print("You don't own this game")


class AllGameDataPage:

    def __init__(self, switch_menu, player: Player, args: Dict):
        self.player = player
        self.switch_menu = switch_menu
        self.gid = args["gid"]
        self.prev_games = args["prev_gamelist"]

        self.game = game.get_game(self.gid)

        self.back_btn = urwid.Button("Back to Results", self.pressed,
                                     "back")
        self.add_to_collection_btn = urwid.Button(
            "Add to collection", self.pressed, "add")

        ps: List[Tuple[Platform, float, datetime.datetime]
        ] = game.game_platforms(self.game.id)

        def to_button(t: Tuple[Platform, float, datetime.datetime]): return urwid.Button(
            f"%s - $%s - %s  %s" % (t[0].name, t[1], t[2], "✅" if True else "🚫"), self.purchase_pressed)

        platform_info = [to_button(r) for r in ps]
        platform_pile = urwid.Pile(platform_info)

        body = [self.back_btn,
                urwid.Divider(),
                urwid.Text("Game: " + self.game.name),
                urwid.Text("Publisher: " + self.game.publisher),
                urwid.Text("Rating: " + self.game.rating),
                urwid.Divider(),
                self.add_to_collection_btn,
                urwid.Divider(),
                urwid.Text(
                    "✅ you do own this platform 🚫 you don't own this platform"),
                urwid.Divider(),
                urwid.Text("Select a version to purchase: "),
                platform_pile]

        pile = urwid.Pile(body)
        self.widget = urwid.Filler(pile)

    def purchase_pressed(self, b: urwid.Button):
        purchase_game(self.player.username, self.game.id)
        if not self.prev_games:
            self.switch_menu("main", {})
            return
        self.switch_menu("games.results", {"games": self.prev_games})

    def pressed(self, b: urwid.Button, dat: str):
        if b == self.back_btn:
            if not self.prev_games:
                self.switch_menu("main", {})
                return
            self.switch_menu("games.results", {"games": self.prev_games})
            return
        if b == self.add_to_collection_btn:
            if not self.prev_games:
                self.switch_menu("games.add_to_col", {
                    "prevgames": "main", "game": self.game})
                return
            self.switch_menu("games.add_to_col", {
                "prevgames": self.prev_games, "game": self.game})
            return


class GameResultsPage:
    def __init__(self, switch_menu, player: Player, args: Dict):
        self.player = player
        self.switch_menu = switch_menu
        self.back_btn = urwid.Button("Back to search", self.pressed,
                                     "back")
        self.gamelist: List[(Game, str, str, str)] = args["games"]

        body = [self.back_btn, urwid.Divider()]
        for (game, platform, developers, rating) in self.gamelist:
            row = urwid.Columns([
                urwid.Button(game.name, self.pressed, str(game.id.id)),
                urwid.Text(platform + ""),
                urwid.Text(developers),
                urwid.Text(game.rating),
                urwid.Text(str(round(rating, 2))),

            ], 15)
            body.append(row)
        pile = urwid.Pile(body)
        self.widget = urwid.Filler(pile)

    def pressed(self, b: urwid.Button, dat: str):
        if b == self.back_btn:
            self.switch_menu("games", {})
            return

        self.switch_menu("games.data", {"gid": GID(
            int(dat)), "prev_gamelist": self.gamelist})


class GameSearchPage:
    def __init__(self, switch_menu, player: Player, args: Dict):
        self.switch_menu = switch_menu
        self.player = player

        self.title_inp = urwid.Edit("Title: ")

        self.rgroup = []
        self.rating_inp = urwid.Pile(
            [urwid.Text("Rating:"), urwid.RadioButton(self.rgroup, "Any"), urwid.RadioButton(self.rgroup, "Everyone"),
             urwid.RadioButton(self.rgroup, "Everyone 10+"), urwid.RadioButton(self.rgroup, "Teen"),
             urwid.RadioButton(self.rgroup, "Mature 17+"), urwid.RadioButton(self.rgroup, "Adults Only"),
             urwid.RadioButton(self.rgroup, "Rating Pending")])

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

        self.sbgroup = []
        self.sort_by = urwid.Pile(
            [urwid.Text("Sort By")] + [urwid.RadioButton(self.sbgroup, text) for text in
                                       ["Name", "Price", "Genre", "Release Year"]])

        self.sogroup = []
        self.sort_order = urwid.Pile(
            [urwid.Text("Sort Order")] + [urwid.RadioButton(self.sogroup, text) for text in ["ASC", "DESC"]])

        self.rate_group = []
        self.user_rating = urwid.Pile([urwid.Text("Rating")] + [urwid.RadioButton(self.rate_group, text, user_data=num)
                                                                for (text, num) in
                                                                zip([">= 0 stars", ">= 1 star", ">= 2 stars",
                                                                     ">= 3 stars", ">= 4 stars", "5 stars"],
                                                                    [0, 1, 2, 3, 4, 5])])

        self.error_text = urwid.Text("")
        parts = [
            urwid.Text("Games"),
            self.error_text,
            urwid.Button("Back", self.pressed, user_data="main"),
            urwid.Button("Submit", self.pressed, user_data="submit"),
            urwid.Divider(),
            urwid.Text("Search:"),
            urwid.GridFlow([self.title_inp, self.rating_inp,
                            self.platform_inp, self.developer_inp, self.price_inp, self.date_inp, self.user_rating,
                            self.sort_by, self.sort_order], 20, 1, 1, "left")

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
            self.error_text.set_text("Date range error: " + repr(e))
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

        sort_order = list(
            # returns  ASC or DESC
            filter(lambda radio: radio.get_state(), self.sogroup))[0].get_label()

        sort_by = list(
            # returns "Name", "Price", "Genre", or "Release Year"
            filter(lambda radio: radio.get_state(), self.sbgroup))[0].get_label()
        column_map = {
            "Name": 0,
            "Price": 7,
            "Genre": 8,
            "Release Year": 9,
        }
        if sort_by in column_map:
            sort_by = column_map[sort_by]

        esrb = list(filter(lambda radio: radio.get_state(), self.rgroup))[
            0].get_label()
        if esrb == "Any":
            esrb = "%"

        rating = [">= 0 stars", ">= 1 star", ">= 2 stars", ">= 3 stars", ">= 4 stars", "5 stars"].index(
            list(filter(lambda radio: radio.get_state(), self.rate_group))[
                0].get_label())  # returns 0, 1, 2, 3, 4, 5

        games = game.search_games(title, platform, (date_start, date_end),
                                  developer, (price_low, price_high), genre, esrb, rating, sort_by, sort_order)
        self.switch_menu("games.results", {"games": games})

class MostPopularIn90DayPage:
    def __init__(self, switch_menu, player: Player, args: Dict):
        self.switch_menu = switch_menu
        self.back_btn = urwid.Button(
            "Back to all recommendations", self.back_pressed)
        body = [urwid.Text("Top 20 Most Popular Video Games in the Last 90 Days"),
                urwid.Divider()]

        for g in game.get_most_popular_games_past_90_days():
            body.append(urwid.Button(g.name, self.pressed, g.id))

        pile = urwid.Pile(body)
        self.widget = urwid.Filler(pile)

    def back_pressed(self, b: urwid.Button):
        self.switch_menu("back", {})

    def pressed(self, buttone, id):
        self.switch_menu("main", {})

class Top5ReleasesOfMonth:
    def __init__(self, switch_menu, player: Player, args: Dict):
        self.switch_menu = switch_menu
        self.back_btn = urwid.Button(
            "Back to all recommendations", self.back_pressed)
        body = [urwid.Text("Top 5 Releases This Month"),
                urwid.Divider()]

        for g in game.get_top_5_releases_of_month():
            body.append(urwid.Button(g.name, self.pressed, g.id))

        pile = urwid.Pile(body)
        self.widget = urwid.Filler(pile)

    def back_pressed(self, b: urwid.Button):
        self.switch_menu("back", {})

    def pressed(self, buttone, id):
        self.switch_menu("main", {})

class MostPopularByFollowing:
    def __init__(self, switch_menu, player: Player, args: Dict):
        self.switch_menu = switch_menu
        self.back_btn = urwid.Button(
            "Back to all recommendations", self.back_pressed)
        body = [urwid.Text("Top 20 Most Popular Games Video Games Among Your Followers"),
                urwid.Divider()]

        for g in game.get_most_popular_games_by_following(username=player.username):
            body.append(urwid.Button(g.name, self.pressed, g.id))

        pile = urwid.Pile(body)
        self.widget = urwid.Filler(pile)

    def back_pressed(self, b: urwid.Button):
        self.switch_menu("back", {})

    def pressed(self, buttone, id):
        self.switch_menu("main", {})
    
class GameRecommendationPage:
    def __init__(self, switch_menu, player: Player, args: Dict):
        self.switch_menu = switch_menu
        self.player = player
        self.genre = get_top_genre(player.username)
        self.developer = get_top_developer(player.username)
        self.back_btn = urwid.Button("Back", self.back)
        self.random_genre = get_random_genre(self.player.username, self.genre)
        self.random_developer = get_random_developer(self.player.username, self.developer)
        body = [urwid.Text("** Welcome to \"For You\" **\nRecommendations for " + player.username),
                urwid.Divider(),
                urwid.Text("Games based on your favourite genre: " + self.genre)]

        for g in self.random_genre:
            body.append(urwid.Button(g.name, self.pressed, g.id))

        body.append(urwid.Divider())

        body.append(urwid.Text("Games based off your favourite developer " + self.developer))
        for g in self.random_developer:
            body.append(urwid.Button(g.name, self.pressed, g.id))

        body.append(self.back_btn)

        pile = urwid.Pile(body)
        self.widget = urwid.Filler(pile)

    def pressed(self, b: urwid.Button, dat: GID):
        self.switch_menu("games.data", {"gid": dat, "prev_gamelist": False})

    def back(self, b: urwid.Button):
        self.switch_menu("main", {})
