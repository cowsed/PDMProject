from ui.login_page import LoginPage
import urwid



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
