from ui.login_page import LoginPage
import urwid
from backend.player import Player, get_player
from typing import Hashable, Callable, Any, Iterable, Dict

from ui.account import AccountPage, ChangeNamePage
from ui.games import GamesPage, GameResultsPage, AllGameDataPage, AddGameToCollection
from ui.collection import CollectionsPage, NewCollection, ViewCollection
from ui.library import LibraryPage


class MainPage():
    player: Player

    def __init__(self, switch_menu, player: Player):
        self.switch_menu = switch_menu
        self.player = player

        body = [urwid.Text("Menu: "+player.username), urwid.Divider()]

        for c in ["Account", "Games", "Collections", "Library", "Quit"]:
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
            case "Games":
                switch_menu("games", {})
            case "Collections":
                switch_menu("collections", {})
            case "Library":
                switch_menu("library", {})
            case "Quit":
                switch_menu("quit", {})
        pass


next_menu = "main"
next_args = {}


def switch_menu(towhat: str, args: Dict):
    global next_menu, next_args
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
    lp = LoginPage()
    # loop = urwid.MainLoop(urwid.Filler(urwid.Padding(lp.widget, urwid.CENTER)))
    # loop.run()

    lp.user = get_player("richie3000")

    if lp.user == None:
        print("Quitting...")
        return

    menu = MainPage(switch_menu, lp.user)
    choices = {
        "main": lambda args: MainPage(switch_menu, lp.user),
        "account": lambda args: AccountPage(switch_menu, lp.user, args),
        "account.changename": lambda args: ChangeNamePage(switch_menu, lp.user, args),

        "games": lambda args: GamesPage(switch_menu, lp.user, args),
        "games.results": lambda args: GameResultsPage(switch_menu, lp.user, args),
        "games.data": lambda args: AllGameDataPage(switch_menu, lp.user, args),
        "games.add_to_col": lambda args: AddGameToCollection(switch_menu, lp.user, args),

        "collections": lambda args: CollectionsPage(switch_menu, lp.user, args),
        "collections.new": lambda args: NewCollection(switch_menu, lp.user, args),
        "collections.view": lambda args: ViewCollection(switch_menu, lp.user, args),

        "library": lambda args: LibraryPage(switch_menu, lp.user, args),
        "library.onegame": lambda args: LibraryPage(switch_menu, lp.user, args),
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
