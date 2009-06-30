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

import gtk

from urllib2 import urlopen, HTTPError
from zipfile import ZipFile

from globals import *
from db import *
from dat import *
from files import *

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
			self.gui.update_statusbar("DatUpdater", _("Searching for a new DAT file..."))
			try:
				new_version_file = urlopen(self.dat_version_url)
				new_version = new_version_file.read()
							
				if int(self.dat_version) < int(new_version):
					self.gui.update_statusbar("DatUpdater", _("New DAT file available!"))
					# Make sure we are not downloading all images
					# No need to check if we are rebuilding archives, because we can't be here if it's so.
					for thread in self.threads:
						if thread.isAlive() and thread.getName() == "AllImagesDownloader":
							thread.stop()
							thread.join()
							break
					# Deactivate all widgets
					self.gui.deactivate_widgets()
					# Download new DAT file
					datdownloader = DatDownloader(self.gui)
					datdownloader.start()
					datdownloader.join()
					self.gui.update_statusbar("DatUpdater", _("Loading the new DAT file and creating database..."))
					dat = Dat(DAT_NAME)
					self.gui.update_statusbar("DatUpdater", _("Database created."))
					self.gui.add_games()
				else:
					self.gui.update_statusbar("DatUpdater", _("DAT file is up to date."))
			except:
				self.gui.update_statusbar("DatUpdater", _("Can't download DAT version file!"))
				raise
		finally:
			# reactivate widgets
			self.gui.activate_widgets()
			self.gui.set_previous_treeview_cursor()
		
	def stop(self):
		return

class DatDownloader(threading.Thread):
	""" Download and unzip DAT file """
	def __init__(self, gui):
		threading.Thread.__init__(self, name="DatDownloader")
		self.dat_url = DAT_URL
		self.dat_name_zip = DAT_NAME_ZIP
		self.dat_name = DAT_NAME
		self.gui = gui
	
	def run(self):
		self.gui.update_statusbar("DatDownloader", _("Downloading the new DAT file..."))
		try:
			input = urlopen(self.dat_url)
			output = open(self.dat_name_zip, "wb")
			for data in input:
				output.write(data)
			output.close()
		except:
			self.gui.update_statusbar("DatDownloader", _("Can't download DAT!"))
			raise
		
		self.gui.update_statusbar("FirstRun", _("Unzipping the new DAT file..."))
		zip = ZipFile(self.dat_name_zip, "r")
		file(self.dat_name, "wb").write(zip.read(self.dat_name))
		zip.close()
		os.remove(self.dat_name_zip)
	
	def stop(self):
		return 

class ImagesDownloader(threading.Thread):
	""" Download 'game' images and show them (if possible).
	Take care of local path's creation when needed """
	def __init__(self, gui, game):
		threading.Thread.__init__(self,  name="ImagesDownloader")

		self.fullinfo = game[GAME_FULLINFO]
		self.release_number = game[GAME_RELEASE_NUMBER]
		self.filename1 = game[GAME_IMG1_LOCAL_PATH]
		self.url1 = game[GAME_IMG1_REMOTE_URL]
		self.filename2 = game[GAME_IMG2_LOCAL_PATH]
		self.url2 = game[GAME_IMG2_REMOTE_URL]
		self.range_dir = os.path.join(config.get_option("images_path"), game[GAME_RANGE_DIR])
		
		self.gui = gui
	
	def run(self):
		if os.path.exists(DB_FILE_REBUILD):
			self.gui.update_statusbar("ImagesDownloader", _("Unable to show images. Restart 'DsRomsManager'."))
			return
		
		if not os.path.exists(self.range_dir):
			os.mkdir(self.range_dir)
			
		if not os.path.exists(self.filename1):
			try:
				input = urlopen(self.url1)
				output = open(self.filename1, "wb")
				for data in input:
					output.write(data)
				output.close()
			except HTTPError:
				self.gui.update_statusbar("ImageDownloader",
								_("Error while downloading image 1 for '%s': File not found.") % self.fullinfo)
			else:
				self.gui.update_image(self.release_number, 1, self.filename1)
		
		if not os.path.exists(self.filename2):
			try:
				input = urlopen(self.url2)
				output = open(self.filename2, "wb")
				for data in input:
					output.write(data)
				output.close()
			except HTTPError:
				self.gui.update_statusbar("ImageDownloader",
								_("Error while downloading image 2 for '%s': File not found.") % self.fullinfo)
			else:
				self.gui.update_image(self.release_number, 2, self.filename2)
			
	def stop(self):
		return
		
class AllImagesDownloader(threading.Thread):
	""" Update the gui button and download all missing images """
	def __init__(self, gui, games):
		threading.Thread.__init__(self, name="AllImagesDownloader")
		self.games = games
		self.gui = gui
		self.check_images_crc = config.get_option("check_images_crc")
		self.check_images_notified = False
		self.stopnow = False
	
	def run(self):
		if os.path.exists(DB_FILE_REBUILD):
			self.gui.update_statusbar("AllImagesDownloader", _("Unable to download images. Restart 'DsRomsManager'."))
			return
		
		self.gui.toggle_all_images_download_toolbutton()
		self.gui.update_statusbar("AllImagesDownloader", _("Downloading all images..."))

		for game in self.games:
			if self.stopnow == True:
				break
			
			range_dir = os.path.join(config.get_option("images_path"), game[GAME_RANGE_DIR])
			img1 = game[GAME_IMG1_LOCAL_PATH]
			img2 = game[GAME_IMG2_LOCAL_PATH]
			url1 = game[GAME_IMG1_REMOTE_URL]
			url2 = game[GAME_IMG2_REMOTE_URL]
						
			if not os.path.exists(range_dir):
				os.mkdir(range_dir)
			
			# check images CRC
			if self.check_images_crc == True:
				if self.check_images_notified == False:
				    self.gui.update_statusbar("AllImagesDownloader", _("Checking images integrity..."))
				    self.check_images_notified = True
				if os.path.exists(img1) and game[GAME_IMG1_CRC] != get_crc32(img1):
					os.remove(img1)
				if os.path.exists(img2) and game[GAME_IMG2_CRC] != get_crc32(img2):
					os.remove(img2)

			if not os.path.exists(img1) or not os.path.exists(img2):
				self.gui.update_statusbar("AllImagesDownloader", _("Downloading images for '%s'...") % game[GAME_FULLINFO])
				self.check_images_notified = False
			
			if not os.path.exists(img1):
				try:
					input = urlopen(url1)
					output = open(img1, "wb")
					for data in input:
						output.write(data)
					output.close()
				except HTTPError:
					pass

			if not os.path.exists(img2):
				try:
					input = urlopen(url2)
					output = open(img2, "wb")
					for data in input:
						output.write(data)
					output.close()
				except:
					pass
		
		if self.stopnow == True:
			self.gui.update_statusbar("AllImagesDownloader", _("Download of all images stopped."))
		else:
			self.gui.update_statusbar("AllImagesDownloader", _("Download of all images completed."))
		# restore original button
		self.gui.toggle_all_images_download_toolbutton()
				
	def stop(self):
		""" Stop the thread """
		self.stopnow = True
