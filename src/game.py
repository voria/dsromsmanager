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

# gettext
import locale, gettext
_ = gettext.gettext

from globals import *

class Game():
	""" Hold informations about a game """
	def __init__(self, infos):
				
		self.image_number = infos.getElementsByTagName("imageNumber")[0].firstChild.data
		self.release_number = int(infos.getElementsByTagName("releaseNumber")[0].firstChild.data)
		self.title = infos.getElementsByTagName("title")[0].firstChild.data
		self.save_type = infos.getElementsByTagName("saveType")[0].firstChild.data
		self.rom_size = int(infos.getElementsByTagName("romSize")[0].firstChild.data)
		self.publisher = infos.getElementsByTagName("publisher")[0].firstChild.data
		self.location = int(infos.getElementsByTagName("location")[0].firstChild.data)
		self.source_rom = infos.getElementsByTagName("sourceRom")[0].firstChild.data
		self.language = self.__dec2bin(int(infos.getElementsByTagName("language")[0].firstChild.data))
		self.language = self.language.rjust(len(langs), "0")
		self.language = self.language[::-1]
		self.rom_crc = infos.getElementsByTagName("romCRC")[0].firstChild.data.upper()
		self.im1_crc = infos.getElementsByTagName("im1CRC")[0].firstChild.data.upper()
		self.im2_crc = infos.getElementsByTagName("im2CRC")[0].firstChild.data.upper()
		try: # Comment can be empty
			self.comment = infos.getElementsByTagName("comment")[0].firstChild.data
		except:
			self.comment = "---"
		self.duplicate_id = int(infos.getElementsByTagName("duplicateID")[0].firstChild.data)
	
	def __str__(self):
		""" Return game's main informations in a printable form """
		s = str(self.release_number) + " - " + self.title + " (" + self.get_location_short() + ")"
		temp = self.get_language().split(" - ")
		if len(temp) != 1:
			s += "(M" + str(len(temp)) + ")"
		return s
		
	def __dec2bin(self, n):
		""" Convert an integer 'n' to a string
		representing its binary representation """
		s = ""
		if n == 0:
			return "0"
		while n > 0:
			s = str(n % 2) + s
			n = n >> 1
		return s
	
	def __get_range(self):
		""" Return a string with the name of the directory in which
		the image is stored, following the offlinelist convention """
		imgCoc = (int(self.image_number) - 1) / 500
		imgRangeStart = (imgCoc * 500) + 1
		imgRange = str(imgRangeStart) + "-" + str(imgRangeStart + 499)
		return imgRange
	
	def get_image_number(self):
		""" Return game's image number """
		return self.image_number
	
	def get_img_range(self):
		""" Return game's image range """
		return self.__get_range()
	
	def get_img1_local(self, path):
		""" Return absolute local path of img1 """
		return os.path.join(path, self.__get_range(), self.image_number + "a.png")
		
	def get_img2_local(self, path):
		""" Return absolute local path of img2 """
		return os.path.join(path, self.__get_range(), self.image_number + "b.png")
	
	def get_img1_url(self, url):
		""" Return remote URL of img1 """
		return os.path.join(url, self.__get_range(), self.image_number + "a.png")
						
	def get_img2_url(self, url):
		""" Return remote URL of img2 """
		return os.path.join(url, self.__get_range(), self.image_number + "b.png")
	
	def get_release_number(self):
		""" Return game's release number """
		return self.release_number
	
	def get_title(self):
		""" Return game's title """
		return self.title
	
	def get_save_type(self):
		""" Return game's save type """
		return self.save_type
	
	def get_rom_size(self):
		""" Return game's rom size """
		return self.rom_size
	
	def get_publisher(self):
		""" Return game's publisher """
		return self.publisher
	
	def get_location_index(self):
		""" Return game's location as a key of 'countries' dictionary """
		return self.location
	
	def get_location(self):
		""" Return game's location in the long form """
		return _(countries[self.location])
	
	def get_location_short(self):
		""" Return game's location in the short form """
		return countries_short[self.location]
	
	def get_source_rom(self):
		""" Return game's source rom """
		return self.source_rom
	
	def get_language(self):
		""" Return a string containing all game's languages """
		languages = ""
		for i in range(len(langs)):
			if self.language[i] == '1':
				languages += _(langs[i]) + " - "
		return languages[:len(languages)-3]
	
	def get_rom_crc(self):
		""" Return rom's crc """
		return self.rom_crc
			
	def get_img1_crc(self):
		""" Return image1 crc """
		return self.im1_crc
	
	def get_img2_crc(self):
		""" Return image2 crc """
		return self.im2_crc
		
	def get_comment(self):
		""" Return game's comment """
		return self.comment
	
	def get_duplicate_id(self):
		""" Return game's duplicate ID """
		return self.duplicate_id
	
