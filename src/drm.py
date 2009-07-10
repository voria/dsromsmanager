#!/usr/bin/env python
#
# DRM - DsRomsManager
#
# Copyright (C) 2008-2009 by
# Fortunato Ventre (voRia) - <vorione@gmail.com> - <http://www.voria.org>
#
# 'DRM' is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# <http://www.gnu.org/licenses/gpl.txt>

import os
import sys
import threading

import locale, gettext
_ = gettext.gettext

from globals import *

from gui import *
from downloaders import DatDownloader
from dat import *
from db import *

if sys.version_info[0] != 2 or sys.version_info[1] < 6:
	print "This application requires at least Python 2.6 to run."
	sys.exit()

class Main(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self, name = "Main")
		self.threads = [] # Keep track of all threads
		self.threads.append(self)
		
	def run(self):
		
		os.chdir(WORK_DIR)
		
		self.gui = Gui(self.threads)
		self.gui.start()
		
		if config.get_option("enable_splash"):
			self.gui.show_splash_screen(3000, True)
		
		db_deleted = False
		
		if os.path.exists(DB_FILE):
			# check db version
			self.db = DB(DB_FILE)
			db_info = self.db.get_info()
			if db_info == None or db_info[INFO_DB_VERSION] != DB_VERSION:
				# current db is out of date, remove it
				os.remove(DB_FILE)
				db_deleted = True
				
		if not os.path.exists(DB_FILE):
			if db_deleted:
				self.gui.show_info_dialog(_("""Database out of date or corrupt, it has been deleted.\n
A new DAT file will be automatically downloaded and a new database will be created."""), True)
			else:
				self.gui.show_info_dialog(_("""No database found.\n
A new DAT file will be automatically downloaded and a new database will be created."""), True)
			datdownloader = DatDownloader(self.gui)
			self.threads.append(datdownloader)
			datdownloader.start()
			datdownloader.join()
			# Check if we really have the DAT file
			while not os.path.exists(DAT_NAME):
				message = _("Unable to download DAT file. Retry?")
				if self.gui.show_okcancel_question_dialog(message, True) == True: 
					datdownloader = DatDownloader(self.gui)
					self.threads.append(datdownloader)
					datdownloader.start()
					datdownloader.join()
				else: # Exit
					self.gui.stop()
					return
			# Now we have the DAT file
			self.gui.update_statusbar("Dat", _("Loading DAT file and creating database..."), True)
			dat = Dat(DAT_NAME)
			self.gui.update_statusbar("Dat", _("Database created."), True)
		# Pass control to the Gui
		self.gui.add_games(scan_anyway = False, use_threads = True)

	def stop(self):
		return
		
if __name__ == "__main__":
	try:
		locale.setlocale(locale.LC_ALL, '')
	except:
		pass
	gettext.bindtextdomain(APP_NAME.lower(), LOCALE_DIR)
	gettext.textdomain(APP_NAME.lower())
	Main().start()
