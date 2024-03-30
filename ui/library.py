from backend.player import Player
from backend.game import get_owned_games, get_game, GID
from backend.owns_game import get_ratings, add_rating, delete_rating
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
        self.switch_menu("main", {})

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
        self.change_rating = urwid.Button("Change Rating", self.pressed)
        self.delete_rating = urwid.Button("Delete Rating", self.pressed)
        self.rating = get_ratings(self.gameid, self.player.username)
        self.rating_text = urwid.Text("Rating")

        if self.rating.star_rating is not None:
            self.rating_text.set_text("\n" + str(self.rating.star_rating) + " stars\n" +
                                      (self.rating.review_text or ''))
        else:
            self.rating_text.set_text("\nNo Rating")

        parts = [
            self.back_btn,
            urwid.Text("Game: " + self.game.name),
            urwid.Divider(),
            self.record_time,
            self.change_rating,
            self.delete_rating,
            self.rating_text,
        ]

        self.widget = urwid.Filler(urwid.Pile(parts))

    def pressed(self, b: urwid.Button):
        if b == self.back_btn:
            self.switch_menu("library", {})
        elif b == self.record_time:
            self.switch_menu("library.onegame.record_time",
                             {"game": self.game, "gid": self.game.id})
        elif b == self.change_rating:
            self.switch_menu("library.onegame.change_rating",
                             {"game": self.game, "gid": self.game.id})
        elif b == self.delete_rating:
            delete_rating(self.gameid, self.player.username)


class ChangeRating:
    def __init__(self, switch_menu, player: Player, args: Dict):
        self.switch_menu = switch_menu
        self.player = player

        self.header = urwid.Text("Change Rating")
        self.star = urwid.Edit("Number of Stars: ")
        self.rating = urwid.Edit("Review: ")
        self.gameid = args["gid"]
        self.game = get_game(self.gameid)
        self.back_btn = urwid.Button("Back", self.pressed)

        parts = [
            self.header,
            urwid.Divider(),

            self.star,
            self.rating,
            urwid.Divider(),

            urwid.Button("Change", self.pressed, "change"),
            urwid.Button("Back", self.pressed, self.game.id)
        ]

        self.widget = urwid.Filler(urwid.Pile(parts))

    def pressed(self, b: urwid.Button, dat: GID):
        if dat == "change":
            star = self.star.get_edit_text()
            rating = self.rating.get_edit_text()
            if star != '':
                add_rating(self.gameid, self.player.username, int(star), rating)
        else:
            self.switch_menu("library.onegame", {"gameid": dat})
