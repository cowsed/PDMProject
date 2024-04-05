from ui.login_page import LoginPage
import urwid
from backend.player import Player, get_player
from typing import Hashable, Callable, Any, Iterable, Dict

from ui.account import AccountPage, ChangeNamePage
from ui.games import GameSearchPage, GameResultsPage, AllGameDataPage, AddGameToCollection, LogGameTime, GameRecommendationPage
from ui.collection import CollectionsPage, NewCollection, ViewCollection
from ui.library import LibraryPage, ViewOnePage, ChangeRating
from ui.friends import FriendsSearchPage, FriendResultsPage, FriendInfoPage


class MainPage():
    player: Player

    def __init__(self, switch_menu, player: Player):
        self.switch_menu = switch_menu
        self.player = player

        body = [urwid.Text("Menu: "+player.username), urwid.Divider()]

        for c in ["Account", "Game Search", "Game Recommendations", "Collections", "Library", "Friends", "Quit"]:
            button = urwid.Button(c)
            urwid.connect_signal(button, "click", self.item_chosen, c)
            body.append(urwid.AttrMap(button, None, focus_map="reversed"))

        body.append(urwid.Divider())
        body.append(urwid.Text("Press Enter to select an option"))
        self.list = urwid.ListBox(urwid.SimpleFocusListWalker(body))

        self.widget = urwid.Padding(self.list)

    def item_chosen(self, button: urwid.Button, choice: str) -> None:
        match choice:
            case "Account":
                switch_menu("account", {})
            case "Game Search":
                switch_menu("games", {})
            case "Game Recommendations":
                switch_menu("recommendations", {})
            case "Collections":
                switch_menu("collections", {})
            case "Library":
                switch_menu("library", {})
            case "Friends":
                switch_menu("friends", {})
            case "Quit":
                switch_menu("quit", {})
        pass


next_menu = "main"
next_args = {}
history = []
user: Player | None = None


def switch_menu(towhat: str, args: Dict, refresh_user: bool = False):
    global user, next_menu, next_args, history
    if refresh_user:
        user = get_player(user.username)

    if towhat == "back":
        if len(history) > 0:
            next_menu = history[-1][0]
            next_args = history[-1][1]
            history = history[:-1]
        else:
            next_menu = "main"
            next_args = {}
    else:
        history.append((next_menu, next_args))
        next_menu = towhat
        next_args = args

    raise urwid.ExitMainLoop()


palette = [
    ("body", "black", "light gray", "standout"),
    ("header", "white", "dark red", "bold"),
    ("screen edge", "light blue", "dark cyan"),
    ("main shadow", "dark gray", "black"),
    ("line", "black", "light gray", "standout"),
    ("bg background", "light gray", "black"),
    ("bg 1", "black", "dark blue", "standout"),
    ("bg 1 smooth", "dark blue", "black"),
    ("bg 2", "black", "dark cyan", "standout"),
    ("bg 2 smooth", "dark cyan", "black"),
    ("button normal", "light gray", "dark blue", "standout"),
    ("button select", "white", "dark green"),
    ("line", "black", "light gray", "standout"),
    ("pg normal", "white", "black", "standout"),
    ("pg complete", "white", "dark magenta"),
    ("pg smooth", "dark magenta", "black"),
]


def begin():
    print("\r\n"*20)  # clear the screen
    lp = LoginPage()
    loop = urwid.MainLoop(urwid.Filler(urwid.Padding(lp.widget, urwid.CENTER)))
    loop.run()

    if lp.user == None:
        print("Quitting...")
        return
    global user
    user = lp.user

    menu = MainPage(switch_menu, lp.user)
    choices = {
        "main": lambda args: MainPage(switch_menu, user),
        "account": lambda args: AccountPage(switch_menu, user, args),
        "account.changename": lambda args: ChangeNamePage(switch_menu, user, args),

        "games": lambda args: GameSearchPage(switch_menu, user, args),
        "games.results": lambda args: GameResultsPage(switch_menu, user, args),
        "games.data": lambda args: AllGameDataPage(switch_menu, user, args),
        "games.add_to_col": lambda args: AddGameToCollection(switch_menu, user, args),
        "games.log_time": lambda args: LogGameTime(switch_menu, user, args),

        "recommendations": lambda args: GameRecommendationPage(switch_menu, user, args),

        "collections": lambda args: CollectionsPage(switch_menu, user, args),
        "collections.new": lambda args: NewCollection(switch_menu, user, args),
        "collections.view": lambda args: ViewCollection(switch_menu, user, args),

        "friends": lambda args: FriendsSearchPage(switch_menu, user, args),
        "friends.results": lambda args: FriendResultsPage(switch_menu, user, args),
        "friends.info": lambda args: FriendInfoPage(switch_menu, user, args),

        "library": lambda args: LibraryPage(switch_menu, user, args),
        "library.onegame": lambda args: ViewOnePage(switch_menu, user, args),
        "library.onegame.record_time": lambda args: LogGameTime(switch_menu, user, args),
        "library.onegame.change_rating": lambda args: ChangeRating(switch_menu, user, args),
    }

    while (1):
        if next_menu == "quit":
            return
        try:
            menu = choices[next_menu]
        except KeyError:
            print("Invalid menu item:", next_menu)
            return

        new_widget = menu(next_args).widget

        loop = urwid.MainLoop(new_widget, palette)
        loop.run()
