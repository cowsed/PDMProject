from typing import Dict
from backend.player import Player
import urwid

class CollectionsPage:
    def __init__(self ,switch_menu, player: Player, args: Dict):
        self.switch_menu = switch_menu
        self.player = player

        self.back_button = urwid.Button("Back", self.pressed, "")

        self.create_button = urwid.Button("Create Collection", self.pressed, "")


        collections = ["todo", "load", "actual", "collections", "asdasdasas", "asdsadas", "asdsadasd", "asdasda", "asddasdas", "collections", "asdasdasas", "asdsadas", "asdsadasd", "asdasda", "asddasdas"]
        
        parts = [
            urwid.Text("Collections"),
            urwid.Divider(),
            self.create_button, 
            urwid.Divider(),
        ]
        for c in collections:
            parts.append(urwid.Button(c, self.pressed, c))


        parts.append(urwid.Divider())
        parts.append(self.back_button)

        pile = urwid.Pile(parts)

        self.widget= urwid.Filler(pile)
    def pressed(self, b: urwid.Button, dat: str):
        if b == self.back_button:
            self.switch_menu("main", {})
        if b == self.create_button:
            self.switch_menu("collections.new", {})


class NewCollection():
    def __init__(self ,switch_menu, player: Player, args: Dict):
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
        if dat=="create":
            raise NotImplementedError("Creating new collection")
        elif dat == "back":
            self.switch_menu("colections", {})
        pass