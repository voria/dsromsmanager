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

from globals import *

from gui import Gui
from downloaders import DatDownloader
from dat import Dat
from db import DB

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
		
		self.gui = Gui(self.threads)
		#self.threads.append(self.gui)
		self.gui.start()
		
		if not os.path.exists(DB_FILE):
			if self.stopnow == False:
				self.gui.show_info_dialog("No database found.\n\nA new DAT file will be automatically downloaded.")
			datdownloader = DatDownloader(self.gui)
			self.threads.append(datdownloader)
			datdownloader.start()
			datdownloader.join()
			# Now we have the DAT file
			if self.stopnow == False:
				self.gui.update_statusbar("Dat", "Loading DAT file and creating database...")
				dat = Dat(DAT_NAME)
			if self.stopnow == False:
				self.gui.update_statusbar("Dat", "Database created.")
		
		# Pass control to the gui
		if self.stopnow == False:
			self.gui.update_statusbar("DB", "Loading database...")
		self.gui.open_db()
		if self.stopnow == False:
			self.gui.update_statusbar("DB", "Database loaded.")
		self.gui.add_games()

	def stop(self):
		self.stopnow = True
		
if __name__ == "__main__":
	m = Main()
	m.start()