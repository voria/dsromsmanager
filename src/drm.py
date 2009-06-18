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

class Main(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self, name="Main")
		self.threads = [] # Keep track of all threads
		self.threads.append(self)
		self.stopnow = False
		
	def run(self):
		if not os.path.exists(WORK_DIR): # First run
			os.mkdir(WORK_DIR)
			os.mkdir(os.path.join(WORK_DIR, IMG_DIR))
		os.chdir(WORK_DIR)
		
		self.gui = Gui(self.threads)
		self.threads.append(self.gui)
		self.gui.start()
		
		if not os.path.exists(os.path.join(WORK_DIR, DAT_NAME)):
			if self.stopnow == False:
				self.gui.show_info_dialog("DAT file not found.\n\nA new one will be automatically downloaded.")
			self.datdownloader = DatDownloader(self.gui)
			self.threads.append(self.datdownloader)
			self.datdownloader.start()
			self.datdownloader.join()
		
		if os.path.exists(DAT_NAME):
			if self.stopnow == False:
				self.gui.update_statusbar("Dat", "Loading DAT file...")
			self.dat = Dat(DAT_NAME)

			if self.stopnow == False:
				self.gui.add(self.dat)
				self.gui.update_statusbar("Ready", "DAT file loaded")
	
	def stop(self):
		self.stopnow = True
		
	def get_dat(self):
		""" Returns the loaded DAT file """
		return self.dat

		
if __name__ == "__main__":
	m = Main()
	m.start()