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
DATA_IMG_DIR = os.path.join(DATA_DIR, "images")

APP_NAME = "DsRomsManager"
APP_VERSION = "0.3"

WORK_DIR = os.path.expanduser("~") + "/." + APP_NAME.lower()
IMG_DIR = os.path.join(WORK_DIR, "images")

DAT_URL = "http://www.advanscene.com/offline/datas/ADVANsCEne_NDS_S.zip"
DAT_NAME_ZIP = "ADVANsCEne_NDS_S.zip"
DAT_NAME = "ADVANsCEne_NDS_S.xml"

sizes = ["64 MBits", "128 MBits", "256 MBits", "512 MBits", "1024 MBits", "2048 MBits"]

langs = {
		0 : "French",
		1 : "English",
		2 : "Unknown",
		3 : "Danish",
		4 : "Dutch",
		5 : "Finnish",
		6 : "German",
		7 : "Italian",
		8 : "Japanese",
		9 : "Norwegian",
		10 : "Polish",
		11 : "Portuguese",
		12 : "Spanish",
		13 : "Swedish",
		14 : "Unknown",
		15 : "Unknown",
		16 : "Korean"
		}

countries = {
			0 : "Europe",
			1 : "USA",
			2 : "Germany",
			4 : "Spain",
			5 : "France",
			6 : "Italy",
			7 : "Japan",
			8 : "Netherlands",
			19 : "Australia",
			22 : "South Korea"
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
