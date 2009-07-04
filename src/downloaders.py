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

import gettext
_ = gettext.gettext

from urllib2 import urlopen, HTTPError
from zipfile import ZipFile

from globals import *
from db import *
from files import *

class DatDownloader(threading.Thread):
	""" Download and unzip DAT file """
	def __init__(self, gui):
		""" Prepare thread """
		threading.Thread.__init__(self, name = "DatDownloader")
		self.dat_url = DAT_URL
		self.dat_name_zip = DAT_NAME_ZIP
		self.dat_name = DAT_NAME
		self.gui = gui
	
	def run(self):
		""" Start thread """
		self.gui.update_statusbar("DatDownloader", _("Downloading the new DAT file..."), True)
		try:
			input = urlopen(self.dat_url)
			output = open(self.dat_name_zip, "wb")
			for data in input:
				output.write(data)
			output.close()
		except:
			self.gui.update_statusbar("DatDownloader", _("Can't download DAT!"), True)
			return
				
		self.gui.update_statusbar("FirstRun", _("Unzipping the new DAT file..."), True)
		zip = ZipFile(self.dat_name_zip, "r")
		zip.extractall()
		zip.close()
		os.remove(self.dat_name_zip)
	
	def stop(self):
		""" Stop thread """
		return 

class ImagesDownloader(threading.Thread):
	"""
	Download 'game' images and show them (if possible).
	Take care of local path's creation when needed.
	"""
	def __init__(self, gui, game):
		""" Prepare thread """
		threading.Thread.__init__(self, name = "ImagesDownloader")
		self.fullinfo = game[GAME_FULLINFO]
		self.release_number = game[GAME_RELEASE_NUMBER]
		self.filename1 = game[GAME_IMG1_LOCAL_PATH]
		self.url1 = game[GAME_IMG1_REMOTE_URL]
		self.filename2 = game[GAME_IMG2_LOCAL_PATH]
		self.url2 = game[GAME_IMG2_REMOTE_URL]
		self.range_dir = os.path.join(config.get_option("images_path"), game[GAME_RANGE_DIR])
		self.gui = gui
	
	def run(self):
		""" Start thread """		
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
								_("Error while downloading image 1 for '%s': File not found.") % self.fullinfo, True)
			else:
				self.gui.update_image(self.release_number, 1, self.filename1, True)
		
		if not os.path.exists(self.filename2):
			try:
				input = urlopen(self.url2)
				output = open(self.filename2, "wb")
				for data in input:
					output.write(data)
				output.close()
			except HTTPError:
				self.gui.update_statusbar("ImageDownloader",
								_("Error while downloading image 2 for '%s': File not found.") % self.fullinfo, True)
			else:
				self.gui.update_image(self.release_number, 2, self.filename2, True)
			
	def stop(self):
		""" Stop thread """
		return
		
class AllImagesDownloader(threading.Thread):
	""" Download all missing images """
	def __init__(self, gui, games):
		""" Prepare thread """
		threading.Thread.__init__(self, name = "AllImagesDownloader")
		self.games = games
		self.gui = gui
		self.check_images_crc = config.get_option("check_images_crc")
		self.check_images_notified = False
		self.stopnow = False
	
	def run(self):
		""" Start thread """
		self.gui.toggle_images_download_toolbutton(True)
		self.gui.update_statusbar("AllImagesDownloader", _("Downloading all images..."), True)

		for game in self.games:
			if self.stopnow:
				break
			
			range_dir = os.path.join(config.get_option("images_path"), game[GAME_RANGE_DIR])
			img1 = game[GAME_IMG1_LOCAL_PATH]
			img2 = game[GAME_IMG2_LOCAL_PATH]
			url1 = game[GAME_IMG1_REMOTE_URL]
			url2 = game[GAME_IMG2_REMOTE_URL]
						
			if not os.path.exists(range_dir):
				os.mkdir(range_dir)
			
			# check images CRC
			if self.check_images_crc:
				if not self.check_images_notified:
				    self.gui.update_statusbar("AllImagesDownloader", _("Checking images integrity..."), True)
				    self.check_images_notified = True
				if os.path.exists(img1) and game[GAME_IMG1_CRC] != get_crc32(img1):
					os.remove(img1)
				if os.path.exists(img2) and game[GAME_IMG2_CRC] != get_crc32(img2):
					os.remove(img2)

			if not os.path.exists(img1) or not os.path.exists(img2):
				self.gui.update_statusbar("AllImagesDownloader", _("Downloading images for '%s'...") % game[GAME_FULLINFO], True)
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
		
		if self.stopnow:
			self.gui.update_statusbar("AllImagesDownloader", _("Download of all images stopped."), True)
		else:
			self.gui.update_statusbar("AllImagesDownloader", _("Download of all images completed."), True)
		# restore original button
		self.gui.toggle_images_download_toolbutton(True)
				
	def stop(self):
		""" Stop thread """
		self.stopnow = True
