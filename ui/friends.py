from typing import Dict
from backend.player import Player, search_player_by_email, get_player, player_follows_player, follow_player, unfollow_player
import urwid


class FriendsSearchPage:
    def __init__(self, switch_menu, player: Player, args: Dict):
        self.switch_menu = switch_menu
        self.player = player
        self.email_inp = urwid.Edit("Email: ")
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
        self.switch_menu("main", {})

    def submit_pressed(self, button: urwid.Button):
        email = self.email_inp.get_edit_text()
        l = search_player_by_email(email, self.player.username)
        self.switch_menu("friends.results", {"players": l})


class FriendResultsPage:
    def __init__(self, switch_menu, player: Player, args: Dict):
        self.switch_menu = switch_menu
        self.player = player
        self.players = args["players"]
        body = [
            urwid.Button("Back", self.back_pressed),
            urwid.Text("Users: (press enter to see info)"),
            urwid.Pile([urwid.Button(uname, self.upressed, uname)
                       for uname in self.players]),
            urwid.Divider(),
        ]

        pile = urwid.Pile(body)
        self.widget = urwid.Filler(pile)

    def back_pressed(self, button: urwid.Button):
        self.switch_menu("back", {})

    def upressed(self, button: urwid.Button, uname: str):
        player = get_player(uname)
        follows = player_follows_player(self.player.username, uname)

        self.switch_menu("friends.info", {
                         "player": player, "follows": follows})


class FriendInfoPage:
    def __init__(self, switch_menu, player: Player, args: Dict):
        self.switch_menu = switch_menu
        self.player = player

        self.lookat: Player = args["player"]
        self.follows: bool = player_follows_player(
            self.player.username, self.lookat.username)
        body = [
            urwid.Button("Back", self.back_pressed),
            urwid.Divider(),
            # urwid.Text(repr(self.lookat)),
            urwid.Text(
                ("You follow " if self.follows else "You do not follow ")+self.lookat.username),
            urwid.Button(
                "Follow" if not self.follows else "Unfollow", self.pressed)

        ]

        pile = urwid.Pile(body)
        self.widget = urwid.Filler(pile)

    def pressed(self, button: urwid.Button):
        if self.follows:
            unfollow_player(self.player.username, self.lookat.username)
        else:
            follow_player(self.player.username, self.lookat.username)
        self.switch_menu("friends.info", {
            "player": self.lookat, })

    def back_pressed(self, button: urwid.Button):
        self.switch_menu("friends", {})
