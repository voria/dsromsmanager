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

import xml.dom.minidom
from game import Game

class Dat():
	""" Holds all DAT info """
	def __init__(self, filename):		
		self.games = []
		self.dat = xml.dom.minidom.parse(filename)
		# Read DAT general infos
		self.dat_name = self.dat.getElementsByTagName("datName")[0].firstChild.data
		self.img_dir = self.dat.getElementsByTagName("imFolder")[0].firstChild.data
		self.dat_version = self.dat.getElementsByTagName("datVersion")[0].firstChild.data
		self.system = self.dat.getElementsByTagName("system")[0].firstChild.data
		self.screenshots_width = self.dat.getElementsByTagName("screenshotsWidth")[0].firstChild.data
		self.screenshots_height = self.dat.getElementsByTagName("screenshotsHeight")[0].firstChild.data
		self.dat_version_url = self.dat.getElementsByTagName("datVersionURL")[0].firstChild.data
		self.dat_url = self.dat.getElementsByTagName("datURL")[0].firstChild.data
		self.img_url = self.dat.getElementsByTagName("imURL")[0].firstChild.data
		
		for game in self.dat.getElementsByTagName("game"):
				self.games.append(Game(game, self.img_url))
	
	def get_dat_name(self):
		""" Returns DAT internal name """
		return self.dat_name
	
	def get_version(self):
		""" Returns DAT version """
		return self.dat_version
	
	def get_version_url(self):
		""" Returns DAT version URL """
		return self.dat_version_url
	
	def get_dat_url(self):
		""" Returns DAT URL """
		return self.dat_url
	
	def get_game(self, number):
		""" Returns game n. 'number'."""
		return self.games[number-1]
	
	def get_games(self):
		""" Returns games' list """
		return self.games
	
	def get_games_number(self):
		""" Returns number of games in list """
		gamesnum = 0
		for game in self.get_games():
			gamesnum += 1
		return gamesnum
	
