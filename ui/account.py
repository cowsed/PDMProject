import urwid
from typing import Dict
from backend.player import Player, change_names, get_num_created_collections, get_num_followers, get_num_following, get_top_ten_video_games


class AccountPage:
    def __init__(self, switch_menu, player: Player, args: Dict):
        self.switch_menu = switch_menu
        self.player = player
        body = [urwid.Text("Account: " + player.username),
                urwid.Text(player.first_name + " " + player.last_name),
                urwid.Divider(),
                urwid.Text("Last Online: %s" % player.last_online),
                urwid.Text("Account Created: %s" % player.creation_date),
                urwid.Divider(), 
                urwid.Text("Collections: %s" % get_num_created_collections(player.username)),
                urwid.Text("Followers: %s" % get_num_followers(player.username)),
                urwid.Text("Following: %s" % get_num_following(player.username)),
                urwid.Divider(),]

        button = urwid.Button("Change Name")
        urwid.connect_signal(button, "click", self.item_chosen, "Change Name")
        body.append(urwid.AttrMap(button, None, focus_map="reversed"))

        body.append(urwid.Divider())
        button = urwid.Button("Top 10 Video Games")
        urwid.connect_signal(button, "click", self.item_chosen, "Top 10 Video Games")
        body.append(urwid.AttrMap(button, None, focus_map="reversed"))

        self.sbgroup = []
        self.sort_by = 1 # sorts by rating by default
        sort_by = urwid.Pile(
            [urwid.Text("Sort By")]+[urwid.RadioButton(self.sbgroup, text, on_state_change=self.set_top_games_sort_by) for text in ["Rating", "Playtime"]])
        body.append(urwid.GridFlow([sort_by], 20, 1, 1, "left"))

        body.append(urwid.Divider())
        button = urwid.Button("Back")
        urwid.connect_signal(button, "click", self.item_chosen, "Back")
        body.append(urwid.AttrMap(button, None, focus_map="reversed"))

        body.append(urwid.Divider())
        body.append(urwid.Text("Press Enter to select an option"))

        self.list = urwid.ListBox(urwid.SimpleFocusListWalker(body))
        self.widget = urwid.Padding(self.list)

    def item_chosen(self, button: urwid.Button, choice: str):
        if choice == "Back":
            self.switch_menu("main", {})
        elif choice == "Change Name":
            self.switch_menu("account.changename", {})
        elif choice == "Top 10 Video Games":
            self.switch_menu("account.top10videogames", {'sort by': self.sort_by})

    def set_top_games_sort_by(self, radio_button, state):
        if state:
            self.sort_by = radio_button.get_label()
            column_map = {
                "Playtime": 0,
                "Rating": 1,
            }

            if self.sort_by in column_map:
                self.sort_by = column_map[self.sort_by]
            else:
                self.sort_by = 1


class ChangeNamePage:
    def __init__(self, switch_menu, player: Player, args: Dict):
        self.player = player
        self.switch_menu = switch_menu
        self.login_title = urwid.Text(u"Change Name", align=urwid.CENTER)

        self.fname = urwid.Edit("First Name: ", player.first_name)
        self.lname = urwid.Edit("Last Name: ", player.last_name)

        self.submit_button = urwid.Button(
            "Submit", on_press=self.item_chosen, user_data="Submit")
        self.back_button = urwid.Button(
            "Back", on_press=self.item_chosen, user_data="Back")

        parts = [
            self.login_title,
            urwid.Divider(),
            self.fname,
            self.lname,
            urwid.Divider(),
            self.submit_button,
            urwid.Divider(),
            self.back_button,
        ]
        pile = urwid.Pile(parts)
        self.widget = urwid.Filler(pile)

    def item_chosen(self, button: urwid.Button, choice: str) -> None:

        if choice == "Back":
            self.switch_menu("account", {})
        elif choice == "Submit":
            fname = self.fname.get_edit_text()
            lname = self.lname.get_edit_text()
            if len(fname) == 0:
                self.login_titile.set_text("Please enter a first name")
                return
            if len(lname) == 0:
                self.login_titile.set_text("Please enter a last name")
                return
            change_names(self.player.username, fname, lname)
            self.switch_menu("account", {}, True)

class Top10VideoGamesPage:
    def __init__(self, switch_menu, player: Player, args: Dict):
        self.player = player
        self.switch_menu = switch_menu
        self.title = urwid.Text(u"Top 10 Video Games", align=urwid.CENTER)

        self.back_button = urwid.Button(
            "Back", on_press=self.item_chosen, user_data="Back")
        
        self.games_list = get_top_ten_video_games(player.username, args['sort by'])

        body = [self.title,
                urwid.Divider(),
        ]

        body.append(urwid.Columns([
                urwid.Text("Game"),
                urwid.Text("Rating"),
                urwid.Text("Playtime"),
            ], 15))
        body.append(urwid.Divider())
        for game in self.games_list:
            row = urwid.Columns([
                urwid.Text(game[0]),
                urwid.Text(str(game[1]) if game[1] != None else "Unrated"),
                urwid.Text(str(round(game[2] / 3600, 2)) + " hours" if game[2] != None else "Unplayed"),
            ], 15)
            body.append(row)

        if len(self.games_list) == 0:
            body.append(urwid.Text(u"You have no video games", align=urwid.CENTER))

        body.append(urwid.Divider())
        body.append(self.back_button)

        pile = urwid.Pile(body)
        self.widget = urwid.Filler(pile)

    def item_chosen(self, button: urwid.Button, choice: str) -> None:

        if choice == "Back":
            self.switch_menu("account", {})