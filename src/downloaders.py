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

import struct
import binascii

from globals import *
from db import *
from dat import *

#===============================================================================
# def get_crc32(filename):
#	""" Return CRC32 of 'filename' """
#	bin = struct.pack('>l', binascii.crc32(file(filename, 'r').read()))
#	return binascii.hexlify(bin).upper()
#===============================================================================

#===============================================================================
# def get_crc32_zip(zipfile):
#	""" Return CRC32 of .nds file contained in 'zipfile'.
#	Return None if no .nds file is found """
#	result = None
#	zip = zipfile.ZipFile(zipfile, "r")
#	for info in zip.infolist():
#		if info.filename[len(info.filename)-4:].lower() == ".nds":
#			crc = struct.pack('>l', info.CRC)
#			result = binascii.hexlify(crc).upper()
#			break
#	zip.close()
#	return result
#===============================================================================

class DatUpdater(threading.Thread):
	""" Update DAT file if needed """
	def __init__(self, gui, buttons, dat_version, dat_version_url):
		threading.Thread.__init__(self, name="DatUpdater")
		self.dat_version = dat_version
		self.dat_version_url = dat_version_url
		self.gui = gui
		self.buttons = buttons
		
		for button in self.buttons:
			button.set_sensitive(False)
		
		self.stopnow = False
	
	def run(self):
		try:
			if self.stopnow == False:
				self.gui.update_statusbar("DatUpdater", _("Searching for a new DAT file..."))
			try:
				new_version_file = urlopen(self.dat_version_url)
				new_version = new_version_file.read()
							
				if int(self.dat_version) < int(new_version):
					if self.stopnow == False:
						self.gui.update_statusbar("DatUpdater", _("New DAT file available!"))
					# Deactivate all widgets
					if self.stopnow == False:
						self.gui.deactivate_widgets()
					# Download new DAT file
					datdownloader = DatDownloader(self.gui)
					datdownloader.start()
					datdownloader.join()
					if self.stopnow == False:
						self.gui.update_statusbar("DatUpdater", _("Loading the new DAT file and creating database..."))
					dat = Dat(DAT_NAME)
					if self.stopnow == False:
						self.gui.update_statusbar("DatUpdater", _("Database created."))
						self.gui.add_games()
				else:
					if self.stopnow == False:
						self.gui.update_statusbar("DatUpdater", _("DAT file is already up to date."))
			except:
				if self.stopnow == False:
					self.gui.update_statusbar("DatUpdater", _("Can't download DAT version file!"))
				raise
		finally:
			# reactivate widgets
			if self.stopnow == False:
				self.gui.activate_widgets()
		
	def stop(self):
		self.stopnow = True

class DatDownloader(threading.Thread):
	""" Download and unzip DAT file """
	def __init__(self, gui):
		threading.Thread.__init__(self, name="DatDownloader")
		self.dat_url = DAT_URL
		self.dat_name_zip = DAT_NAME_ZIP
		self.dat_name = DAT_NAME
		self.gui = gui
		self.stopnow = False
	
	def run(self):
		if self.stopnow == False:
			self.gui.update_statusbar("DatDownloader", _("Downloading a new DAT file..."))
		try:
			input = urlopen(self.dat_url)
			output = open(self.dat_name_zip, "wb")
			for data in input:
				output.write(data)
			output.close()
		except:
			if self.stopnow == False:
				self.gui.update_statusbar("DatDownloader", _("Can't download DAT!"))
			raise
		
		if self.stopnow == False:
			self.gui.update_statusbar("FirstRun", _("Unzipping the new DAT file..."))
		zip = ZipFile(self.dat_name_zip, "r")
		file(self.dat_name, "wb").write(zip.read(self.dat_name))
		zip.close()
		os.remove(self.dat_name_zip)
	
	def stop(self):
		self.stopnow = True 

class ImagesDownloader(threading.Thread):
	""" Download 'game' images and show them (if possible).
	Take care of local path's creation when needed """
	def __init__(self, gui, game):
		threading.Thread.__init__(self,  name="ImagesDownloader")

		self.release_number = game[GAME_RELEASE_NUMBER]
		self.filename1 = game[GAME_IMG1_LOCAL_PATH]
		self.url1 = game[GAME_IMG1_REMOTE_URL]
		self.filename2 = game[GAME_IMG2_LOCAL_PATH]
		self.url2 = game[GAME_IMG2_REMOTE_URL]
		range_dir = os.path.join(IMG_DIR, game[GAME_RANGE_DIR])
		
		self.gui = gui
		self.stopnow = False
		
		if not os.path.exists(range_dir):
			os.mkdir(range_dir)
	
	def run(self):
		if not os.path.exists(self.filename1):
			try:
				input = urlopen(self.url1)
				output = open(self.filename1, "wb")
				for data in input:
					output.write(data)
				output.close()
			except HTTPError:
				if self.stopnow == False:
					self.gui.update_statusbar("ImageDownloader",
									_("Error while downloading image 1 for '%s': File not found.") % str(game))
			else:
				if self.stopnow == False:
					self.gui.update_image(self.release_number, 1, self.filename1)
		
		if not os.path.exists(self.filename2):
			try:
				input = urlopen(self.url2)
				output = open(self.filename2, "wb")
				for data in input:
					output.write(data)
				output.close()
			except HTTPError:
				if self.stopnow == False:
					self.gui.update_statusbar("ImageDownloader",
									_("Error while downloading image 2 for '%s': File not found.") % str(game))
			else:
				if self.stopnow == False:
					self.gui.update_image(self.release_number, 2, self.filename2)
			
	def stop(self):
		self.stopnow = True
		
class AllImagesDownloader(threading.Thread):
	""" Update the gui button and download all missing images """
	def __init__(self, gui, games):
		threading.Thread.__init__(self, name="AllImagesDownloader")
		self.games = games
		self.gui = gui
		self.stopnow = False
	
	def run(self):
		self.gui.toggle_all_images_download_toolbutton()
		if self.stopnow == False:
			self.gui.update_statusbar("AllImagesDownloader", _("Downloading all images..."))

		for game in self.games:
			if self.stopnow == True:
				if self.gui.is_alive():
					self.gui.update_statusbar("AllImagesDownloader", _("Download of all images stopped."))
					self.gui.toggle_all_images_download_toolbutton()
				break
			
			range_dir = os.path.join(IMG_DIR, game[GAME_RANGE_DIR])
			img1 = game[GAME_IMG1_LOCAL_PATH]
			img2 = game[GAME_IMG2_LOCAL_PATH]
			url1 = game[GAME_IMG1_REMOTE_URL]
			url2 = game[GAME_IMG2_REMOTE_URL]
						
			if not os.path.exists(range_dir):
				os.mkdir(range_dir)
			
			# check images CRC (disabled for now)
#			if os.path.exists(img1):
#				if game.get_img1_crc() != get_crc32(img1):
#					os.remove(img1)
#			
#			if os.path.exists(img2):
#				if game.get_img2_crc() != get_crc32(img2):
#					os.remove(img2)
#				

			if not os.path.exists(img1) or not os.path.exists(img2):
				if self.stopnow == False:
					self.gui.update_statusbar("AllImagesDownloader", _("Downloading images for '%s'...") % game[GAME_FULLINFO])
			
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
		
		if self.stopnow == False:
			self.gui.update_statusbar("AllImagesDownloader", _("Download of all images completed."))
			# restore original button
			self.gui.toggle_all_images_download_toolbutton()
				
	def stop(self):
		""" Stop the thread """
		self.stopnow = True
