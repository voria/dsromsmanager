#!/usr/bin/env python
#
# DRM - DsRomsManager
#
# Copyright (C) 2008 by
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
import threading

import locale, gettext
_ = gettext.gettext

from globals import *

from gui import *
from downloaders import DatDownloader
from dat import *
from db import *

class Main(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self, name="Main")
		self.threads = [] # Keep track of all threads
		self.threads.append(self)
		self.stopnow = False
		
	def run(self):
		if not os.path.exists(WORK_DIR): # First run
			os.mkdir(WORK_DIR)
			os.mkdir(IMG_DIR)
		
		os.chdir(WORK_DIR)
		
		if not os.path.exists(CFG_FILE):
			config_file = open(CFG_FILE, "w")
			config_file.write(DEFAULT_CFG_FILE)
			config_file.flush()
		
		self.gui = Gui(self.threads)
		self.gui.start()
		
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
			if db_deleted == True:
				if self.stopnow == False:
					self.gui.show_info_dialog(_("""Database out of date or corrupt, it has been deleted.\n\n
A new DAT file will be automatically downloaded and a new database will be created."""))
			else:
				if self.stopnow == False:
					self.gui.show_info_dialog(_("""No database found.\n\n
A new DAT file will be automatically downloaded and a new database will be created."""))
			datdownloader = DatDownloader(self.gui)
			self.threads.append(datdownloader)
			datdownloader.start()
			datdownloader.join()
			# Now we have the DAT file
			if self.stopnow == False:
				self.gui.update_statusbar("Dat", _("Loading DAT file and creating database..."))
				dat = Dat(DAT_NAME)
			if self.stopnow == False:
				self.gui.update_statusbar("Dat", _("Database created."))
		
		# Pass control to the gui
		if self.stopnow == False:
			self.gui.update_statusbar("DB", _("Loading database..."))
		self.gui.open_db()
		if self.stopnow == False:
			self.gui.update_statusbar("DB", _("Database loaded."))
		self.gui.add_games()

	def stop(self):
		self.stopnow = True
		
if __name__ == "__main__":
	
	try:
		locale.setlocale(locale.LC_ALL, '')
	except:
		pass
	gettext.bindtextdomain(APP_NAME, LOCALE_DIR)
	gettext.textdomain(APP_NAME)
	
	m = Main()
	m.start()