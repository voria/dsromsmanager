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
import threading
import shutil

import gettext
_ = gettext.gettext

from urllib2 import urlopen

from globals import *
from downloaders import *
from dat import *
from db import *

class DBImagesUpdater(threading.Thread):
	""" Update images paths in database """
	def __init__(self, gui, path):
		""" Prepare thread """
		threading.Thread.__init__(self, name="DBImagesUpdater")
		self.gui = gui
		self.path = path
	
	def run(self):
		""" Start thread """
		self.gui.deactivate_widgets(True)
		self.gui.update_statusbar("DBImagesUpdater", _("Updating database with the new 'Images' path..."), True)
		
		db = DB(DB_FILE)
		db.update_images_path(self.path)

		self.gui.update_statusbar("DBImagesUpdater", _("Database updated."), True)
		self.gui.activate_widgets(True)
	
	def stop(self):
		""" Stop thread """
		return
		

class DatUpdater(threading.Thread):
	""" Update DAT file if needed """
	def __init__(self, gui, threads, buttons, dat_version, dat_version_url, autorescan_archives):
		""" Prepare thread """
		threading.Thread.__init__(self, name="DatUpdater")
		self.dat_version = dat_version
		self.dat_version_url = dat_version_url
		self.autorescan_archives = autorescan_archives
		self.gui = gui
		self.threads = threads
		self.buttons = buttons
		
		for button in self.buttons:
			button.set_sensitive(False)
	
	def run(self):
		""" Start thread """
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
					# Rename old DAT file, if it exists yet
					backup = DAT_NAME + ".old"
					try:
						shutil.move(DAT_NAME, backup)
					except:
						pass
					# Download new DAT file
					datdownloader = DatDownloader(self.gui)
					datdownloader.start()
					datdownloader.join()
					# Check if we really have the new DAT file
					while not os.path.exists(DAT_NAME):
						message = _("Unable to download DAT file. Retry?")
						if self.gui.show_okcancel_question_dialog(message, True) == True:
							datdownloader = DatDownloader(self.gui)
							datdownloader.start()
							datdownloader.join()
						else:
							shutil.move(backup, DAT_NAME)
							message = _("Previous DAT file has been restored.")
							self.gui.show_info_dialog(message, True)
							return
					# Now we have the DAT file
					self.gui.update_statusbar("DatUpdater", _("Loading the new DAT file and creating database..."), True)
					try:
						dat = Dat(DAT_NAME)
					except: # something goes wrong while loading the new DAT file
						# remove the problematic DAT file
						os.remove(DAT_NAME)
						if os.path.exists(backup): # restore backup if we have it
							message = _("Error while loading the new DAT file. The old one will be restored.")
							self.gui.show_error_dialog(message, True)
							shutil.move(backup, DAT_NAME)
							self.gui.update_statusbar("DatUpdater", _("Reloading the old DAT file and creating database..."), True)
							dat = Dat(DAT_NAME)
						else:
							message = _("Error while loading the new DAT file!")
							self.gui.show_error_dialog(message, True)
							
					self.gui.update_statusbar("DatUpdater", _("Database created."), True)
					if self.autorescan_archives:
						self.gui.add_games(scan_anyway=True, use_threads=True)
					else:
						self.gui.add_games(scan_anyway=False, use_threads=True)
				else:
					self.gui.update_statusbar("DatUpdater", _("DAT file is already up to date to the latest version."), True)
			except:
				self.gui.update_statusbar("DatUpdater", _("Can't download DAT version file!"), True)
		finally:
			# reactivate widgets
			self.gui.activate_widgets(True)
		
	def stop(self):
		""" Stop thread """
		return
