from __future__ import annotations
import urwid
from backend import player
from typing import List
import typing

class LoginPage(urwid.WidgetWrap):
	signals: typing.ClassVar[list[str]] = ["close"]

	def __init__(self):
		# close_button = urwid.Button("that's pretty cool")
		self.title = urwid.Text(u"login", align=urwid.CENTER)
		self.username_inp = urwid.Edit("Username: ")
		self.password_inp = urwid.Edit("Password: ")
		self.submit = urwid.Button("Submit")
		self.create_account_button = urwid.Button("Create account")
	
		urwid.connect_signal(self.submit, "click", self.on_submit_pressed)
		pile = urwid.Pile(
			[
				self.title,
				self.username_inp,
				self.password_inp,
				self.submit,
                urwid.Text("or"),
                self.create_account_button
			]
		)
		super().__init__(urwid.AttrMap(urwid.Filler(pile), "popbg"))

	def on_submit_pressed(self, _button: urwid.Button):
		username = self.username_inp.edit_text
		password = self.password_inp.edit_text
				
		pl = player.get_player(username)

		if pl==None:
			self.title.set_text("Unknown username")
			return
		if password != pl.password:
			self.title.set_text("Incorrect password")
			return

		# logged in successfully
		urwid.emit_signal(self, "close", None)

class MainWindow(urwid.PopUpLauncher):
    def __init__(self) -> None:
        super().__init__(urwid.Button("click-me"))
        urwid.connect_signal(self.original_widget, "click", lambda button: self.open_pop_up())
        urwid.emit_signal(self.original_widget, "click", None)

    def create_pop_up(self) -> LoginPage:
        pop_up = LoginPage()
        urwid.connect_signal(pop_up, "close", lambda button: self.close_pop_up())
        return pop_up

    def get_pop_up_parameters(self):
        return {"left": 0, "top": 0, "overlay_width": 32, "overlay_height": 7}

    def keypress(self, size: tuple[int], key: str) -> str | None:
        parsed = super().keypress(size, key)
        if parsed in {"q", "Q"}:
            raise urwid.ExitMainLoop("Done")
        return parsed



def begin():
	# txt = urwid.Text("Hello World")
	# fill = urwid.Filler(txt, "top")
	# loop = urwid.MainLoop(fill)
	# loop.run()
	lp = urwid.Filler(urwid.Padding(LoginPage(), urwid.CENTER, 15))
	loop = urwid.MainLoop(lp)
	loop.run()

	mp = urwid.Filler(urwid.Padding(MainWindow(), urwid.CENTER, 15))
	loop = urwid.MainLoop(mp, [("popbg", "white", "dark blue")], pop_ups=True)
	loop.run()
