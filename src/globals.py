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

DATA_DIR = os.path.join(os.getcwd(), "data")
LOCALE_DIR = "/usr/share/locale/"
DATA_IMG_DIR = os.path.join(DATA_DIR, "images")

APP_NAME = "DsRomsManager"
APP_VERSION = "0.3"

# gettext
import locale, gettext
_ = gettext.gettext

WORK_DIR = os.path.expanduser("~") + "/." + APP_NAME.lower()
IMG_DIR = os.path.join(WORK_DIR, "images")
DB_FILE = os.path.join(WORK_DIR, "db")
DB_VERSION = "2"
CFG_FILE = os.path.join(WORK_DIR, "config")

DEFAULT_REVIEW_URL="http://www.google.com/search?hl=en&q={FOOBAR} DS review site:metacritic.com&btnI=I'm+Feeling+Lucky"

DEFAULT_CFG_FILE="""[DEFAULT]
show_found_games_only = False
review_url = """ + DEFAULT_REVIEW_URL

DAT_URL = "http://www.advanscene.com/offline/datas/ADVANsCEne_NDS_S.zip"
DAT_NAME_ZIP = "ADVANsCEne_NDS_S.zip"
DAT_NAME = "ADVANsCEne_NDS_S.xml"

sizes = ["64 MBits", "128 MBits", "256 MBits", "512 MBits", "1024 MBits", "2048 MBits"]

NO = 0
YES = 1

langs = {
		0 : _("French"),
		1 : _("English"),
		2 : _("Unknown"),
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
		14 : _("Unknown"),
		15 : _("Unknown"),
		16 : _("Korean")
		}

countries = {
			0 : _("Europe"),
			1 : _("USA"),
			2 : _("Germany"),
			4 : _("Spain"),
			5 : _("France"),
			6 : _("Italy"),
			7 : _("Japan"),
			8 : _("Netherlands"),
			19 : _("Australia"),
			22 : _("South Korea")
			}

countries_short = {
			0 : "EU",
			1 : "US",
			2 : "DE",
			4 : "SP",
			5 : "FR",
			6 : "IT",
			7 : "JP",
			8 : "NL",
			19 : "AU",
			22 : "KS"
			}