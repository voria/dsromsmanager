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
		self.statusbar = self.gui.get_statusbar()
	
	def run(self):
		self.statusbar.push(self.statusbar.get_context_id("DatUpdater"),
						"Searching for a new DAT file...")
		try:
			new_version_file = urlopen(self.dat_version_url)
			new_version = new_version_file.read()
			
			if self.dat_version < new_version:
				self.statusbar.push(self.statusbar.get_context_id("DatUpdater"),
							"New DAT file available!")
				datdownloader = DatDownloader(self.statusbar)
				datdownloader.start()
				datdownloader.join()
				self.statusbar.push(self.statusbar.get_context_id("DatUpdater"), "Loading the new DAT file...")
				dat = Dat(DAT_NAME)
				self.gui.add(dat)
				self.statusbar.push(self.statusbar.get_context_id("DatUpdater"), "New DAT file loaded")
			else:
				self.statusbar.push(self.statusbar.get_context_id("DatUpdater"),
							"DAT file is already up to date")		
		except:
			self.statusbar.push(self.statusbar.get_context_id("DatUpdater"),
							"Can't download DAT version file!")
			raise
		
	def stop(self):
		pass

class DatDownloader(threading.Thread):
	""" Download and unzip DAT file """
	def __init__(self, statusbar):
		threading.Thread.__init__(self, name="DatDownloader")
		self.dat_url = DAT_URL
		self.dat_name_zip = DAT_NAME_ZIP
		self.dat_name = DAT_NAME
		self.statusbar = statusbar
	
	def run(self):
		self.statusbar.push(self.statusbar.get_context_id("DatDownloader"),
						"Downloading a new DAT file...")
		try:
			input = urlopen(self.dat_url)
			output = open(self.dat_name_zip, "wb")
			for data in input:
				output.write(data)
			output.close()
		except:
			self.statusbar.push(self.statusbar.get_context_id("DatDownloader"), "Can't download DAT!")
			raise
		
		self.statusbar.push(self.statusbar.get_context_id("FirstRun"), "Unzipping the new DAT file...")
		zip = ZipFile(self.dat_name_zip, "r")
		file(self.dat_name, "wb").write(zip.read(self.dat_name))
		zip.close()
		os.remove(self.dat_name_zip)
	
	def stop(self):
		return

class ImagesDownloader(threading.Thread):
	""" Download 'game' images and show them (if possible).
	Take care of local path's creation when needed """
	def __init__(self, game, treeview, image1, image2, statusbar):
		threading.Thread.__init__(self)

		self.game = game
		self.url1 = game.get_img1_url()
		self.filename1 = os.path.join(IMG_DIR, game.get_img1_local())
		range_dir = os.path.join(IMG_DIR, game.get_img_range())
		self.url2 = game.get_img2_url()
		self.filename2 = os.path.join(IMG_DIR, game.get_img2_local())
				
		if not os.path.exists(range_dir):
			os.mkdir(range_dir)
		
		self.treeview = treeview
		self.image1 = image1
		self.image2 = image2
		self.statusbar = statusbar
	
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
				self.statusbar.push(self.statusbar.get_context_id("ImageDownloader"),
				"Error while downloading image '" + file + "' for '" + str(game) + "': File not found")
			else:
				selection = self.treeview.get_selection()
				model, iter = selection.get_selected()
				try:
					if model.get_value(iter, 1) == self.game.get_release_number():
						self.image1.set_from_file(self.filename1)
				except:
					pass
		
		if not os.path.exists(self.filename2):
			try:
				input = urlopen(self.url2)
				output = open(self.filename2, "wb")
				for data in input:
					output.write(data)
				output.close()
			except HTTPError:
				file = self.filename2.split(os.sep)[len(self.filename2.split(os.sep))-1]
				self.statusbar.push(self.statusbar.get_context_id("ImageDownloader"),
				"Error while downloading image '" + file + "' for '" + str(game) + "': File not found")
			else:
				selection = self.treeview.get_selection()
				model, iter = selection.get_selected()
				try:
					if model.get_value(iter, 1) == self.game.get_release_number():
						self.image2.set_from_file(self.filename2)
				except:
					pass
		
	
	def stop(self):
		return
		
class AllImagesDownloader(threading.Thread):
	""" Take control over a gui button, while downloading all missing images """
	def __init__(self, games, statusbar, button, button_signal_id):
		threading.Thread.__init__(self, name="AllImagesDownloader")
		self.games = games
		self.statusbar = statusbar
		self.button = button
		self.button_signal_id = button_signal_id
		self.stopnow = False
	
	def run(self):
		oldlabel = self.button.get_label()
		oldstockid = self.button.get_stock_id()
		self.button.set_stock_id(gtk.STOCK_CANCEL)
		self.button.set_label("Stop images download")
		self.button.handler_block(self.button_signal_id)
		sid = self.button.connect("clicked", self.on_button_clicked)
		self.statusbar.push(self.statusbar.get_context_id("AllImagesDownloader"),
								"Searching for invalid images...")
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
				
#				if os.path.exists(img1):
#					if game.get_img1_crc() != get_crc32(img1):
#						os.remove(img1)
#				
#				if os.path.exists(img2):
#					if game.get_img2_crc() != get_crc32(img2):
#						os.remove(img2)
#				
				if not os.path.exists(img1) or not os.path.exists(img2):
					self.statusbar.push(self.statusbar.get_context_id("AllImagesDownloader"),
									"Downloading images for '" + str(game) + "'...")
				
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
					
		self.button.disconnect(sid)
		self.button.set_label(oldlabel)
		self.button.set_stock_id(oldstockid)
		self.button.handler_unblock(self.button_signal_id)
		
		if self.stopnow == True:
			self.statusbar.push(self.statusbar.get_context_id("AllImagesDownloader"),
							"Download of all images stopped")
		else:
			self.statusbar.push(self.statusbar.get_context_id("AllImagesDownloader"),
							"Download of all images completed")
			
	
	def stop(self):
		""" Stop the thread """
		self.statusbar.push(self.statusbar.get_context_id("AllImagesDownloader"), "Stopping images download...")
		self.stopnow = True
	
	def on_button_clicked(self, button):
		self.stop()
