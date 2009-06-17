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

import gtk

from urllib2 import urlopen, HTTPError
from zipfile import ZipFile

import struct
import binascii

from globals import *
from dat import Dat

def get_crc32(filename):
	""" Return CRC32 of 'filename' """
	bin = struct.pack('>l', binascii.crc32(file(filename, 'r').read()))
	return binascii.hexlify(bin).upper()

def get_crc32_zip(zipfile):
	""" Return CRC32 of .nds file contained in 'zipfile'.
	Return None if no .nds file is found """
	result = None
	zip = zipfile.ZipFile(zipfile, "r")
	for info in zip.infolist():
		if info.filename[len(info.filename)-4:].lower() == ".nds":
			crc = struct.pack('>l', info.CRC)
			result = binascii.hexlify(crc).upper()
			break
	zip.close()
	return result

class DatUpdater(threading.Thread):
	""" Update DAT file if needed """
	def __init__(self, gui, dat_version, dat_version_url):
		threading.Thread.__init__(self, name="DatUpdater")
		self.dat_version = dat_version
		self.dat_version_url = dat_version_url
		self.gui = gui
	
	def run(self):
		self.gui.update_statusbar("DatUpdater", "Searching for a new DAT file...")
		try:
			new_version_file = urlopen(self.dat_version_url)
			new_version = new_version_file.read()
			
			if self.dat_version < new_version:
				self.gui.update_statusbar("DatUpdater", "New DAT file available!")
				datdownloader = DatDownloader(self.gui)
				datdownloader.start()
				datdownloader.join()
				self.gui.update_statusbar("DatUpdater", "Loading the new DAT file...")
				dat = Dat(DAT_NAME)
				self.gui.add(dat)
				self.gui.update_statusbar("DatUpdater", "New DAT file loaded")
			else:
				self.gui.update_statusbar("DatUpdater", "DAT file is already up to date")
				pass		
		except:
			self.gui.update_statusbar("DatUpdater", "Can't download DAT version file!")
			raise
		
	def stop(self):
		pass

class DatDownloader(threading.Thread):
	""" Download and unzip DAT file """
	def __init__(self, gui):
		threading.Thread.__init__(self, name="DatDownloader")
		self.dat_url = DAT_URL
		self.dat_name_zip = DAT_NAME_ZIP
		self.dat_name = DAT_NAME
		self.gui = gui
	
	def run(self):
		self.gui.update_statusbar("DatDownloader", "Downloading a new DAT file...")
		try:
			input = urlopen(self.dat_url)
			output = open(self.dat_name_zip, "wb")
			for data in input:
				output.write(data)
			output.close()
		except:
			self.gui.update_statusbar("DatDownloader", "Can't download DAT!")
			raise
		
		self.gui.update_statusbar("FirstRun", "Unzipping the new DAT file...")
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
		threading.Thread.__init__(self)

		self.game = game
		self.url1 = game.get_img1_url()
		self.filename1 = os.path.join(IMG_DIR, game.get_img1_local())
		range_dir = os.path.join(IMG_DIR, game.get_img_range())
		self.url2 = game.get_img2_url()
		self.filename2 = os.path.join(IMG_DIR, game.get_img2_local())
				
		if not os.path.exists(range_dir):
			os.mkdir(range_dir)
		
		self.gui = gui
	
	def run(self):
		if not os.path.exists(self.filename1):
			try:
				input = urlopen(self.url1)
				output = open(self.filename1, "wb")
				for data in input:
					output.write(data)
				output.close()
			except HTTPError:
				file = self.filename1.split(os.sep)[len(self.filename1.split(os.sep))-1]
				self.gui.update_statusbar("ImageDownloader",
					"Error while downloading image '" + file + "' for '" + str(game) + "': File not found")
			else:
				self.gui.update_image(self.game.get_release_number(), 1, self.filename1)
		
		if not os.path.exists(self.filename2):
			try:
				input = urlopen(self.url2)
				output = open(self.filename2, "wb")
				for data in input:
					output.write(data)
				output.close()
			except HTTPError:
				file = self.filename2.split(os.sep)[len(self.filename2.split(os.sep))-1]
				self.gui.update_statusbar("ImageDownloader",
				    "Error while downloading image '" + file + "' for '" + str(game) + "': File not found")
			else:
				self.gui.update_image(self.game.get_release_number(), 2, self.filename2)
			
	def stop(self):
		return
		
class AllImagesDownloader(threading.Thread):
	""" Update the gui button and download all missing images """
	def __init__(self, gui, games):
		threading.Thread.__init__(self, name="AllImagesDownloader")
		self.games = games
		self.gui = gui
		self.stopnow = False
	
	def run(self):
		self.gui.toggle_all_images_download_toolbutton(self)
		self.gui.update_statusbar("AllImagesDownloader", "Searching for invalid images...")
		for game in self.games:
			if self.stopnow == False:
				img1 = game.get_img1_local()
				range_dir = os.path.join(IMG_DIR, img1.split(os.sep)[0])
				url1 = game.get_img1_url()
				url2 = game.get_img2_url()
				img1 = os.path.join(IMG_DIR, img1)
				img2 = os.path.join(IMG_DIR, game.get_img2_local())
				
				if not os.path.exists(range_dir):
					os.mkdir(range_dir)
				
				# check images CRC (disabled for now)
#				if os.path.exists(img1):
#					if game.get_img1_crc() != get_crc32(img1):
#						os.remove(img1)
#				
#				if os.path.exists(img2):
#					if game.get_img2_crc() != get_crc32(img2):
#						os.remove(img2)
#				
				if not os.path.exists(img1) or not os.path.exists(img2):
					self.gui.update_statusbar("AllImagesDownloader", "Downloading images for '" + str(game) + "'...")
				
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
			self.gui.update_statusbar("AllImagesDownloader", "Download of all images stopped")
		else:
			self.gui.update_statusbar("AllImagesDownloader", "Download of all images completed")
		
		# restore original button
		self.gui.toggle_all_images_download_toolbutton(self)
				
	def stop(self):
		""" Stop the thread """
		self.gui.update_statusbar("AllImagesDownloader", "Stopping images download...")
		self.stopnow = True
