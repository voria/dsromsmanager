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
import zipfile

import locale, gettext
_ = gettext.gettext

from globals import *
from db import DB

def get_crc32(filename):
    """ Return CRC32 of 'filename' """
    bin = struct.pack('>l', binascii.crc32(file(filename, 'r').read()))
    return binascii.hexlify(bin).upper()

def get_crc32_zip(zipf):
    """ Return CRC32 of .nds file contained in 'zipf'.
    Return None if no .nds file is found """
    result = None
    zip = zipfile.ZipFile(zipf, "r")
    for info in zip.infolist():
        if info.filename[len(info.filename)-4:].lower() == ".nds":
            crc = struct.pack('>L', info.CRC)
            result = binascii.hexlify(crc)[:8].upper()
            break
    zip.close()
    return result

def get_nds_filename_from_zip(zipf):
    """ Return the filename of .nds file contained in 'zipf',
    or None if no .nds file is found """
    result = None
    try:
        zip = zipfile.ZipFile(zipf, "r")
        for info in zip.infolist():
            if info.filename[len(info.filename)-4:].lower() == ".nds":
                result = info.filename
                break
        zip.close()
    except:
        # zipf doesnt exist anymore, probably the roms archives are getting updated
        # and old files are deleted
        pass
    return result

class RomArchivesRebuild(threading.Thread):
    """ Rebuild zip archive for games listed in 'games' dictionary """
    def __init__(self, gui, widgets, games):
        threading.Thread.__init__(self, name="RomArchivesRebuild")
        self.gui = gui
        self.widgets = widgets
        self.games = games
        self.games_to_fix = len(games)
        self.games_fixed = 0
        self.stopnow = False
    
    def run(self):
        # Deactivate widgets
        for widget in self.widgets:
            widget.set_sensitive(False)
            
        self.gui.toggle_rebuild_roms_archives_toolbutton()
        
        for key in sorted(self.games.iterkeys()):
            if self.stopnow == True:
                break
            self.games_fixed += 1
            text = " (%d/%d): " % (self.games_fixed, self.games_to_fix)  
            self.gui.update_statusbar("RomArchivesRebuild", text + _("Rebuilding archive for '%s'...") % key)
                
            oldzipfile = self.games[key]
            dir = oldzipfile.rsplit(os.sep, 1)[0]
            newzipfile = os.path.join(dir, key + ".zip")
            newndsname = key + ".nds"
            
            try:  
                zip = zipfile.ZipFile(oldzipfile, "r")
                
                if len(zip.infolist()) != 1:
                    # We can't handle zip with multiple files in it for now
                    zip.close()
                    continue
                
                info = zip.infolist()[0]
                oldndsname = info.filename
                oldndsfile = os.path.join(dir, oldndsname)
                if oldndsname == newndsname:
                    # nds name is ok, check zip name
                    if oldzipfile == newzipfile:
                        # Nothing to do
                        zip.close()
                        continue
                    else:
                        # Just rename the zip file, its content is ok
                        zip.close()
                        shutil.move(oldzipfile, newzipfile)
                        continue
                
                # Extract the nds file and rename it
                zip.extract(info, dir)
                # Reopen zip file in write mode (truncate it)
                zip.close()
                zip = zipfile.ZipFile(oldzipfile, "w", zipfile.ZIP_DEFLATED)
                zip.write(oldndsfile, newndsname)
                zip.close()
                # Rename zip file
                shutil.move(oldzipfile, newzipfile)
                # Remove nds file
                os.remove(oldndsfile)
            except:
                self.gui.update_statusbar("RomArchivesRebuild", _("Error while rebuilding archive for '%s'!") % key)
        
        if self.stopnow == True:
            self.gui.update_statusbar("RomArchivesRebuild", _("Rebuild stopped."))
        else:
            self.gui.update_statusbar("RomArchivesRebuild", _("Rebuild completed."))
        
        # restore original button
        self.gui.toggle_rebuild_roms_archives_toolbutton()
        # Add games to treeview
        self.gui.add_games()
                    
    def stop(self):
        """ Stop the thread """
        self.stopnow = True
