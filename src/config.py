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

from ConfigParser import *
from globals import *

CFG_FILE = os.path.join(WORK_DIR, "config")

DEFAULT_CFG_SECTION = "Main"

DEFAULT_CHECK_IMAGES_CRC = False
DEFAULT_AUTOSCAN_ARCHIVES_AT_START = True
DEFAULT_AUTOSCAN_ARCHIVES_AT_DATUPDATE = True
DEFAULT_TRIM_ROMS = False
DEFAULT_SHOW_TRIM_LOG = False
DEFAULT_TRIM_TEMP_PATH = "/tmp"
DEFAULT_REVIEW_URL = "http://www.google.com/search?hl=en&q={FOOBAR} DS review site:metacritic.com&btnI=I'm+Feeling+Lucky"
DEFAULT_ROMS_PATH = ROMS_DIR
DEFAULT_UNKNOWN_ROMS_PATH = UNKNOWN_ROMS_DIR
DEFAULT_NEW_ROMS_PATH = DEFAULT_ROMS_PATH
DEFAULT_IMAGES_PATH = IMG_DIR
DEFAULT_DEFAULT_EXTRACT_DIRECTORY = os.path.expandvars("$HOME")
DEFAULT_SHOW_AVAILABLE_GAMES = True
DEFAULT_SHOW_NOT_AVAILABLE_GAMES = True
DEFAULT_SHOW_FIXABLE_GAMES = True

DEFAULT_CFG_FILE = "[" + DEFAULT_CFG_SECTION + "]"
DEFAULT_CFG_FILE += "\ncheck_images_crc = " + str(DEFAULT_CHECK_IMAGES_CRC)
DEFAULT_CFG_FILE += "\nautoscan_archives_at_start = " + str(DEFAULT_AUTOSCAN_ARCHIVES_AT_START)
DEFAULT_CFG_FILE += "\nautoscan_archives_at_datupdate = " + str(DEFAULT_AUTOSCAN_ARCHIVES_AT_DATUPDATE)
DEFAULT_CFG_FILE += "\ntrim_roms = " + str(DEFAULT_TRIM_ROMS)
DEFAULT_CFG_FILE += "\nshow_trim_log = " + str(DEFAULT_SHOW_TRIM_LOG)
DEFAULT_CFG_FILE += "\ntrim_temp_path = " + DEFAULT_TRIM_TEMP_PATH
DEFAULT_CFG_FILE += "\nreview_url = " + DEFAULT_REVIEW_URL
DEFAULT_CFG_FILE += "\nroms_path = " + DEFAULT_ROMS_PATH
DEFAULT_CFG_FILE += "\nunknown_roms_path = " + DEFAULT_UNKNOWN_ROMS_PATH
DEFAULT_CFG_FILE += "\nnew_roms_path = " + DEFAULT_NEW_ROMS_PATH
DEFAULT_CFG_FILE += "\nimages_path = " + DEFAULT_IMAGES_PATH
DEFAULT_CFG_FILE += "\ndefault_extract_directory = " + DEFAULT_DEFAULT_EXTRACT_DIRECTORY
DEFAULT_CFG_FILE += "\nshow_available_games = " + str(DEFAULT_SHOW_AVAILABLE_GAMES)
DEFAULT_CFG_FILE += "\nshow_not_available_games = " + str(DEFAULT_SHOW_NOT_AVAILABLE_GAMES)
DEFAULT_CFG_FILE += "\nshow_fixable_games = " + str(DEFAULT_SHOW_FIXABLE_GAMES)
DEFAULT_CFG_FILE += "\n\n"

class Config():
    def __init__(self):
        try:
            self.config = SafeConfigParser()
            self.config.readfp(open(CFG_FILE))
            if not self.config.has_section(DEFAULT_CFG_SECTION):
                raise Exception
        except: # CFG_FILE does not exists or it doesnt have the default section, recreate it           
            cfg = open(CFG_FILE, "w")
            cfg.write(DEFAULT_CFG_FILE)
            cfg.flush()
            self.config = SafeConfigParser()
            self.config.readfp(open(CFG_FILE))

        try:
            self.check_images_crc = self.config.getboolean(DEFAULT_CFG_SECTION, "check_images_crc")
        except NoOptionError:
            self.config.set(DEFAULT_CFG_SECTION, "check_images_crc", str(DEFAULT_CHECK_IMAGES_CRC))
            self.check_images_crc = DEFAULT_CHECK_IMAGES_CRC
        try:
            self.autoscan_archives_at_start = self.config.getboolean(DEFAULT_CFG_SECTION, "autoscan_archives_at_start")
        except NoOptionError:
            self.config.set(DEFAULT_CFG_SECTION, "autoscan_archives_at_start", str(DEFAULT_AUTOSCAN_ARCHIVES_AT_START))
            self.autoscan_archives_at_start = DEFAULT_AUTOSCAN_ARCHIVES_AT_START
        try:
            self.autoscan_archives_at_datupdate = self.config.getboolean(DEFAULT_CFG_SECTION, "autoscan_archives_at_datupdate")
        except NoOptionError:
            self.config.set(DEFAULT_CFG_SECTION, "autoscan_archives_at_datupdate", str(DEFAULT_AUTOSCAN_ARCHIVES_AT_DATUPDATE))
            self.autoscan_archives_at_datupdate = DEFAULT_AUTOSCAN_ARCHIVES_AT_DATUPDATE
        try:
            self.trim_roms = self.config.getboolean(DEFAULT_CFG_SECTION, "trim_roms")
        except NoOptionError:
            self.config.set(DEFAULT_CFG_SECTION, "trim_roms", str(DEFAULT_TRIM_ROMS))
            self.trim_roms = DEFAULT_TRIM_ROMS
        try:
            self.show_trim_log = self.config.getboolean(DEFAULT_CFG_SECTION, "show_trim_log")
        except NoOptionError:
            self.config.set(DEFAULT_CFG_SECTION, "show_trim_log", str(DEFAULT_SHOW_TRIM_LOG))
            self.show_trim_log = DEFAULT_SHOW_TRIM_LOG
        try:
            self.trim_temp_path = self.config.get(DEFAULT_CFG_SECTION, "trim_temp_path")
        except NoOptionError:
            self.config.set(DEFAULT_CFG_SECTION, "trim_temp_path", DEFAULT_TRIM_TEMP_PATH)
            self.trim_temp_path = DEFAULT_TRIM_TEMP_PATH
        try:
            self.review_url = self.config.get(DEFAULT_CFG_SECTION, "review_url")
        except NoOptionError:
            self.config.set(DEFAULT_CFG_SECTION, "review_url", DEFAULT_REVIEW_URL)
            self.review_url = DEFAULT_REVIEW_URL
        try:
            self.roms_path = self.config.get(DEFAULT_CFG_SECTION, "roms_path")
        except NoOptionError:
            self.config.set(DEFAULT_CFG_SECTION, "roms_path", DEFAULT_ROMS_PATH)
            self.roms_path = DEFAULT_ROMS_PATH
        try:
            self.unknown_roms_path = self.config.get(DEFAULT_CFG_SECTION, "unknown_roms_path")
        except NoOptionError:
            self.config.set(DEFAULT_CFG_SECTION, "unknown_roms_path", DEFAULT_UNKNOWN_ROMS_PATH)
            self.unknown_roms_path = DEFAULT_UNKNOWN_ROMS_PATH
        try:
            self.new_roms_path = self.config.get(DEFAULT_CFG_SECTION, "new_roms_path")
        except NoOptionError:
            self.config.set(DEFAULT_CFG_SECTION, "new_roms_path", DEFAULT_NEW_ROMS_PATH)
            self.new_roms_path = DEFAULT_NEW_ROMS_PATH
        try:
            self.images_path = self.config.get(DEFAULT_CFG_SECTION, "images_path")
        except NoOptionError:
            self.config.set(DEFAULT_CFG_SECTION, "images_path", DEFAULT_IMAGES_PATH)
            self.images_path = DEFAULT_IMAGES_PATH
        try:
            self.default_extract_directory = self.config.get(DEFAULT_CFG_SECTION, "default_extract_directory")
        except NoOptionError:
            self.config.set(DEFAULT_CFG_SECTION, "default_extract_directory", DEFAULT_DEFAULT_EXTRACT_DIRECTORY)
            self.default_extract_directory = DEFAULT_DEFAULT_EXTRACT_DIRECTORY
        try:
            self.show_available_games = self.config.getboolean(DEFAULT_CFG_SECTION, "show_available_games")
        except NoOptionError:
            self.config.set(DEFAULT_CFG_SECTION, "show_available_games", str(DEFAULT_SHOW_AVAILABLE_GAMES))
            self.show_available_games = DEFAULT_SHOW_AVAILABLE_GAMES
        try:
            self.show_not_available_games = self.config.getboolean(DEFAULT_CFG_SECTION, "show_not_available_games")
        except NoOptionError:
            self.config.set(DEFAULT_CFG_SECTION, "show_not_available_games", str(DEFAULT_SHOW_NOT_AVAILABLE_GAMES))
            self.show_not_available_games = DEFAULT_SHOW_NOT_AVAILABLE_GAMES
        try:
            self.show_fixable_games = self.config.getboolean(DEFAULT_CFG_SECTION, "show_fixable_games")
        except NoOptionError:
            self.config.set(DEFAULT_CFG_SECTION, "show_fixable_games", str(DEFAULT_SHOW_FIXABLE_GAMES))
            self.show_fixable_games = DEFAULT_SHOW_FIXABLE_GAMES

    def get_all_options(self):
        return self.config.options(DEFAULT_CFG_SECTION)
    
    def get_option(self, option):
        if option == "review_url":
            return self.review_url
        if option == "check_images_crc":
            return self.check_images_crc
        if option == "autoscan_archives_at_start":
            return self.autoscan_archives_at_start
        if option == "autoscan_archives_at_datupdate":
            return self.autoscan_archives_at_datupdate
        if option == "trim_roms":
            return self.trim_roms
        if option == "show_trim_log":
            return self.show_trim_log
        if option == "trim_temp_path":
            return self.trim_temp_path
        if option == "roms_path":
            return self.roms_path
        if option == "unknown_roms_path":
            return self.unknown_roms_path
        if option == "new_roms_path":
            return self.new_roms_path
        if option == "images_path":
            return self.images_path
        if option == "default_extract_directory":
            return self.default_extract_directory
        if option == "show_available_games":
            return self.show_available_games
        if option == "show_not_available_games":
            return self.show_not_available_games
        if option == "show_fixable_games":
            return self.show_fixable_games
        raise Exception
    
    def get_option_default(self, option):
        if option == "review_url":
            return DEFAULT_REVIEW_URL
        if option == "check_images_crc":
            return DEFAULT_CHECK_IMAGES_CRC
        if option == "autoscan_archives_at_start":
            return DEFAULT_AUTOSCAN_ARCHIVES_AT_START
        if option == "autoscan_archives_at_datupdate":
            return DEFAULT_AUTOSCAN_ARCHIVES_AT_DATUPDATE
        if option == "trim_roms":
            return DEFAULT_TRIM_ROMS
        if option == "show_trim_log":
            return DEFAULT_SHOW_TRIM_LOG
        if option == "trim_temp_path":
            return DEFAULT_TRIM_TEMP_PATH
        if option == "roms_path":
            return DEFAULT_ROMS_PATH
        if option == "unknown_roms_path":
            return DEFAULT_UNKNOWN_ROMS_PATH
        if option == "new_roms_path":
            return DEFAULT_NEW_ROMS_PATH
        if option == "images_path":
            return DEFAULT_IMAGES_PATH
        if option == "default_extract_directory":
            return DEFAULT_DEFAULT_EXTRACT_DIRECTORY
        if option == "show_available_games":
            return DEFAULT_SHOW_AVAILABLE_GAMES
        if option == "show_not_available_games":
            return DEFAULT_SHOW_NOT_AVAILABLE_GAMES
        if option == "show_fixable_games":
            return DEFAULT_SHOW_FIXABLE_GAMES
        raise Exception
    
    def set_option(self, option, value):
        if option == "review_url":
            self.review_url = value
        elif option == "check_images_crc":
            self.check_images_crc = value
        elif option == "autoscan_archives_at_start":
            self.autoscan_archives_at_start = value
        elif option == "autoscan_archives_at_datupdate":
            self.autoscan_archives_at_datupdate = value
        elif option == "trim_roms":
            self.trim_roms = value
        elif option == "show_trim_log":
            self.show_trim_log = value
        elif option == "trim_temp_path":
            self.trim_temp_path = value
        elif option == "roms_path":
            self.roms_path = value
        elif option == "unknown_roms_path":
            self.unknown_roms_path = value
        elif option == "new_roms_path":
            self.new_roms_path = value
        elif option == "images_path":
            self.images_path = value
        elif option == "default_extract_directory":
            self.default_extract_directory = value
        elif option == "show_available_games":
            self.show_available_games = value
        elif option == "show_not_available_games":
            self.show_not_available_games = value
        elif option == "show_fixable_games":
            self.show_fixable_games = value
        else:
            raise Exception        
    
    def set_option_default(self, option):
        if option == "review_url":
            self.review_url = DEFAULT_REVIEW_URL
        elif option == "check_images_crc":
            self.check_images_crc = DEFAULT_CHECK_IMAGES_CRC
        elif option == "autoscan_archives_at_start":
            self.autoscan_archives_at_start = DEFAULT_AUTOSCAN_ARCHIVES_AT_START
        elif option == "autoscan_archives_at_datupdate":
            self.autoscan_archives_at_datupdate = DEFAULT_AUTOSCAN_ARCHIVES_AT_DATUPDATE
        elif option == "trim_roms":
            self.trim_roms = DEFAULT_TRIM_ROMS
        elif option == "show_trim_log":
            self.show_trim_log = DEFAULT_SHOW_TRIM_LOG
        elif option == "trim_temp_path":
            self.trim_temp_path = DEFAULT_TRIM_TEMP_PATH
        elif option == "roms_path":
            self.roms_path = DEFAULT_ROMS_PATH
        elif option == "unknown_roms_path":
            self.unknown_roms_path = DEFAULT_UNKNOWN_ROMS_PATH
        elif option == "new_roms_path":
            self.roms_path = DEFAULT_NEW_ROMS_PATH
        elif option == "images_path":
            self.images_path = DEFAULT_IMAGES_PATH
        elif option == "default_extract_directory":
            self.default_extract_directory = DEFAULT_DEFAULT_EXTRACT_DIRECTORY
        elif option == "show_available_games":
            self.show_available_games = DEFAULT_SHOW_AVAILABLE_GAMES
        elif option == "show_not_available_games":
            self.show_not_available_games = DEFAULT_SHOW_NOT_AVAILABLE_GAMES
        elif option == "show_fixable_games":
            self.show_fixable_games = DEFAULT_SHOW_FIXABLE_GAMES
        else:
            raise Exception
    
    def save(self):
        config = SafeConfigParser()
        config.add_section(DEFAULT_CFG_SECTION)
        config.set(DEFAULT_CFG_SECTION, "show_fixable_games", str(self.show_fixable_games))
        config.set(DEFAULT_CFG_SECTION, "show_not_available_games", str(self.show_not_available_games))
        config.set(DEFAULT_CFG_SECTION, "show_available_games", str(self.show_available_games))
        config.set(DEFAULT_CFG_SECTION, "default_extract_directory", self.default_extract_directory)
        config.set(DEFAULT_CFG_SECTION, "images_path", self.images_path)
        config.set(DEFAULT_CFG_SECTION, "new_roms_path", self.new_roms_path)
        config.set(DEFAULT_CFG_SECTION, "unknown_roms_path", self.unknown_roms_path)
        config.set(DEFAULT_CFG_SECTION, "roms_path", self.roms_path)
        config.set(DEFAULT_CFG_SECTION, "review_url", self.review_url)
        config.set(DEFAULT_CFG_SECTION, "trim_temp_path", self.trim_temp_path)
        config.set(DEFAULT_CFG_SECTION, "show_trim_log", str(self.show_trim_log))
        config.set(DEFAULT_CFG_SECTION, "trim_roms", str(self.trim_roms))
        config.set(DEFAULT_CFG_SECTION, "autoscan_archives_at_datupdate", str(self.autoscan_archives_at_datupdate))
        config.set(DEFAULT_CFG_SECTION, "autoscan_archives_at_start", str(self.autoscan_archives_at_start))
        config.set(DEFAULT_CFG_SECTION, "check_images_crc", str(self.check_images_crc))
        cfg = open(CFG_FILE, "w")
        config.write(cfg)
        cfg.flush()
