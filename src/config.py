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

DEFAULT_SHOW_FOUND_GAMES_ONLY=False
DEFAULT_CHECK_IMAGES_CRC=False
DEFAULT_REVIEW_URL="http://www.google.com/search?hl=en&q={FOOBAR} DS review site:metacritic.com&btnI=I'm+Feeling+Lucky"

DEFAULT_CFG_FILE = "[DEFAULT]"
DEFAULT_CFG_FILE += "\nshow_found_games_only = " + str(DEFAULT_SHOW_FOUND_GAMES_ONLY) 
DEFAULT_CFG_FILE += "\ncheck_images_crc = " + str(DEFAULT_CHECK_IMAGES_CRC)
DEFAULT_CFG_FILE += "\nreview_url = " + DEFAULT_REVIEW_URL

class Config():
    def __init__(self):
        self.config = SafeConfigParser()
        # If config file exists, create a default one
        if not os.path.exists(CFG_FILE):
            cfg = open(CFG_FILE, "w")
            cfg.write(DEFAULT_CFG_FILE)
            cfg.flush()            

        self.config.readfp(open(CFG_FILE))
        try:
            self.show_found_games_only = self.config.getboolean("DEFAULT", "show_found_games_only")
        except:
            self.show_found_games_only = DEFAULT_SHOW_FOUND_GAMES_ONLY
        try:
            self.check_images_crc = self.config.getboolean("DEFAULT", "check_images_crc")
        except:
            self.check_images_crc = DEFAULT_CHECK_IMAGES_CRC
        try:
            self.review_url = self.config.get("DEFAULT", "review_url")
        except:
            self.review_url = DEFAULT_REVIEW_URL
    
    def get_option(self, option):
        if option == "review_url":
            return self.review_url
        if option == "show_found_games_only":
            return self.show_found_games_only
        if option == "check_images_crc":
            return self.check_images_crc
    
    def get_option_default(self, option):
        if option == "review_url":
            return DEFAULT_REVIEW_URL
        if option == "show_found_games_only":
            return DEFAULT_SHOW_FOUND_GAMES_ONLY
        if option == "check_images_crc":
            return DEFAULT_CHECK_IMAGES_CRC
    
    def set_option(self, option, value):
        if option == "review_url":
            self.review_url = value
        if option == "show_found_games_only":
            self.show_found_games_only = value
        if option == "check_images_crc":
            self.check_images_crc = value
    
    def set_option_default(self, option):
        if option == "review_url":
            self.review_url = DEFAULT_REVIEW_URL
        if option == "show_found_games_only":
            self.show_found_games_only = DEFAULT_SHOW_FOUND_GAMES_ONLY
        if option == "check_images_crc":
            self.check_images_crc = DEFAULT_CHECK_IMAGES_CRC
    
    def save(self):
        self.config.set("DEFAULT", "review_url", self.review_url)
        self.config.set("DEFAULT", "check_images_crc", str(self.check_images_crc))
        self.config.set("DEFAULT", "show_found_games_only", str(self.show_found_games_only))
        cfg = open(CFG_FILE, "w")
        self.config.write(cfg)
        cfg.flush()
