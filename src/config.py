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
DEFAULT_REVIEW_URL = "http://www.google.com/search?hl=en&q={FOOBAR} DS review site:metacritic.com&btnI=I'm+Feeling+Lucky"
DEFAULT_ROMS_PATH = ROMS_DIR
DEFAULT_UNKNOWN_ROMS_PATH = UNKNOWN_ROMS_DIR
DEFAULT_NEW_ROMS_PATH = DEFAULT_ROMS_PATH
DEFAULT_SHOW_AVAILABLE_GAMES = True
DEFAULT_SHOW_NOT_AVAILABLE_GAMES = True
DEFAULT_SHOW_FIXABLE_GAMES = True

DEFAULT_CFG_FILE = "[" + DEFAULT_CFG_SECTION + "]"
DEFAULT_CFG_FILE += "\ncheck_images_crc = " + str(DEFAULT_CHECK_IMAGES_CRC)
DEFAULT_CFG_FILE += "\nreview_url = " + DEFAULT_REVIEW_URL
DEFAULT_CFG_FILE += "\nroms_path = " + DEFAULT_ROMS_PATH
DEFAULT_CFG_FILE += "\nunknown_roms_path = " + DEFAULT_UNKNOWN_ROMS_PATH
DEFAULT_CFG_FILE += "\nnew_roms_path = " + DEFAULT_NEW_ROMS_PATH
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
        if option == "roms_path":
            return self.roms_path
        if option == "unknown_roms_path":
            return self.unknown_roms_path
        if option == "new_roms_path":
            return self.new_roms_path
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
        if option == "roms_path":
            return DEFAULT_ROMS_PATH
        if option == "unknown_roms_path":
            return DEFAULT_UNKNOWN_ROMS_PATH
        if option == "new_roms_path":
            return DEFAULT_NEW_ROMS_PATH
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
        elif option == "roms_path":
            self.roms_path = value
        elif option == "unknown_roms_path":
            self.unknown_roms_path = value
        elif option == "new_roms_path":
            self.new_roms_path = value
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
        elif option == "roms_path":
            self.roms_path = DEFAULT_ROMS_PATH
        elif option == "unknown_roms_path":
            self.unknown_roms_path = DEFAULT_UNKNOWN_ROMS_PATH
        elif option == "new_roms_path":
            self.roms_path = DEFAULT_NEW_ROMS_PATH
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
        config.set(DEFAULT_CFG_SECTION, "new_roms_path", self.new_roms_path)
        config.set(DEFAULT_CFG_SECTION, "unknown_roms_path", self.unknown_roms_path)
        config.set(DEFAULT_CFG_SECTION, "roms_path", self.roms_path)
        config.set(DEFAULT_CFG_SECTION, "review_url", self.review_url)
        config.set(DEFAULT_CFG_SECTION, "check_images_crc", str(self.check_images_crc))
        cfg = open(CFG_FILE, "w")
        config.write(cfg)
        cfg.flush()
