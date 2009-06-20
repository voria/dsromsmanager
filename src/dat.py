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
import xml.dom.minidom

from globals import *
from game import Game
from db import DB

class Dat():
	""" Holds all DAT info """
	def __init__(self, filename):		
		dat = xml.dom.minidom.parse(filename)
		# Create a new database
		db = DB()
		# Read DAT general infos and insert them into database
		datinfo = []
		datinfo.append(dat.getElementsByTagName("datName")[0].firstChild.data)
		datinfo.append(dat.getElementsByTagName("imFolder")[0].firstChild.data)
		datinfo.append(dat.getElementsByTagName("datVersion")[0].firstChild.data)
		datinfo.append(dat.getElementsByTagName("system")[0].firstChild.data)
		datinfo.append(dat.getElementsByTagName("screenshotsWidth")[0].firstChild.data)
		datinfo.append(dat.getElementsByTagName("screenshotsHeight")[0].firstChild.data)
		datinfo.append(dat.getElementsByTagName("datVersionURL")[0].firstChild.data)
		datinfo.append(dat.getElementsByTagName("datURL")[0].firstChild.data)
		# we need to save img_url info because we need them when adding games info
		img_url = dat.getElementsByTagName("imURL")[0].firstChild.data
		datinfo.append(img_url)
		db.add_datinfo(datinfo)
		# Read games info and insert them into database
		for game in dat.getElementsByTagName("game"):
			g = Game(game)
			infos = []
			infos.append(g.get_image_number())
			infos.append(g.get_release_number())
			infos.append(g.get_title())
			infos.append(str(g))
			infos.append(g.get_save_type())
			infos.append(g.get_rom_size())
			infos.append(g.get_publisher())
			infos.append(g.get_location_index())
			infos.append(g.get_location())
			infos.append(g.get_location_short())
			infos.append(g.get_source_rom())
			infos.append(g.get_language())
			infos.append(g.get_rom_crc())
			infos.append(g.get_img_range())
			infos.append(g.get_img1_crc())
			infos.append(g.get_img1_local(IMG_DIR))
			infos.append(g.get_img1_url(img_url))
			infos.append(g.get_img2_crc())
			infos.append(g.get_img2_local(IMG_DIR))
			infos.append(g.get_img2_url(img_url))
			infos.append(g.get_comment())
			infos.append(g.get_duplicate_id())
			db.add_game(infos)
		# Save the newly create database on disk
		db.save_as(DB_FILE)
		# Remove DAT file
		os.remove(filename)


