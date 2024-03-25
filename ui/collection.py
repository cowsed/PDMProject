from typing import Dict
from backend.player import Player
from backend.collection import Collection, get_collection
import urwid


class CollectionsPage:
    def __init__(self, switch_menu, player: Player, args: Dict):
        self.switch_menu = switch_menu
        self.player = player

        self.back_button = urwid.Button("Back", self.pressed, "")

        self.create_button = urwid.Button(
            "Create Collection", self.pressed, "")

        self.collections = ["todo", "load", "actual", "collections"]
        self.collectionIDs = {
            self.collections[0]: 4, self.collections[1]: 3, self.collections[2]: 99, self.collections[3]: 2}

        parts = [
            urwid.Text("Collections"),
            urwid.Divider(),
            self.create_button,
            urwid.Divider(),
        ]
        for c in self.collections:
            parts.append(urwid.Button(
                c + "   123 games    playtime: 12234232 minutes", self.pressed, c))

        parts.append(urwid.Divider())
        parts.append(self.back_button)

        pile = urwid.Pile(parts)

        self.widget = urwid.Filler(pile)

    def pressed(self, b: urwid.Button, dat: str):
        if b == self.back_button:
            self.switch_menu("main", {})
        elif b == self.create_button:
            self.switch_menu("collections.new", {})
        # was a collection
        id = self.collectionIDs[dat]
        self.switch_menu("collections.view", {"collection": id})


class NewCollection():
    def __init__(self, switch_menu, player: Player, args: Dict):
        self.switch_menu = switch_menu
        self.player = player

        self.header = urwid.Text("New Collection")
        self.name = urwid.Edit("Name: ")

        parts = [
            self.header,
            urwid.Divider(),

            self.name,

            urwid.Divider(),
            urwid.Button("Create", self.pressed, "create"),
            urwid.Button("Back", self.pressed, "back")

        ]

        self.widget = urwid.Filler(urwid.Pile(parts))

    def pressed(self, b: urwid.Button, dat: str):
        if dat == "create":
            raise NotImplementedError("Creating new collection")
        elif dat == "back":
            self.switch_menu("collections", {})


class ViewCollection():
    def __init__(self, switch_menu, player: Player, args: Dict):
        self.switch_menu = switch_menu
        self.player = player

        parts = [urwid.Text("Collection Viewing"),
                 urwid.Button("Back", self.pressed, "back")]

        self.widget = urwid.Filler(urwid.Pile(parts))
        return
        self.this_collection_id = args["collection"]
        self.collection = get_collection(self.this_collection_id)

        self.header = urwid.Text("Collection: "+self.collection.name)

    def pressed(self, b: urwid.Button, dat: str):
        if dat == "back":
            self.switch_menu("collections", {})
