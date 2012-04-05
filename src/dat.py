#!/usr/bin/env python2
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
		info = []
		info.append(DB_VERSION)
		info.append(dat.getElementsByTagName("datName")[0].firstChild.data)
		info.append(dat.getElementsByTagName("imFolder")[0].firstChild.data)
		info.append(dat.getElementsByTagName("datVersion")[0].firstChild.data)
		info.append(dat.getElementsByTagName("system")[0].firstChild.data)
		info.append(dat.getElementsByTagName("screenshotsWidth")[0].firstChild.data)
		info.append(dat.getElementsByTagName("screenshotsHeight")[0].firstChild.data)
		info.append(dat.getElementsByTagName("datVersionURL")[0].firstChild.data)
		info.append(dat.getElementsByTagName("datURL")[0].firstChild.data)
		# we need to save img_url info because we need them when adding games info
		img_url = dat.getElementsByTagName("imURL")[0].firstChild.data
		info.append(img_url)
		db.add_info(info)
		# Read games and insert them into database
		for game in dat.getElementsByTagName("game"):
			g = Game(game)
			info = []
			info.append(g.get_image_number())
			info.append(g.get_release_number())
			info.append(g.get_release_number_text())
			info.append(g.get_title())
			info.append(g.get_fullinfo())
			info.append(g.get_filename())
			info.append(g.get_save_type())
			info.append(g.get_rom_size())
			info.append(g.get_publisher())
			info.append(g.get_location_index())
			info.append(g.get_location())
			info.append(g.get_location_short())
			info.append(g.get_source_rom())
			info.append(g.get_language())
			info.append(g.get_rom_crc())
			info.append(g.get_img_range())
			info.append(g.get_img1_crc())
			info.append(g.get_img1_local(config.get_option("images_path")))
			info.append(g.get_img1_url(img_url))
			info.append(g.get_img2_crc())
			info.append(g.get_img2_local(config.get_option("images_path")))
			info.append(g.get_img2_url(img_url))
			info.append(g.get_comment())
			info.append(g.get_duplicate_id())
			db.add_game(info)
		# Close the DAT file
		dat.unlink()
		# Save the newly create database on disk
		db.save_as(DB_FILE)
		# Close connection
		del db
