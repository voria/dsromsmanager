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
import shutil
import threading
import struct
import binascii
from zipfile import ZipFile

import locale, gettext
_ = gettext.gettext

from globals import *
from db import DB

def get_crc32(filename):
    """ Return CRC32 of 'filename' """
    bin = struct.pack('>l', binascii.crc32(file(filename, 'r').read()))
    return binascii.hexlify(bin).upper()

def get_crc32_zip(zipfile):
    """ Return CRC32 of .nds file contained in 'zipfile'.
    Return None if no .nds file is found """
    result = None
    zip = ZipFile(zipfile, "r")
    for info in zip.infolist():
        if info.filename[len(info.filename)-4:].lower() == ".nds":
            crc = struct.pack('>L', info.CRC)
            result = binascii.hexlify(crc)[:8].upper()
            break
    zip.close()
    return result

def get_nds_filename_from_zip(zipfile):
    """ Return the filename of .nds file contained in 'zipfile',
    or None if no .nds file is found """
    result = None
    zip = ZipFile(zipfile, "r")
    for info in zip.infolist():
        if info.filename[len(info.filename)-4:].lower() == ".nds":
            result = info.filename
            break
    zip.close()
    return result

class RomArchiveRebuild(threading.Thread):
    """ Rebuild zip archive for games listed in 'games' dictionary """
    def __init__(self, gui, games):
        threading.Thread.__init__(self, name="RomArchiveRebuild")
        self.gui = gui
        self.games = games
        self.games_to_fix = len(games)
        self.games_fixed = 0
        self.stopnow = False
    
    def run(self):
        # Deactivate all widgets
        self.gui.deactivate_widgets()
        try:
            for key in self.games.keys():
                if self.stopnow == True:
                    return
                self.games_fixed += 1
                text = " (%d/%d): " % (self.games_fixed, self.games_to_fix)  
                self.gui.update_statusbar("RomArchiveRebuild", text + _("Rebuilding archive for '%s'...") % key)
                oldzipfile = self.games[key]
                zipdir = oldzipfile.rsplit(os.sep, 1)[0]
                zipfile = os.path.join(zipdir, key + ".zip")
                ndsname = key + ".nds"
                ndsfile = os.path.join(zipdir, ndsname)
                
                zip = ZipFile(oldzipfile, "r")
                
                if len(zip.infolist()) != 1:
                    # We can't handle zip with multiple files in it for now
                    zip.close()
                    continue
                
                info = zip.infolist()[0]
                oldndsname = info.filename
                oldndsfile = os.path.join(zipdir, oldndsname)
                if oldndsname == ndsname:
                    # nds name is ok, check zip name
                    if oldzipfile == zipfile:
                        # Nothing to do
                        zip.close()
                        continue
                    else:
                        # Just rename the zip file, its content is ok
                        zip.close()
                        shutil.move(oldzipfile, zipfile)
                        continue
                
                # Extract the nds file and rename it
                zip.extract(info, zipdir)
                shutil.move(oldndsfile, ndsfile)
                # Delete old zip file
                zip.close()
                os.remove(oldzipfile)
                # Create a new zip file
                zip = ZipFile(zipfile, "w")
                zip.write(ndsfile, ndsname)
                zip.close()
                # Remove nds file
                os.remove(ndsfile)
        finally:
            self.gui.update_statusbar("RomArchiveRebuild", _("Rebuild completed."))
            # Add games to treeview
            self.gui.add_games()
                    
    def stop(self):
        """ Stop the thread """
        self.stopnow = True
