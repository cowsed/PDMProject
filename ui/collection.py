from typing import Dict
from backend.player import Player
from backend.collection import Collection, CollectionID, get_collection_data, get_owned_collections, create_collection, delete_collection, change_title, get_collection, get_games, delete_game
import urwid
import random


class CollectionsPage:
    def __init__(self, switch_menu, player: Player, args: Dict):
        self.switch_menu = switch_menu
        self.player = player

        self.back_button = urwid.Button("Back", self.pressed, "")

        self.create_button = urwid.Button(
            "Create Collection", self.pressed, "")

        self.collections = get_owned_collections(self.player.username)
        self.collection_data = [get_collection_data(
            col.id, self.player.username) for col in self.collections]

        parts = [
            urwid.Text("Collections"),
            urwid.Divider(),
            self.create_button,
            urwid.Divider(),
        ]
        for c, dat in zip(self.collections, self.collection_data):
            parts.append(urwid.Button(f"%s - %d games - %s hrs " %
                         (c.title, dat[0], dat[1]), self.col_selected, c.id))

        parts.append(urwid.Divider())
        parts.append(self.back_button)

        pile = urwid.Pile(parts)

        self.widget = urwid.Filler(pile)

    def pressed(self, b: urwid.Button, dat: str):
        if b == self.back_button:
            self.switch_menu("main", {})
        elif b == self.create_button:
            self.switch_menu("collections.new", {})

    def col_selected(self, b: urwid.Button, id: CollectionID):
        # was a collection
        self.switch_menu("collections.view", {"collection": id})


class NewCollection():
    def __init__(self, switch_menu, player: Player, args: Dict):
        self.switch_menu = switch_menu
        self.player = player

        self.header = urwid.Text("New Collection")
        self.name = urwid.Edit("Name: ")
        self.visible = urwid.CheckBox("Visible")

        parts = [
            self.header,
            urwid.Divider(),

            self.name,
            self.visible,
            urwid.Divider(),
            urwid.Button("Create", self.pressed, "create"),
            urwid.Button("Back", self.pressed, "back")

        ]

        self.widget = urwid.Filler(urwid.Pile(parts))

    def pressed(self, b: urwid.Button, dat: str):
        if dat == "create":
            visible = self.visible.get_state()
            name = self.name.get_edit_text()

            create_collection(self.player.username, name, visible)

            self.switch_menu("collections", {})
        elif dat == "back":
            self.switch_menu("collections", {})


class ViewCollection():
    def __init__(self, switch_menu, player: Player, args: Dict):
        self.switch_menu = switch_menu
        self.player = player
        self.colID: CollectionID = args["collection"]
        self.col: Collection = get_collection(self.colID)

        self.nameedit = urwid.Edit("Name: ", self.col.title)

        self.delete_btn = urwid.Button(
            "Delete Collection", self.delete_pressed, "delete")

        self.record_random = urwid.Button("Play Random", self.random_pressed)

        settings = urwid.Pile([self.nameedit,
                               urwid.Button(
                                   "Rename", self.pressed, "rename"),
                               self.record_random,
                               urwid.Button(
                                   "Back", self.pressed, "back"),
                               self.delete_btn])
        self.games = get_games(self.colID)
        game_buttons = [urwid.Text("Games: (Press enter to remove game from collection)")] + [urwid.Button(g[0], self.remove_game, g[1])
                                                                                              for g in self.games]
        cols = urwid.Columns(
            [urwid.LineBox(settings), urwid.LineBox(urwid.Pile(game_buttons))])
        parts = [urwid.Text("Collection"),
                 cols]

        self.widget = urwid.Filler(urwid.Pile(parts))

    def random_pressed(self, b: urwid.Button):
        gid = random.sample(self.games, 1)[0][1]
        self.switch_menu("library.onegame.record_time", {"gid": gid})

    def pressed(self, b: urwid.Button, dat: str):
        if dat == "back":
            self.switch_menu("collections", {})
        elif dat == "rename":
            change_title(self.colID, self.nameedit.get_edit_text())
            self.switch_menu("collections", {})

    def delete_pressed(self, b: urwid.Button, dat: str):
        delete_collection(self.colID)
        self.switch_menu("collections", {})

    def remove_game(self, b: urwid.Button, id: CollectionID):
        delete_game(self.colID, id)
        self.switch_menu("collections.view", {"collection": self.colID})
