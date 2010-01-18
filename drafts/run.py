#!/usr/bin/env python

import gtk
import sys

if __name__ == "__main__":
	builder = gtk.Builder()
	builder.add_from_file("gui.glade")
	builder.connect_signals({ "on_window_destroy" : gtk.main_quit })
	window = builder.get_object("main")
	window.show()
	gtk.main()
