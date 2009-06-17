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

try:
	import sqlite3
except:
	print "This application requires at least Python 2.5 to run."
	from sys import exit
	exit(1)

from globals import *

class DB():
	def __init__(self):
		self.connection = sqlite3.connect(":memory:")
		self.cursor = self.connection.cursor()
		
		self.games = 0
		
		# Create table
		self.cursor.execute("""CREATE TABLE games (
		image_number TEXT,
		release_number INT,
		title TEXT,
		fullinfo TEXT,
		save_type TEXT,
		rom_size INT,
		publisher TEXT,
		location TEXT,
		location_short TEXT,
		source_rom TEXT,
		language TEXT,
		rom_crc TEXT,
		img1_crc TEXT,
		img2_crc TEXT,
		comment TEXT,
		duplicate_id INT
		)""")
	
	def add(self, game):
		"""	Add 'game' to database """		
		infos = []
		infos.append(game.get_image_number())
		infos.append(game.get_release_number())
		infos.append(game.get_title())
		infos.append(str(game))
		infos.append(game.get_save_type())
		infos.append(game.get_rom_size())
		infos.append(game.get_publisher())
		infos.append(game.get_location())
		infos.append(game.get_location_short())
		infos.append(game.get_source_rom())
		infos.append(game.get_language())
		infos.append(game.get_rom_crc())
		infos.append(game.get_img1_crc())
		infos.append(game.get_img2_crc())
		infos.append(game.get_comment())
		infos.append(game.get_duplicate_id())
		
		self.cursor.execute("INSERT INTO games VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", tuple(infos))
		self.connection.commit()
		self.games += 1
	
	def adds(self, games):
		""" Add 'games' (a list of games) to database """
		for game in games:
			self.add(game)
	
	def get_all(self):
		""" Return all games """
		self.cursor.execute("SELECT * FROM games")
		return self.cursor.fetchall()
			
	def filter_by(self, string, location, language, size):
		""" Return games filtered by location, language and size infos """
		command = "SELECT * FROM games WHERE"
		if string != "":
			for s in string.split():
				command += " fullinfo LIKE '%" + s + "%' AND"
		if location != "All":
			command += " location = '" + location + "' AND"
		if language != "All":
			command += " language LIKE '%" + language + "%' AND"
		if size != "All":
			command += " rom_size = '" + str(int(size.split()[0])/8*1048576) + "'"
		if command[len(command)-3:] == "AND":
			command = command[:len(command)-4]
		if command[len(command)-5:] == "WHERE":
			command = command[:len(command)-6]
		self.cursor.execute(command)
		return self.cursor.fetchall()
	
#	def get_by_str(self, string):
#		""" Return games infos matching string in fullinfo """
#		self.cursor.execute("SELECT * FROM games WHERE fullinfo LIKE ?", ("%" + string + "%", ))
#		return self.cursor.fetchall()
#	
#	def get_gamesnumber(self):
#		""" Return games number """
#		return self.games
