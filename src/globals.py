#!/usr/bin/env python2
#
# DRM - DsRomsManager
#
# Copyright (C) 2008-2009 by
# Fortunato Ventre - <vorione@gmail.com> - <http://www.voria.org>
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

DATA_DIR = os.path.join(os.getcwd(), "data")
LOCALE_DIR = "/usr/share/locale/"
DATA_IMG_DIR = os.path.join(DATA_DIR, "images")

APP_NAME = "DsRomsManager"
APP_VERSION = "1.7"

import gettext
_ = gettext.gettext

WORK_DIR = os.path.expanduser("~") + "/." + APP_NAME.lower()
if not os.path.exists(WORK_DIR):
    os.mkdir(WORK_DIR)
IMG_DIR = os.path.join(WORK_DIR, "images")
if not os.path.exists(IMG_DIR):
    os.mkdir(IMG_DIR)
ROMS_DIR = os.path.join(WORK_DIR, "roms")
if not os.path.exists(ROMS_DIR):
    os.mkdir(ROMS_DIR)
UNKNOWN_ROMS_DIR = os.path.join(ROMS_DIR, "unknown")
if not os.path.exists(UNKNOWN_ROMS_DIR):
    os.mkdir(UNKNOWN_ROMS_DIR)
DB_FILE = os.path.join(WORK_DIR, "db")
DB_VERSION = "6"

from config import Config
config = Config()

DAT_URL = "http://www.advanscene.com/offline/datas/ADVANsCEne_NDS_S.zip"
DAT_NAME_ZIP = "ADVANsCEne_NDS_S.zip"
DAT_NAME = "ADVANsCEne_NDS_S.xml"

sizes = ["64 MBits", "128 MBits", "256 MBits", "512 MBits", "1024 MBits", "2048 MBits", "4096 MBits"]

CHECKS_ERROR = -1
CHECKS_NO = 0
CHECKS_YES = 1
CHECKS_CONVERT = 2

langs = {
        -1 : _("Unknown"),
        0 : _("French"),
        1 : _("English"),
        2 : _("Chinese"),
        3 : _("Danish"),
        4 : _("Dutch"),
        5 : _("Finnish"),
        6 : _("German"),
        7 : _("Italian"),
        8 : _("Japanese"),
        9 : _("Norwegian"),
        10 : _("Polish"),
        11 : _("Portuguese"),
        12 : _("Spanish"),
        13 : _("Swedish"),
        # 14 : _("English (US)"),
        # 15 : _("Portuguese (BR)"),
        16 : _("Korean"),
        17 : _("Russian"),
        18 : _("Greek"),
        19 : _("Turkish"),
        20 : _("Czech"),
        21 : _("Hungarian")
        }

countries = {
        0 : _("Europe"),
        1 : _("USA"),
        2 : _("Germany"),
        3 : _("China"),
        4 : _("Spain"),
        5 : _("France"),
        6 : _("Italy"),
        7 : _("Japan"),
        8 : _("Netherlands"),
        9 : _("United Kingdom"),
        10 : _("Denmark"),
        11 : _("Finland"),
        12 : _("Norway"),
        13 : _("Poland"),
        14 : _("Portugal"),
        15 : _("Sweden"),
        # 16 : _("USA & Europe"),
        # 17 : _("Japan & USA & Europe"),
        # 18 : _("Japan & USA"),
        19 : _("Australia"),
        20 : _("North Korea"),
        21 : _("Brazil"),
        22 : _("South Korea"),
        # 23 : _("Europe & Brazil"),
        # 24 : _("Europe & USA & Brazil"),
        # 25 : _("USA & Brazil"),
        26 : _("Russia"),
        # 27 : _("Russia"),
        28 : _("Greece"),
        29 : _("Turkey"),
        30 : _("Czech Republic"),
        31 : _("Hungary")
        }

countries_short = {
        0 : "EU",
        1 : "US",
        2 : "DE",
        3 : "CN",
        4 : "ES",
        5 : "FR",
        6 : "IT",
        7 : "JP",
        8 : "NL",
        9 : "UK",
        10 : "DK",
        11 : "FI",
        12 : "NO",
        13 : "PL",
        14 : "PT",
        15 : "SE",
        # 16 : "US-EU",
        # 17 : "JP-US-EU",
        # 18 : "JP-US",
        19 : "AU",
        20 : "KP",
        21 : "BR",
        22 : "KS",
        # 23 : "EU-BR",
        # 24 : "EU-US-BR",
        # 25 : "US-BR",
        26 : "RU",
        27 : "RU",
        28 : "GR",
        29 : "TR",
        30 : "CZ",
        31 : "HU"
        }
