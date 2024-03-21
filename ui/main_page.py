from __future__ import annotations
import urwid
from backend import player
from typing import List
import typing

class LoginPage(urwid.WidgetWrap):
	signals: typing.ClassVar[list[str]] = ["close"]

	def __init__(self):
		self.user = None

		# close_button = urwid.Button("that's pretty cool")
		self.login_titile = urwid.Text(u"Log In", align=urwid.CENTER)
		self.username_inp = urwid.Edit("Username: ")
		self.password_inp = urwid.Edit("Password: ")
		self.login_button = urwid.Button("Submit")
	
		urwid.connect_signal(self.login_button, "click", self.on_login_pressed)

		login = urwid.Pile(
			[
				self.login_titile,
				self.username_inp,
				self.password_inp,
				self.login_button,
			]
		)

		self.signup_title = urwid.Text(u"Sign Up", align=urwid.CENTER)
		self.username_inp_signup = urwid.Edit("Username: ")
		self.firstname_inp_signup = urwid.Edit("First Name: ")
		self.lastname_inp_signup = urwid.Edit("Last Name: ")
		self.email_inp_signup = urwid.Edit("Email: ")
		self.password_inp_signup = urwid.Edit("Password: ")
		self.create_account_button = urwid.Button("Create account")

		urwid.connect_signal(self.create_account_button, "click", self.on_signup_pressed)

		signup = urwid.Pile(
			[
				self.signup_title,
				self.username_inp_signup,
				self.firstname_inp_signup,
				self.lastname_inp_signup,
				self.email_inp_signup,
				self.password_inp_signup,
                self.create_account_button,
				urwid.Text(" "),
			])

		self.quit_button = urwid.Button("Quit")

		self.widget = urwid.Pile([urwid.Columns([login, signup], 15), self.quit_button])

	def on_quit_pressed(self, _button: urwid.Button):
		raise urwid.ExitMainLoop()
	def	on_signup_pressed(self, _button: urwid.Button):
		username = self.username_inp_signup.edit_text
		firstname = self.firstname_inp_signup.edit_text
		lastname = self.lastname_inp_signup.edit_text
		email = self.email_inp_signup.edit_text
		password = self.password_inp_signup.edit_text

		if len(username) == 0:
			self.signup_title.set_text("please enter a username")
			return
		
		if len(firstname) == 0:
			self.signup_title.set_text("please enter a first name")
			return

		if len(lastname) == 0:
			self.signup_title.set_text("please enter a last name")
			return

		if len(password) == 0:
			self.signup_title.set_text("please enter a password")
			return
		if len(email) == 0:
			self.signup_title.set_text("please enter an email")
			return
		
		try:
			player.add_player(username, firstname, lastname, password, [email])
			pl = player.get_player(username)
			self.user = pl
			raise urwid.ExitMainLoop()
		except player.DuplicateNameException:
			self.signup_title.set_text("Username already in use")
			return


	def on_login_pressed(self, _button: urwid.Button):
		username = self.username_inp.edit_text
		password = self.password_inp.edit_text

		pl = player.get_player(username)

		if pl==None:
			self.login_titile.set_text("Unknown username")
			return
		if password != pl.password:
			self.login_titile.set_text("Incorrect password")
			return

		# logged in successfully
		self.user = pl
		raise urwid.ExitMainLoop()



def begin():
	# loop.run()
	lp = LoginPage()
	loop = urwid.MainLoop(urwid.Filler(urwid.Padding(lp.widget, urwid.CENTER)))
	loop.run()
      
	if lp.user == None:
		print("Quitting...")
		return

	# mp = urwid.Filler(urwid.Padding(MainWindow(), urwid.CENTER, 15))
	# loop = urwid.MainLoop(mp, [("popbg", "white", "dark blue")], pop_ups=True)
	# loop.run()
