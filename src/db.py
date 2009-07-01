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
	print "This application requires at least Python 2.6 to run."
	import sys
	sys.exit(1)

import os

CREATE_GAMES_TABLE_QUERY="""CREATE TABLE IF NOT EXISTS games (
							image_number TEXT,
							release_number INT,
							title TEXT,
							fullinfo TEXT,
							save_type TEXT,
							rom_size INT,
							publisher TEXT,
							location_index INT,
							location TEXT,
							location_short TEXT,
							source_rom TEXT,
							language TEXT,
							rom_crc TEXT,
							range_dir TEXT,
							img1_crc TEXT,
							img1_local_path TEXT,
							img1_remote_url TEXT,
							img2_crc TEXT,
							img2_local_url TEXT,
							img2_remote_url TEXT,
							comment TEXT,
							duplicate_id INT
							)"""

# db_game_table info indexes
GAME_IMAGE_NUMBER = 0
GAME_RELEASE_NUMBER = 1
GAME_TITLE = 2
GAME_FULLINFO = 3
GAME_SAVE_TYPE = 4
GAME_ROM_SIZE = 5
GAME_PUBLISHER = 6
GAME_LOCATION_INDEX = 7
GAME_LOCATION = 8
GAME_LOCATION_SHORT = 9
GAME_SOURCE_ROM = 10
GAME_LANGUAGE = 11
GAME_ROM_CRC = 12
GAME_RANGE_DIR = 13
GAME_IMG1_CRC = 14
GAME_IMG1_LOCAL_PATH = 15
GAME_IMG1_REMOTE_URL = 16
GAME_IMG2_CRC = 17
GAME_IMG2_LOCAL_PATH = 18
GAME_IMG2_REMOTE_URL = 19
GAME_COMMENT = 20
GAME_DUPLICATE_ID = 21

CREATE_INFO_TABLE_QUERY="""CREATE TABLE IF NOT EXISTS info (
							db_version TEXT,
							dat_name TEXT,
							img_dir TEXT,
							dat_version INT,
							system TEXT,
							screenshots_width INT,
							screenshots_height INT,
							dat_version_url TEXT,
							dat_url TEXT,
							img_url TEXT
							)"""

INFO_DB_VERSION = 0
INFO_DAT_NAME = 1
INFO_IMG_DIR = 2
INFO_DAT_VERSION = 3
INFO_SYSTEM = 4
INFO_SCREENSHOTS_WIDTH = 5
INFO_SCREENSHOTS_HEIGHT = 6
INFO_DAT_VERSION_URL = 7
INFO_DAT_URL = 8
INFO_IMG_URL = 9

INSERT_GAME_QUERY="INSERT INTO games VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
INSERT_INFO_QUERY="INSERT INTO info VALUES (?,?,?,?,?,?,?,?,?,?)"

class DB():
	def __init__(self, filename=":memory:"):
		self.connection = sqlite3.connect(filename)
		self.cursor = self.connection.cursor()
		
		# Create 'games' table
		self.cursor.execute(CREATE_GAMES_TABLE_QUERY)
		
		# Create 'datinfo' table
		self.cursor.execute(CREATE_INFO_TABLE_QUERY)
		
		# Count games in database
		self.cursor.execute("SELECT * FROM games")
		self.games = len(self.cursor.fetchall())
		
	def add_game(self, game_info):
		"""	Add 'game_info' to database """		
		self.cursor.execute(INSERT_GAME_QUERY, tuple(game_info))
		self.connection.commit()
		self.games += 1
	
	def add_info(self, info):
		""" Add 'info' to database """
		self.cursor.execute(INSERT_INFO_QUERY, tuple(info))
		self.connection.commit()
	
	def get_info(self):
		""" Return info """
		self.cursor.execute("SELECT * FROM info")
		return self.cursor.fetchone()
	
	def get_all_games(self):
		""" Return all games """
		self.cursor.execute("SELECT * FROM games")
		return self.cursor.fetchall()
	
	def get_all_games_crc(self):
		""" Return all games crc """
		self.cursor.execute("SELECT rom_crc FROM games")
		return self.cursor.fetchall()
	
	def get_game(self, release_number):
		""" Return info for game number 'release_number' """
		self.cursor.execute("SELECT * FROM games WHERE release_number = " + str(release_number))
		return self.cursor.fetchone()
	
	def get_game_crc(self, release_number):
		""" Return crc for game number 'release_number' """
		self.cursor.execute("SELECT rom_crc FROM games WHERE release_number = " + str(release_number))
		return self.cursor.fetchone()
		
	def get_games_number(self):
		""" Return the number of games in database """
		return self.games
			
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

	def save_as(self, filename):
		""" Save database in memory on disk as 'filename' """
		if os.path.exists(filename):
			os.remove(filename)
		
		self.cursor.execute("ATTACH '%s' AS extern" % filename)
		
		# Create tables on external file
		self.cursor.execute(CREATE_GAMES_TABLE_QUERY.replace("games", "extern.games", 1))
		self.cursor.execute(CREATE_INFO_TABLE_QUERY.replace("info", "extern.info", 1))
		
		# Copy data from memory database to extern database
		self.cursor.execute("SELECT * FROM games")
		for game in self.cursor.fetchall():
			self.cursor.execute(INSERT_GAME_QUERY.replace("games", "extern.games", 1), game)
		self.cursor.execute("SELECT * FROM info")
		self.cursor.execute(INSERT_INFO_QUERY.replace("info", "extern.info", 1), self.cursor.fetchone())
		
		self.connection.commit()
		