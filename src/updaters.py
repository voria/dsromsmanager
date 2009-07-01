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

import gettext
_ = gettext.gettext

import gtk

from urllib2 import urlopen

from globals import *
from downloaders import *
from dat import *
from db import *

class DBImagesUpdater(threading.Thread):
	""" Update images paths in database """
	def __init__(self, gui, path):
		threading.Thread.__init__(self, name="DBImagesUpdater")
		self.gui = gui
		self.path = path
	
	def run(self):
		self.gui.deactivate_widgets(True)
		self.gui.update_statusbar("DBImagesUpdater", _("Updating database with the new 'Images' path..."), True)
		
		db = DB(DB_FILE)
		db.update_images_path(self.path)

		self.gui.update_statusbar("DBImagesUpdater", _("Database updated."), True)
		self.gui.activate_widgets(True)
	
	def stop(self):
		return
		

class DatUpdater(threading.Thread):
	""" Update DAT file if needed """
	def __init__(self, gui, threads, buttons, dat_version, dat_version_url):
		threading.Thread.__init__(self, name="DatUpdater")
		self.dat_version = dat_version
		self.dat_version_url = dat_version_url
		self.gui = gui
		self.threads = threads
		self.buttons = buttons
		
		for button in self.buttons:
			button.set_sensitive(False)
	
	def run(self):
		try:
			self.gui.update_statusbar("DatUpdater", _("Searching for a new DAT file..."), True)
			try:
				new_version_file = urlopen(self.dat_version_url)
				new_version = new_version_file.read()
							
				if int(self.dat_version) < int(new_version):
					self.gui.update_statusbar("DatUpdater", _("New DAT file available!"), True)
					# Make sure we are not downloading all images
					# No need to check if we are rebuilding archives, because we can't be here if it's so.
					for thread in self.threads:
						if thread.isAlive() and thread.getName() == "AllImagesDownloader":
							thread.stop()
							thread.join()
							break
					# Deactivate all widgets
					self.gui.deactivate_widgets(True)
					# Download new DAT file
					datdownloader = DatDownloader(self.gui)
					datdownloader.start()
					datdownloader.join()
					self.gui.update_statusbar("DatUpdater", _("Loading the new DAT file and creating database..."), True)
					dat = Dat(DAT_NAME)
					self.gui.update_statusbar("DatUpdater", _("Database created."), True)
					self.gui.add_games(True)
				else:
					self.gui.update_statusbar("DatUpdater", _("DAT file is already up to date to the latest version."), True)
			except:
				self.gui.update_statusbar("DatUpdater", _("Can't download DAT version file!"), True)
				raise
		finally:
			# reactivate widgets
			self.gui.activate_widgets(True)
			self.gui.set_previous_treeview_cursor(True)
		
	def stop(self):
		return
