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
    result = None
    try:
        crc = binascii.crc32(file(filename, 'r').read())
        bin = struct.pack('>L', crc & 0xffffffff)
        result = binascii.hexlify(bin)[:8].upper()
    except:
        pass
    return result

def get_crc32_zip(zipf):
    """ Return CRC32 of .nds file contained in 'zipf'.
    Return None if no .nds file is found """
    result = None
    try:
        zip = zipfile.ZipFile(zipf, "r")
        for info in zip.infolist():
            if info.filename[len(info.filename)-4:].lower() == ".nds":
                crc = struct.pack('>L', info.CRC)
                result = binascii.hexlify(crc)[:8].upper()
                break
        zip.close()
    except:
        # Not a valid zip or it does not exist. Remove it if possible
        if os.path.exists(zipf):
            os.remove(zipf)
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

class RomArchiveExtract(threading.Thread):
    """ Extract the archives for games in 'games' dictionary { game_fullinfo : zipfile } """
    def __init__(self, gui, games, target):
        threading.Thread.__init__(self, name="RomArchiveExtract")
        self.gui = gui
        self.games = games
        self.gamesnumber_to_extract = len(games)
        self.gamesnumber_extracted = 0
        self.target = target
    
    def run(self):
        if not os.access(self.target, os.W_OK):
            text = _("Unable to extract archive to '%s'. Check write permissions of target directory.") % self.target
            self.gui.update_statusbar("RomArchiveExtract", text)
            return        
        
        for key in sorted(self.games.iterkeys()):
            game = key
            zipf = self.games[key]
            
            if self.gamesnumber_to_extract > 1:
                text = " (%d/%d) : " % (self.gamesnumber_extracted + 1, self.gamesnumber_to_extract)
            else:
                text = ""
            text += _("Extracting archive for '%s' ") % game
            text += _("in '%s'...") % self.target
            self.gui.update_statusbar("RomArchiveExtract", text)
        
            try:
                zip = zipfile.ZipFile(zipf, "r")
                try:
                    info = zip.infolist()[0]
                    if os.path.exists(os.path.join(self.target, info.filename)):
                        message = _("\nTarget file '%s' already exists. Overwrite?") % os.path.join(self.target, info.filename)
                        if self.gui.show_yesno_question_dialog(message) == False:
                            zip.close()
                            continue
                    zip.extractall(self.target)
                    self.gamesnumber_extracted += 1
                except:
                    self.gui.show_info_dialog(_("Unable to extract file from '%s'.") % zipf)
                zip.close()
            except:
                self.gui.show_info_dialog(_("Unable to open '%s'.") % zipf)
        
        if self.gamesnumber_extracted > 0:
            self.gui.update_statusbar("RomArchiveExtract", _("Extraction completed."))
        else:
            self.gui.update_statusbar("RomArchiveExtract", _("Extraction canceled."))
        
    def stop(self):
        return

class RomArchivesRescan(threading.Thread):
    """ Rescan roms archives on disk and rebuild games list """
    def __init__(self, gui):
        threading.Thread.__init__(self, name="RomArchivesRescan")
        self.gui = gui
    
    def run(self):
        self.gui.add_games()
        
    def stop(self):
        return

class RomArchivesRebuild(threading.Thread):
    """ Rebuild zip archive for games listed in 'games' dictionary.
    games = { fullinfo : (oldfile, relnum) } """
    def __init__(self, gui, widgets, games):
        threading.Thread.__init__(self, name="RomArchivesRebuild")
        self.gui = gui
        self.widgets = widgets
        self.games = games
        self.gamesnumber_to_fix = len(games)
        self.gamesnumber_fixed = 0
        self.is_zip = True # Are we working on zip or nds?
        self.stopnow = False
    
    def run(self):
        # Deactivate widgets
        for widget in self.widgets:
            widget.set_sensitive(False)
            
        self.gui.toggle_rebuild_roms_archives_toolbutton(True)
        
        for key in sorted(self.games.iterkeys()):
            if self.stopnow == True:
                break
            self.gamesnumber_fixed += 1
            if self.gamesnumber_to_fix > 1:
                text = " (%d/%d) : " % (self.gamesnumber_fixed, self.gamesnumber_to_fix)
            else:
                text = ""
            text += _("Rebuilding archive for '%s'...") % key
            self.gui.update_statusbar("RomArchivesRebuild", text)
            
            oldfile = self.games[key][0]
            if oldfile[len(oldfile)-4:].lower() == ".zip":
                self.is_zip = True
            else: # '.nds' file
                self.is_zip = False
            dir = oldfile.rsplit(os.sep, 1)[0]
            newzipfile = os.path.join(dir, key + ".zip")
            newndsname = key + ".nds"
            
            try:
                if self.is_zip == True:
                    zip = zipfile.ZipFile(oldfile, "r")
                    if len(zip.infolist()) != 1:
                        # We can't handle zip with multiple files in it for now
                        zip.close()
                        continue
                    info = zip.infolist()[0]
                    oldndsname = info.filename
                    oldndsfile = os.path.join(dir, oldndsname)
                    if oldndsname == newndsname:
                        # nds name is ok, check zip name
                        if oldfile == newzipfile:
                            # Nothing to do
                            zip.close()
                            # Update game in treeview
                            self.gui.update_game(self.games[key][1], newzipfile)
                            continue
                        else:
                            # Just rename the zip file, its content is ok
                            zip.close()
                            shutil.move(oldfile, newzipfile)
                            # Update game in treeview
                            self.gui.update_game(self.games[key][1], newzipfile)
                            continue
                    # Extract the nds file and delete the old zip file
                    zip.extract(info, dir)
                    zip.close()
                    os.remove(oldfile)
                    oldfile = os.path.join(dir, oldndsname)
                
                # Now we can work with oldfile
                
                # Open the new zip file andrite in it the 'oldfile' as 'newndsname'
                zip = zipfile.ZipFile(newzipfile, "w", zipfile.ZIP_DEFLATED)
                zip.write(oldfile, newndsname)
                zip.close()
                # Remove old nds file
                os.remove(oldfile)
                # Update game in treeview
                self.gui.update_game(self.games[key][1], newzipfile)
            except:
                self.gui.update_statusbar("RomArchivesRebuild", _("Error while building archive for '%s'!") % key)
        
        if self.stopnow == True:
            self.gui.update_statusbar("RomArchivesRebuild", _("Rebuild stopped."))
        else:
            self.gui.update_statusbar("RomArchivesRebuild", _("Rebuild completed."))
        
        # restore original button
        self.gui.toggle_rebuild_roms_archives_toolbutton(True)
        # reactivate all widgets
        self.gui.activate_widgets()
        # Restore previous treeview selection
        self.gui.set_previous_treeview_cursor(True)
                    
    def stop(self):
        """ Stop the thread """
        self.stopnow = True
