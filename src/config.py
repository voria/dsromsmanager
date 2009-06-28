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
DEFAULT_GAMES_ON_DISK_PATH = ROMS_DIR
DEFAULT_SHOW_GAMES_I_HAVE = True
DEFAULT_SHOW_GAMES_I_DONT_HAVE = True

DEFAULT_CFG_FILE = "[" + DEFAULT_CFG_SECTION + "]"
DEFAULT_CFG_FILE += "\ncheck_images_crc = " + str(DEFAULT_CHECK_IMAGES_CRC)
DEFAULT_CFG_FILE += "\nreview_url = " + DEFAULT_REVIEW_URL
DEFAULT_CFG_FILE += "\ngames_on_disk_path = " + DEFAULT_GAMES_ON_DISK_PATH
DEFAULT_CFG_FILE += "\nshow_games_i_have = " + str(DEFAULT_SHOW_GAMES_I_HAVE)
DEFAULT_CFG_FILE += "\nshow_games_i_dont_have = " + str(DEFAULT_SHOW_GAMES_I_DONT_HAVE)
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
            self.games_on_disk_path = self.config.get(DEFAULT_CFG_SECTION, "games_on_disk_path")
        except NoOptionError:
            self.config.set(DEFAULT_CFG_SECTION, "games_on_disk_path", DEFAULT_GAMES_ON_DISK_PATH)
            self.games_on_disk_path = DEFAULT_GAMES_ON_DISK_PATH
        try:
            self.show_games_i_have = self.config.getboolean(DEFAULT_CFG_SECTION, "show_games_i_have")
        except NoOptionError:
            self.config.set(DEFAULT_CFG_SECTION, "show_games_i_have", str(DEFAULT_SHOW_GAMES_I_HAVE))
            self.show_games_i_have = DEFAULT_SHOW_GAMES_I_HAVE
        try:
            self.show_games_i_dont_have = self.config.getboolean(DEFAULT_CFG_SECTION, "show_games_i_dont_have")
        except NoOptionError:
            self.config.set(DEFAULT_CFG_SECTION, "show_games_i_dont_have", str(DEFAULT_SHOW_GAMES_I_DONT_HAVE))
            self.show_games_i_dont_have = DEFAULT_SHOW_GAMES_I_DONT_HAVE

    def get_all_options(self):
        return self.config.options(DEFAULT_CFG_SECTION)
    
    def get_option(self, option):
        if option == "review_url":
            return self.review_url
        if option == "check_images_crc":
            return self.check_images_crc
        if option == "games_on_disk_path":
            return self.games_on_disk_path
        if option == "show_games_i_have":
            return self.show_games_i_have
        if option == "show_games_i_dont_have":
            return self.show_games_i_dont_have
        raise Exception
    
    def get_option_default(self, option):
        if option == "review_url":
            return DEFAULT_REVIEW_URL
        if option == "check_images_crc":
            return DEFAULT_CHECK_IMAGES_CRC
        if option == "games_on_disk_path":
            return DEFAULT_GAMES_ON_DISK_PATH
        if option == "show_games_i_have":
            return DEFAULT_SHOW_GAMES_I_HAVE
        if option == "show_games_i_dont_have":
            return DEFAULT_SHOW_GAMES_I_DONT_HAVE
        raise Exception
    
    def set_option(self, option, value):
        if option == "review_url":
            self.review_url = value
        elif option == "check_images_crc":
            self.check_images_crc = value
        elif option == "games_on_disk_path":
            self.games_on_disk_path = value
        elif option == "show_games_i_have":
            self.show_games_i_have = value
        elif option == "show_games_i_dont_have":
            self.show_games_i_dont_have = value
        else:
            raise Exception        
    
    def set_option_default(self, option):
        if option == "review_url":
            self.review_url = DEFAULT_REVIEW_URL
        elif option == "check_images_crc":
            self.check_images_crc = DEFAULT_CHECK_IMAGES_CRC
        elif option == "games_on_disk_path":
            self.games_on_disk_path = DEFAULT_GAMES_ON_DISK_PATH
        elif option == "show_games_i_have":
            self.show_games_i_have = DEFAULT_SHOW_GAMES_I_HAVE
        elif option == "show_games_i_dont_have":
            self.show_games_i_dont_have = DEFAULT_SHOW_GAMES_I_DONT_HAVE
        else:
            raise Exception
    
    def save(self):
        self.config.set(DEFAULT_CFG_SECTION, "show_games_i_dont_have", str(self.show_games_i_dont_have))
        self.config.set(DEFAULT_CFG_SECTION, "show_games_i_have", str(self.show_games_i_have))
        self.config.set(DEFAULT_CFG_SECTION, "games_on_disk_path", self.games_on_disk_path)
        self.config.set(DEFAULT_CFG_SECTION, "review_url", self.review_url)
        self.config.set(DEFAULT_CFG_SECTION, "check_images_crc", str(self.check_images_crc))
        cfg = open(CFG_FILE, "w")
        self.config.write(cfg)
        cfg.flush()
