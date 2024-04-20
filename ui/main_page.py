from ui.login_page import LoginPage
import urwid
from backend.player import Player, get_player
from typing import Hashable, Callable, Any, Iterable, Dict

from ui.account import AccountPage, ChangeNamePage
from ui.games import GameSearchPage, GameResultsPage, AllGameDataPage, AddGameToCollection, LogGameTime, MostPopularIn90DayPage, Top5ReleasesOfMonth, MostPopularByFollowing
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


def pick_choice(user, args, choice):
    choices = {
        "main": lambda args: MainPage(switch_menu, user),
        "account": lambda args: AccountPage(switch_menu, user, args),
        "account.changename": lambda args: ChangeNamePage(switch_menu, user, args),

        "games": lambda args: GameSearchPage(switch_menu, user, args),
        "games.results": lambda args: GameResultsPage(switch_menu, user, args),
        "games.data": lambda args: AllGameDataPage(switch_menu, user, args),
        "games.add_to_col": lambda args: AddGameToCollection(switch_menu, user, args),
        "games.log_time": lambda args: LogGameTime(switch_menu, user, args),

        "recommendations": lambda args: MostPopularByFollowing(switch_menu, user, args),

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
    return choices[choice](args)


menu_holder = urwid.Filler(urwid.Text("Loading..."))
user = None
history = []


loop: None | urwid.MainLoop = None


def switch_menu(towhat: str, args: Dict):
    global history, menu_holder

    if towhat == "quit":
        raise urwid.ExitMainLoop()

    if towhat == "back":
        if len(history) > 0:
            history.pop()  # remove the current menu so you dont go in circles
            menu_name = history[-1][0]
            menu_args = history[-1][1]
            loop.widget = urwid.Padding(pick_choice(
                user, menu_args, menu_name).widget)
            history = history[:-1]
        else:
            loop.widget = pick_choice(user, {}, "main").widget

    else:
        history.append((towhat, args))
        loop.widget = pick_choice(user, args, towhat).widget


def begin():
    print('\r\n'*100)  # clear the screen
    lp = LoginPage()
    lploop = urwid.MainLoop(urwid.Filler(
        urwid.Padding(lp.widget, urwid.CENTER)))
    lploop.run()

    if lp.user == None:
        print("Quitting...")
        return
    global user
    user = lp.user
    global menu_holder, loop

    loop = urwid.MainLoop(MainPage(switch_menu, user).widget)
    loop.run()
