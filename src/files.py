#!/usr/bin/env python
#
# DRM - DsRomsManager
#
# Copyright (C) 2008-2009 by
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
import statvfs
import shutil
import threading
import struct
import binascii
import zipfile
import commands

import gettext
_ = gettext.gettext

def get_crc32(filename):
    """ Return CRC32 of 'filename' or None on error. """
    result = None
    try:
        crc = binascii.crc32(file(filename, 'r').read())
        bin = struct.pack('>L', crc & 0xffffffff)
        result = binascii.hexlify(bin)[:8].upper()
    except:
        pass
    return result

def get_crc32_zip(zipf):
    """
    Return CRC32 of .nds file contained in 'zipf'.
    Return 'None' if no .nds file is found, or if .zip contains more files.
    Try to remove invalid zip files.
    """
    result = None
    try:
        zip = zipfile.ZipFile(zipf, "r")
        if len(zip.infolist()) > 1:
            return result
        info = zip.infolist()[0]
        if info.filename[len(info.filename) - 4:].lower() == ".nds":
            crc = struct.pack('>L', info.CRC)
            result = binascii.hexlify(crc)[:8].upper()
        zip.close()
    except:
        # Not a valid zip or it does not exist. Remove it if possible
        try:
            os.remove(zipf)
        except:
            pass
    return result

def get_nds_filename_from_zip(zipf):
    """
    Return the filename of .nds file contained in 'zipf'.
    Return 'None' if no .nds file is found, or if .zip contains more files.
    """
    result = None
    try:
        zip = zipfile.ZipFile(zipf, "r")
        if len(zip.infolist()) > 1:
            return result
        info = zip.infolist()[0]
        if info.filename[len(info.filename) - 4:].lower() == ".nds":
            result = info.filename
        zip.close()
    except:
        # zipf doesnt exist anymore.
        # Probably the roms archives are getting updated.
        pass
    return result

class RomArchiveExtract(threading.Thread):
    """
    Extract the archives for games in 'games' dictionary.
    'games' dictionary must be in this format: { fullinfo : zipfile }
    """
    def __init__(self, gui, games, target, trim, temp, show_trim_details):
        """ Prepare thread """
        threading.Thread.__init__(self, name = "RomArchiveExtract")
        self.gui = gui
        self.games = games
        self.gamesnumber_to_extract = len(games)
        self.gamesnumber_extracted = 0
        self.gamesnumber_processed = 0
        self.target = target
        self.temp = temp
        self.trim = trim
        self.show_trim_details = show_trim_details
        self.total_saved_space = 0 # total saved space by trimming
        self.overwrite = False
        self.ask_for_overwrite = True
        self.stopnow = False
    
    def run(self):
        """ Start thread """
        if not os.access(self.target, os.W_OK):
            text = _("Unable to extract archive to '%s'. ") % self.target
            text += _("Check available space and write permissions for target directory.") 
            self.gui.update_statusbar("RomArchiveExtract", text, True)
            return
        
        for key in sorted(self.games.iterkeys()):
            if self.stopnow:
                message = _("Extraction stopped.")
                self.gui.update_statusbar("RomArchiveExtract", message, True)
                return
            game = key
            zipf = self.games[key]
            self.gamesnumber_processed += 1
            if self.gamesnumber_to_extract > 1:
                text = " (%d/%d) : " % (self.gamesnumber_processed, self.gamesnumber_to_extract)
            else:
                text = ""
            text += _("Extracting archive for '%s'...") % game
            self.gui.update_statusbar("RomArchiveExtract", text, True)
        
            # Get free space on target directory (in KB)
            stats = os.statvfs(self.target)
            free_space = stats[statvfs.F_BSIZE] * stats[statvfs.F_BAVAIL] / 1024
        
            try:
                zip = zipfile.ZipFile(zipf, "r")
                try:
                    info = zip.infolist()[0]
                    if os.path.exists(os.path.join(self.target, info.filename)):
                        if self.ask_for_overwrite:
                            message = _("Target file '%s' already exists. Overwrite?") % os.path.join(self.target, info.filename)
                            response = self.gui.show_yesnoalwaysnever_question_dialog(message, True)
                            if response == 0: # No
                                self.overwrite = False
                            elif response == 1: # Yes
                                self.overwrite = True
                            elif response == -1: # No for all
                                self.overwrite = False
                                self.ask_for_overwrite = False
                            else: # Yes for all
                                self.overwrite = True
                                self.ask_for_overwrite = False
                        if self.overwrite:
                            # the file already exists in target directory and we can overwrite it. So, we have more free space.
                            free_space += os.path.getsize(os.path.join(self.target, info.filename)) / 1024
                        else:
                            zip.close()
                            continue

                    if self.trim != None:
                        # Extract in 'temp' directory               
                        zip.extract(info, self.temp)
                        # Get file stats
                        cmd = self.trim + ' -s "' + os.path.join(self.temp, info.filename) + '"'
                        output = commands.getoutput(cmd)
                        try:
                            original_size = int(output.split("\n")[1].split("\t")[2].split()[0])
                            trimmed_size = int(output.split("\n")[2].split("\t")[2].split()[0])
                            saved_space = int(output.split("\n")[3].split("\t")[2].split()[0])
                        except: # rom can't be trimmed
                            message = _("Unable to trim %s!") % game
                            # check if we have enough free space to leave it untrimmed
                            if info.file_size / 1024 > free_space: # We don't
                                self.gui.show_error_dialog(message, True)
                                os.remove(os.path.join(self.temp, info.filename))
                            else:
                                message += _(" Leave it untrimmed?")
                                if self.gui.show_yesno_question_dialog(message, True) == True: # Yes
                                    shutil.move(os.path.join(self.temp, info.filename), self.target)
                                else: # No
                                    os.remove(os.path.join(self.temp, info.filename))
                            zip.close()
                            continue
                        # Check if we have enough free space on 'target'
                        if trimmed_size > free_space: # We don't
                            message = _("Not enough free space on target directory for '%s'. Extraction canceled.") % game
                            self.gui.update_statusbar("RomArchiveExtract", message, True)
                            os.remove(os.path.join(self.temp, info.filename))
                            zip.close()
                            return
                        # Enough free space, let's continue
                        if self.gamesnumber_to_extract > 1:
                            message = " (%d/%d) : " % (self.gamesnumber_processed, self.gamesnumber_to_extract)
                        else:
                            message = ""
                        message += _("Trimming '%s'...") % game
                        self.gui.update_statusbar("RomArchiveExtract", message, True)
                        # Trim using 'target' as trim output directory
                        cmd = self.trim + ' -d "' + self.target + '" -b "' + os.path.join(self.temp, info.filename) + '"'
                        commands.getoutput(cmd)
                        # Remove temp file
                        os.remove(os.path.join(self.temp, info.filename))
                        # Update total saved space
                        self.total_saved_space += saved_space
                        if self.show_trim_details:
                            if self.gamesnumber_to_extract > 1:
                                output = " (%d/%d)" % (self.gamesnumber_processed, self.gamesnumber_to_extract)
                            else:
                                output = ""
                            output += " *** " + info.filename + "\n\t"
                            output += _("Original size:") + "\t" + str(original_size) + " KB\n\t"
                            output += _("Trimmed size:") + "\t" + str(trimmed_size) + " KB\n\t"
                            output += _("Saved space:") + "\t" + str(saved_space) + " KB\n"
                            self.gui.show_trim_details_window(output, True)
                    
                    else: # No trim, extract in 'target' directory directly
                        if info.file_size / 1024 > free_space:
                            message = _("Not enough free space on target directory for '%s'. Extraction canceled.") % game
                            self.gui.update_statusbar("RomArchiveExtract", message, True)
                            zip.close()
                            return
                        else:
                            zip.extract(info, self.target)
                    self.gamesnumber_extracted += 1
                except:
                    self.gui.show_error_dialog(_("Unable to extract file from '%s'.") % zipf, True)
                zip.close()
            except:
                self.gui.show_error_dialog(_("Unable to open '%s'.") % zipf, True)
        
        if self.trim != None and self.show_trim_details and self.gamesnumber_extracted > 0:
            message = "\n" + _("Done. Total saved space:")
            message += " " + str(self.total_saved_space) + " KB (~" + str(self.total_saved_space / 1024) + " MB)\n"
            self.gui.show_trim_details_window(message, True)
        
        if self.gamesnumber_extracted > 0:
            message = _("Extraction completed.")
            if self.total_saved_space > 0 and not self.show_trim_details: # add info about trimming on statusbar 
                message += _(" Total saved space by trimming:")
                message += " " + str(self.total_saved_space) + " KB (~" + str(self.total_saved_space / 1024) + " MB)"
        else:
            message = _("Extraction canceled.")
        self.gui.update_statusbar("RomArchiveExtract", message, True)
        
    def stop(self):
        """ Stop thread """
        self.stopnow = True

class RomArchivesRescan(threading.Thread):
    """ Rescan roms archives on disk and rebuild games list """
    def __init__(self, gui):
        """ Prepare thread """
        threading.Thread.__init__(self, name = "RomArchivesRescan")
        self.gui = gui
    
    def run(self):
        """ Start thread """
        self.gui.add_games(scan_anyway = True, use_threads = True)
        
    def stop(self):
        """ Stop thread """
        return

class RomArchivesRebuild(threading.Thread):
    """
    Rebuild zip archive for games listed in 'games' dictionary.
    'games' dictionary must be in this format: { fullinfo : (filename, oldfile, relnum) }
    """
    def __init__(self, gui, widgets, games):
        """ Prepare thread """
        threading.Thread.__init__(self, name = "RomArchivesRebuild")
        self.gui = gui
        self.games = games
        self.gamesnumber_to_fix = len(games)
        self.gamesnumber_fixed = 0
        self.is_zip = True # Are we working on zip or nds?
        self.stopnow = False
        # Deactivate widgets
        for widget in widgets:
            widget.set_sensitive(False)
    
    def run(self):
        """ Start thread """
        self.gui.toggle_rebuild_roms_archives_toolbutton(True)
        
        for key in sorted(self.games.iterkeys()):
            if self.stopnow:
                break
            self.gamesnumber_fixed += 1
            if self.gamesnumber_to_fix > 1:
                text = " (%d/%d) : " % (self.gamesnumber_fixed, self.gamesnumber_to_fix)
            else:
                text = ""
            text += _("Rebuilding archive for '%s'...") % key
            self.gui.update_statusbar("RomArchivesRebuild", text, True)
            
            oldfile = self.games[key][1]
            if oldfile[len(oldfile) - 4:].lower() == ".zip":
                self.is_zip = True
            else: # '.nds' file
                self.is_zip = False
            dir = oldfile.rsplit(os.sep, 1)[0]
            newzipfile = os.path.join(dir, self.games[key][0] + ".zip")
            newndsname = self.games[key][0] + ".nds"
            
            try:
                if self.is_zip:
                    zip = zipfile.ZipFile(oldfile, "r")
                    if len(zip.infolist()) != 1: # Don't handle zip with multiple files in it
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
                            self.gui.update_game(self.games[key][2], newzipfile, True)
                            continue
                        else:
                            # Just rename the zip file, its content is ok
                            zip.close()
                            shutil.move(oldfile, newzipfile)
                            # Update game in treeview
                            self.gui.update_game(self.games[key][2], newzipfile, True)
                            continue
                    # Extract the nds file and delete the old zip file
                    zip.extract(info, dir)
                    zip.close()
                    os.remove(oldfile)
                    oldfile = os.path.join(dir, oldndsname)
                
                # Now we can work with oldfile
                
                # Open the new zip file and write in it the 'oldfile' as 'newndsname'
                zip = zipfile.ZipFile(newzipfile, "w", zipfile.ZIP_DEFLATED)
                zip.write(oldfile, newndsname)
                zip.close()
                # Remove old nds file
                os.remove(oldfile)
                # Update game in treeview
                self.gui.update_game(self.games[key][2], newzipfile, True)
            except:
                self.gui.update_statusbar("RomArchivesRebuild", _("Error while building archive for '%s'!") % key, True)
        
        if self.stopnow:
            self.gui.update_statusbar("RomArchivesRebuild", _("Rebuilding stopped."), True)
        else:
            self.gui.update_statusbar("RomArchivesRebuild", _("Rebuilding completed."), True)
        
        # restore original button
        self.gui.toggle_rebuild_roms_archives_toolbutton(True)
        # reactivate all widgets
        self.gui.activate_widgets(True)
                    
    def stop(self):
        """ Stop the thread """
        self.stopnow = True
