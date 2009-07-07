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
import threading
import gobject

import gettext
_ = gettext.gettext

try:
	import gtk
	import gtk.gdk as gdk
except:
	print "You have to install 'gtk' modules to run this application."
	from sys import exit
	exit(1)

from globals import *
from db import *
from downloaders import *
from updaters import *
from files import *

import glob
import shutil

TVC_CHECK = 0
TVC_FLAG = 1
TVC_RELEASE_NUMBER = 2
TVC_TITLE = 3

class Gui(threading.Thread):
	"""	Graphical User Interface """
	def __init__(self, threads):
		""" Init Gui """
		threading.Thread.__init__(self, name = "Gui")
		
		self.threads = threads
		
		gdk.threads_init()
		
		self.builder = gtk.Builder()
		self.builder.set_translation_domain(APP_NAME.lower())
		self.builder.add_from_file(os.path.join(DATA_DIR, "drm.glade"))
		
		self.main_window = self.builder.get_object("main_window")
		self.images_window = self.builder.get_object("images_window")
		self.options_dialog = self.builder.get_object("options_dialog")
		self.dat_update_toolbutton = self.builder.get_object("dat_update_toolbutton")
		self.images_download_toolbutton = self.builder.get_object("images_download_toolbutton")
		self.rescan_roms_archives_toolbutton = self.builder.get_object("rescan_roms_archives_toolbutton")
		self.rebuild_roms_archives_toolbutton = self.builder.get_object("rebuild_roms_archives_toolbutton")
		self.show_review_toolbutton = self.builder.get_object("show_review_toolbutton")
		self.options_toolbutton = self.builder.get_object("options_toolbutton")
		self.games_check_ok_checkbutton = self.builder.get_object("games_check_ok_checkbutton")
		self.games_check_no_checkbutton = self.builder.get_object("games_check_no_checkbutton")
		self.games_check_convert_checkbutton = self.builder.get_object("games_check_convert_checkbutton")
		self.options_check_images_crc_checkbutton = self.builder.get_object("options_check_images_crc_checkbutton")
		self.options_autoscan_archives_at_start_checkbutton = self.builder.get_object("options_autoscan_archives_at_start_checkbutton")
		self.options_autoscan_archives_at_datupdate_checkbutton = self.builder.get_object("options_autoscan_archives_at_datupdate_checkbutton")
		self.options_trim_roms_checkbutton = self.builder.get_object("options_trim_roms_checkbutton")
		self.options_trim_roms_details_checkbutton = self.builder.get_object("options_trim_roms_details_checkbutton")
		self.options_roms_path_filechooserbutton = self.builder.get_object("options_roms_path_filechooserbutton")
		self.options_unknown_roms_path_filechooserbutton = self.builder.get_object("options_unknown_roms_path_filechooserbutton")
		self.options_new_roms_path_filechooserbutton = self.builder.get_object("options_new_roms_path_filechooserbutton")
		self.options_images_path_filechooserbutton = self.builder.get_object("options_images_path_filechooserbutton")
		self.options_extractin_path_hbox = self.builder.get_object("options_extractin_path_hbox")
		self.options_extractin_path_filechooserbutton = self.builder.get_object("options_extractin_path_filechooserbutton")
		self.options_extractin_path_enable_button = self.builder.get_object("options_extractin_path_enable_button")
		self.options_review_url_entry = self.builder.get_object("options_review_url_entry")
		self.options_ok_button = self.builder.get_object("options_ok_button")
		self.options_cancel_button = self.builder.get_object("options_cancel_button")
		self.about_toolbutton = self.builder.get_object("about_toolbutton")
		self.images_window_eventbox = self.builder.get_object("images_window_eventbox")
		self.images_window_image1 = self.builder.get_object("images_window_image1")
		self.images_window_image2 = self.builder.get_object("images_window_image2")
		self.list_scrolledwindow = self.builder.get_object("list_scrolledwindow")
		self.list_treeview = self.builder.get_object("list_treeview")
		self.list_treeview_popup_menu = self.builder.get_object("list_treeview_popup_menu")
		self.list_treeview_popup_extract_menuitem = self.builder.get_object("list_treeview_popup_extract_menuitem")
		self.list_treeview_popup_extractin_menuitem = self.builder.get_object("list_treeview_popup_extractin_menuitem")
		self.list_treeview_popup_extract_stop_menuitem = self.builder.get_object("list_treeview_popup_extract_stop_menuitem")
		self.list_treeview_popup_rebuildarchive_menuitem = self.builder.get_object("list_treeview_popup_rebuildarchive_menuitem")
		self.list_game_label = self.builder.get_object("list_games_label")
		self.images_eventbox = self.builder.get_object("images_eventbox")
		self.image1 = self.builder.get_object("image1")
		self.image2 = self.builder.get_object("image2")
		self.image1_frame = self.builder.get_object("image1_frame")
		self.image2_frame = self.builder.get_object("image2_frame")
		self.info_title_eventbox = self.builder.get_object("info_title_eventbox")
		self.info_title_label = self.builder.get_object("info_title_label")
		self.info_location_label = self.builder.get_object("info_location_label")
		self.info_publisher_label = self.builder.get_object("info_publisher_label")
		self.info_source_label = self.builder.get_object("info_source_label")
		self.info_save_label = self.builder.get_object("info_save_label")
		self.info_size_label = self.builder.get_object("info_size_label")
		self.info_comment_label = self.builder.get_object("info_comment_label")
		self.info_crc_label = self.builder.get_object("info_crc_label")
		self.info_language_label = self.builder.get_object("info_language_label")
		self.filter_name_entry = self.builder.get_object("filter_name_entry")
		self.filter_location_combobox = self.builder.get_object("filter_location_combobox")
		self.filter_language_combobox = self.builder.get_object("filter_language_combobox")
		self.filter_size_combobox = self.builder.get_object("filter_size_combobox")
		self.filter_clear_button = self.builder.get_object("filter_clear_button")
		self.statusbar = self.builder.get_object("statusbar")
		self.about_dialog = self.builder.get_object("about_dialog")
		self.trim_details_window = self.builder.get_object("trim_details_window")
		self.trim_details_textview = self.builder.get_object("trim_details_textview")
		self.trim_details_textbuffer = self.trim_details_textview.get_buffer()
		# Widgets needed for hiding informations
		self.images_hbox = self.builder.get_object("images_hbox")
		self.info_label_vbox = self.builder.get_object("info_label_vbox")
		
		# Get screen's height and calculate the resize rate
		self.screen_height = self.main_window.get_screen().get_height()
		if self.screen_height <= 600:
			self.images_resize_rate = 0.5 # 50% 
		elif self.screen_height <= 800:
			self.images_resize_rate = 0.75 # 75%
		else:
			self.images_resize_rate = 1 # 100 %
			
		self.main_window.set_title(APP_NAME + " - " + APP_VERSION)
		self.about_dialog.set_version(APP_VERSION)
		self.main_window_visible = True
		
		# Enable click on website url in about dialog
		def about_dialog_url_clicked(dialog, link, user_data):
			pass
		gtk.about_dialog_set_url_hook(about_dialog_url_clicked, None)
		
		# Set icon and logo in main_window and about_dialog
		try:
			self.main_window.set_icon_from_file(os.path.join(DATA_IMG_DIR, "icon.png"))
			self.about_dialog.set_icon_from_file(os.path.join(DATA_IMG_DIR, "icon.png"))
			self.about_dialog.set_logo(gdk.pixbuf_new_from_file(os.path.join(DATA_IMG_DIR, "icon.png")))
		except:
			pass
		
		## StatusIcon stuff
		# popup menu
		self.popup_menu = gtk.Menu()
		self.toggle_main_window_menuitem = gtk.ImageMenuItem(_("Hide"))
		self.toggle_main_window_menuitem.set_image(gtk.image_new_from_stock(gtk.STOCK_LEAVE_FULLSCREEN, gtk.ICON_SIZE_MENU))
		self.toggle_main_window_menuitem.connect('activate', self.on_statusicon_toggle_main_window_activate)
		self.toggle_main_window_menuitem.set_tooltip_text(_("Hide main window."))
		self.popup_menu.append(self.toggle_main_window_menuitem)
		menuitem = gtk.SeparatorMenuItem()
		self.popup_menu.append(menuitem)
		self.dat_update_menuitem = gtk.ImageMenuItem(_("Update DAT"))
		self.dat_update_menuitem.set_image(gtk.image_new_from_stock(gtk.STOCK_REFRESH, gtk.ICON_SIZE_MENU))
		self.dat_update_menuitem.connect('activate', self.on_statusicon_dat_update_activate)
		self.dat_update_menuitem.set_tooltip_text(self.dat_update_toolbutton.get_tooltip_text())
		self.popup_menu.append(self.dat_update_menuitem)
		self.images_download_menuitem = gtk.ImageMenuItem(_("Download images"))
		self.images_download_menuitem.set_image(gtk.image_new_from_stock(gtk.STOCK_JUMP_TO, gtk.ICON_SIZE_MENU))
		self.images_download_menuitem.connect('activate', self.on_statusicon_images_download_activate)
		self.images_download_menuitem.set_tooltip_text(self.images_download_toolbutton.get_tooltip_text())
		self.popup_menu.append(self.images_download_menuitem)
		menuitem = gtk.SeparatorMenuItem()
		self.popup_menu.append(menuitem)
		self.rescan_roms_archives_menuitem = gtk.ImageMenuItem(_("Rescan archives"))
		self.rescan_roms_archives_menuitem.set_image(gtk.image_new_from_stock(gtk.STOCK_FIND, gtk.ICON_SIZE_MENU))
		self.rescan_roms_archives_menuitem.connect('activate', self.on_statusicon_rescan_roms_archives_activate)
		self.rescan_roms_archives_menuitem.set_tooltip_text(self.rescan_roms_archives_toolbutton.get_tooltip_text())
		self.popup_menu.append(self.rescan_roms_archives_menuitem)
		self.rebuild_roms_archives_menuitem = gtk.ImageMenuItem(_("Rebuild archives"))
		self.rebuild_roms_archives_menuitem.set_image(gtk.image_new_from_stock(gtk.STOCK_CONVERT, gtk.ICON_SIZE_MENU))
		self.rebuild_roms_archives_menuitem.connect('activate', self.on_statusicon_rebuild_roms_archives_activate)
		self.rebuild_roms_archives_menuitem.set_tooltip_text(self.rebuild_roms_archives_toolbutton.get_tooltip_text())
		self.popup_menu.append(self.rebuild_roms_archives_menuitem)
		menuitem = gtk.SeparatorMenuItem()
		self.popup_menu.append(menuitem)
		self.show_review_menuitem = gtk.ImageMenuItem(_("Reviews"))
		self.show_review_menuitem.set_image(gtk.image_new_from_stock(gtk.STOCK_DIALOG_INFO, gtk.ICON_SIZE_MENU))
		self.show_review_menuitem.connect('activate', self.on_statusicon_show_review_activate)
		self.show_review_menuitem.set_tooltip_text(self.show_review_toolbutton.get_tooltip_text())
		self.popup_menu.append(self.show_review_menuitem)
		menuitem = gtk.SeparatorMenuItem()
		self.popup_menu.append(menuitem)
		self.options_menuitem = gtk.ImageMenuItem(_("Options"))
		self.options_menuitem.set_image(gtk.image_new_from_stock(gtk.STOCK_PROPERTIES, gtk.ICON_SIZE_MENU))
		self.options_menuitem.connect('activate', self.on_statusicon_options_activate)
		self.options_menuitem.set_tooltip_text(self.options_toolbutton.get_tooltip_text())
		self.popup_menu.append(self.options_menuitem)
		menuitem = gtk.SeparatorMenuItem()
		self.popup_menu.append(menuitem)
		self.about_menuitem = gtk.ImageMenuItem(_("About"))
		self.about_menuitem.set_image(gtk.image_new_from_stock(gtk.STOCK_ABOUT, gtk.ICON_SIZE_MENU))
		self.about_menuitem.connect('activate', self.on_statusicon_about_activate)
		self.about_menuitem.set_tooltip_text(self.about_toolbutton.get_tooltip_text())
		self.popup_menu.append(self.about_menuitem)
		menuitem = gtk.SeparatorMenuItem()
		self.popup_menu.append(menuitem)
		self.quit_menuitem = gtk.ImageMenuItem(_("Quit"))
		self.quit_menuitem.set_image(gtk.image_new_from_stock(gtk.STOCK_QUIT, gtk.ICON_SIZE_MENU))
		self.quit_menuitem.connect('activate', self.on_statusicon_quit_activate)
		self.quit_menuitem.set_tooltip_text(_("Quit 'DsRomsManager'."))
		self.popup_menu.append(self.quit_menuitem)
		# status icon
		self.statusicon = gtk.StatusIcon()
		self.statusicon.set_from_file(os.path.join(DATA_IMG_DIR, "icon.png"))
		self.statusicon.set_tooltip(self.main_window.get_title())
		self.statusicon.connect('activate', self.on_statusicon_activate)
		self.statusicon.connect('popup-menu', self.on_statusicon_popup_menu, self.popup_menu)
		self.statusicon.set_visible(True)
		
		# Clear images
		self.image1.clear()
		self.image2.clear()
		self.images_window_image1.clear()
		self.images_window_image2.clear()
		
		# Load flags images
		self.flags = []
		for i in countries_short.keys():
			file = os.path.join(DATA_IMG_DIR, countries_short[i].lower() + ".png")
			self.flags.append(gdk.pixbuf_new_from_file(file))
		
		# Load checks images
		self.checks = []
		image = gtk.Image()
		self.checks.append(image.render_icon(gtk.STOCK_NO, gtk.ICON_SIZE_MENU))
		self.checks.append(image.render_icon(gtk.STOCK_OK, gtk.ICON_SIZE_MENU))
		self.checks.append(image.render_icon(gtk.STOCK_CONVERT, gtk.ICON_SIZE_MENU))
		
		# Setup all needed stuff for the main list treeview
		self.list_treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
		self.list_treeview_model = gtk.ListStore(gdk.Pixbuf, gdk.Pixbuf, int, str)
		self.list_treeview.set_model(self.list_treeview_model)
		self.list_treeview_crt = gtk.CellRendererText()
		self.list_treeview_crt_img = gtk.CellRendererPixbuf()
		self.list_treeview_tvc_found = gtk.TreeViewColumn(None, self.list_treeview_crt_img, pixbuf = TVC_CHECK)
		self.list_treeview.append_column(self.list_treeview_tvc_found)
		self.list_treeview_tvc_region = gtk.TreeViewColumn(None, self.list_treeview_crt_img, pixbuf = TVC_FLAG)
		self.list_treeview.append_column(self.list_treeview_tvc_region)
		self.list_treeview_tvc_relnum = gtk.TreeViewColumn("#", self.list_treeview_crt, text = TVC_RELEASE_NUMBER)
		self.list_treeview_tvc_relnum.set_sort_column_id(TVC_RELEASE_NUMBER)
		self.list_treeview.append_column(self.list_treeview_tvc_relnum)
		self.list_treeview_tvc_name = gtk.TreeViewColumn(_("Title"), self.list_treeview_crt, text = TVC_TITLE)
		self.list_treeview_tvc_name.set_sort_column_id(TVC_TITLE)
		self.list_treeview.append_column(self.list_treeview_tvc_name)
		
		# Setup all needed stuff for location combobox
		self.filter_location_model = gtk.ListStore(str, str)
		self.filter_location_combobox.set_model(self.filter_location_model)
		self.filter_location_crt = gtk.CellRendererText()
		self.filter_location_combobox.pack_start(self.filter_location_crt)
		self.filter_location_combobox.add_attribute(self.filter_location_crt, 'text', 0)  
		self.filter_location_model.append([_("All"), "All"])
		for i in countries.keys():
			self.filter_location_model.append([_(countries[i]), countries[i]])
		self.filter_location_combobox.set_active(0)
		
		# Setup all needed stuff for language combobox
		self.filter_language_model = gtk.ListStore(str, str)
		self.filter_language_combobox.set_model(self.filter_language_model)
		self.filter_language_crt = gtk.CellRendererText()
		self.filter_language_combobox.pack_start(self.filter_language_crt)
		self.filter_language_combobox.add_attribute(self.filter_language_crt, 'text', 0)  
		self.filter_language_model.append([_("All"), "All"])
		for i in langs.keys():
			if langs[i] != "Unknown":
				self.filter_language_model.append([_(langs[i]), langs[i]])
		self.filter_language_combobox.set_active(0)
		
		# Setup all needed stuff for size combobox
		self.filter_size_model = gtk.ListStore(str, str)
		self.filter_size_combobox.set_model(self.filter_size_model)
		self.filter_size_crt = gtk.CellRendererText()
		self.filter_size_combobox.pack_start(self.filter_size_crt)
		self.filter_size_combobox.add_attribute(self.filter_size_crt, 'text', 0)  
		self.filter_size_model.append([_("All"), "All"])
		for size in sizes:
			self.filter_size_model.append([_(size), size])
		self.filter_size_combobox.set_active(0)
		
		# Set games checks filters
		self.games_check_ok_checkbutton.set_active(config.get_option("show_available_games"))
		self.games_check_no_checkbutton.set_active(config.get_option("show_not_available_games"))
		self.games_check_convert_checkbutton.set_active(config.get_option("show_rebuildable_games"))
		
		# Connect signals
		self.main_window.connect("delete_event", self.on_main_window_delete_event)
		self.statusbar.connect("text-pushed", self.on_statusbar_text_pushed)
		self.dat_update_toolbutton.connect("clicked", self.on_dat_update_toolbutton_clicked)
		self.rescan_roms_archives_toolbutton.connect("clicked", self.on_rescan_roms_archives_toolbutton_clicked)
		self.filter_clear_button.connect("clicked", self.on_filter_clear_button_clicked)
		self.options_toolbutton.connect("clicked", self.on_options_toolbutton_clicked)
		self.options_dialog.connect("response", self.on_options_dialog_response)
		self.options_dialog.connect("delete_event", self.on_options_dialog_delete_event)
		self.options_extractin_path_enable_button.connect("clicked", self.on_options_extractin_path_enable_button_clicked)
		self.images_window.connect("delete_event", self.on_images_window_delete_event)
		self.about_toolbutton.connect("clicked", self.on_about_toolbutton_clicked)
		self.about_dialog.connect("response", self.on_about_dialog_response)
		self.list_treeview.get_selection().connect("changed", self.on_list_treeview_selection_changed)
		self.list_treeview.connect("button-press-event", self.on_list_treeview_button_press_event)
		self.list_treeview_popup_extract_menuitem.connect("activate", self.on_list_treeview_popup_extract_menuitem_activate)
		self.list_treeview_popup_extractin_menuitem.connect("activate", self.on_list_treeview_popup_extractin_menuitem_activate)
		self.list_treeview_popup_extract_stop_menuitem.connect("activate", self.on_list_treeview_popup_extract_stop_menuitem_activate)
		self.list_treeview_popup_rebuildarchive_menuitem.connect("activate", self.on_list_treeview_popup_rebuildarchive_menuitem_activate)
		self.show_review_toolbutton.connect("clicked", self.on_show_review_toolbutton_clicked)
		self.games_check_ok_checkbutton.connect("toggled", self.on_games_check_ok_checkbutton_toggled)
		self.games_check_no_checkbutton.connect("toggled", self.on_games_check_no_checkbutton_toggled)
		self.games_check_convert_checkbutton.connect("toggled", self.on_games_check_convert_checkbutton_toggled)
		self.options_trim_roms_checkbutton.connect("toggled", self.on_options_trim_roms_checkbutton_toggled)
		self.trim_details_window.connect("delete_event", self.on_trim_details_window_delete_event)
		if self.images_resize_rate != 1:
			self.images_window_eventbox.connect("button-press-event", self.toggle_images_window)
		# We need signal id for the following signals, to block them when needed
		self.fne_sid = self.filter_name_entry.connect("changed", self.on_filter_triggered)
		self.flocc_sid = self.filter_location_combobox.connect("changed", self.on_filter_triggered)
		self.flanc_sid = self.filter_language_combobox.connect("changed", self.on_filter_triggered)
		self.fsc_sid = self.filter_size_combobox.connect("changed", self.on_filter_triggered)
		self.aidtb_sid = self.images_download_toolbutton.connect("clicked", self.on_images_download_toolbutton_clicked)
		self.rratb_sid = self.rebuild_roms_archives_toolbutton.connect("clicked", self.on_rebuild_roms_archives_toolbutton_clicked)
		self.ite_sid = None # info_title_eventbox signal
		
		self.quitting = False # Are we quitting?
		self.canexitnow = True # Can we exit now?
		
		self.db = None
		
		self.gamesnumber_total = 0 # Number of all games shown in treeview
		self.gamesnumber_available = 0 # Number of available games shown in treeview
		self.gamesnumber_not_available = 0 # Number of not available games shown in treeview
		self.gamesnumber_fixable = 0 # Number of fixable games shown in treeview
		self.games_to_rebuild = {} # Dictionary of all the games to rebuild in the format { fullinfo : (filename, oldfile, relnum) }
		
		# Does the current games list contain games that should be filter by games_checks checkbuttons?
		self.dirty_gameslist = False
		
		self.previous_selection_release_number = None
		
		# Dictionary of all the games checksums as keys, pointing to roms paths on the disk. Format: { crc : pathondisk }
		self.checksums = {}
		
		self.autoscan_archives_at_start = config.get_option("autoscan_archives_at_start")
		self.archives_already_scanned = False # Have archives been already scanned?
		
		self.options_save_extractin_path = True # Should we save the 'Extract in' path in options window?
				
		self.deactivate_widgets()
		
	def run(self):
		""" Start thread """
		gtk.main()
	
	def stop(self):
		""" Stop thread """
		self.quit()
	
	### Private functions
	
	def __add_game_to_list(self, game, anyway = False, insert_before_iter = None, use_threads = False):
		"""
		Add 'game' in treeview and return it's archive state (CHECKS_OK, CHECKS_NO, CHECKS_CONVERT).
		If 'anyway' is True, add the game to treeview model even if it should be filtered.
		If 'insert_before_iter' is a valid iter, add the game before the passed iter.
		Return CHECKS_ERROR on error.
		"""
		returnvalue = CHECKS_ERROR
		if self.quitting:
			return returnvalue
		
		relnum = game[GAME_RELEASE_NUMBER]
		title = game[GAME_TITLE]
		region = game[GAME_LOCATION_INDEX]
		crc = game[GAME_ROM_CRC]
		flag = self.flags[countries_short.keys().index(region)]

		# Get the games_checks checkbuttons status
		if use_threads:
			gdk.threads_enter()
		check_ok_active = self.games_check_ok_checkbutton.get_active()
		check_no_active = self.games_check_no_checkbutton.get_active()
		check_convert_active = self.games_check_convert_checkbutton.get_active()
		if use_threads:
			gdk.threads_leave()
		
		if self.checksums[crc] == None: # we dont have the game
			returnvalue = CHECKS_NO
			if anyway or check_no_active:
				check = self.checks[CHECKS_NO]
				self.gamesnumber_not_available += 1
			else:
				return returnvalue
		else: # we have the game
			disk_zip_filename = self.checksums[crc].split(os.sep)
			disk_zip_filename = disk_zip_filename[len(disk_zip_filename) - 1]
			db_zip_filename = game[GAME_FILENAME] + ".zip"
			nds_filename = game[GAME_FILENAME] + ".nds"
			if disk_zip_filename == db_zip_filename and get_nds_filename_from_zip(self.checksums[crc]) == nds_filename:
				# game archive is good
				returnvalue = CHECKS_YES
				check = self.checks[CHECKS_YES]
				if anyway or check_ok_active:
					self.gamesnumber_available += 1
				else:
					return returnvalue
			else: # archive to rebuild
				returnvalue = CHECKS_CONVERT
				check = self.checks[CHECKS_CONVERT]
				if anyway or check_convert_active:
					self.gamesnumber_fixable += 1
				else:
					return returnvalue
		
		if use_threads:
			gdk.threads_enter()
		self.list_treeview_model.insert_before(insert_before_iter, (check, flag, relnum, title))
		if use_threads:
			gdk.threads_leave()
		self.gamesnumber_total += 1
		return returnvalue
	
	def __update_list(self, games, anyway = False, rebuild_dict = False, use_threads = False):
		"""
		List games fro 'games' list in treeview.
		If 'anyway' is True add the game to the list even if it should be filtered.
		If 'rebuild_dict' is True, rebuild dictionary containing games to rebuild.
		"""
		if self.quitting:
			return
		
		if rebuild_dict:
			# delete old dictionary
			self.games_to_rebuild = {}
			
		if use_threads:
			gdk.threads_enter()
		self.list_treeview_model.clear()
		if use_threads:
			gdk.threads_leave()
		
		self.gamesnumber_total = 0
		self.gamesnumber_available = 0
		self.gamesnumber_fixable = 0
		self.gamesnumber_not_available = 0
		
		for game in reversed(games):
			if self.quitting:
				return
			check = self.__add_game_to_list(game, anyway = anyway, use_threads = use_threads)
			if check == CHECKS_CONVERT and rebuild_dict:
				# add game to dictionary
				fullinfo = game[GAME_FULLINFO]
				filename = game[GAME_FILENAME]
				crc = game[GAME_ROM_CRC]
				relnum = game[GAME_RELEASE_NUMBER]
				self.games_to_rebuild[fullinfo] = (filename, self.checksums[crc], relnum)
				
		if use_threads:
			gdk.threads_enter()
		self.update_list_game_label()
		if use_threads:
			gdk.threads_leave()
	
	def __filter(self, dirty_list = False):
		"""
		If 'dirty_list' is False, rebuild list according to filters.
		If 'dirty_list is True, just filter the list by removing the games that should be already filtered. 
		"""
		if self.quitting:
			return
		if dirty_list:
			## Remove alien games (according to games_checks checkbuttons) from the games list
			# Get checkbuttons status
			check_ok = self.games_check_ok_checkbutton.get_active()
			check_no = self.games_check_no_checkbutton.get_active()
			check_convert = self.games_check_convert_checkbutton.get_active()
			# Get the list
			model = self.list_treeview_model
			iter = model.get_iter_first()
			while iter != None:
				iter_next = model.iter_next(iter)
				check = model.get_value(iter, TVC_CHECK)
				if check == self.checks[CHECKS_YES] and check_ok == True:
					pass
				elif check == self.checks[CHECKS_NO] and check_no == True:
					pass
				elif check == self.checks[CHECKS_CONVERT] and check_convert == True:
					pass
				else: # games has to be removed
					model.remove(iter)
					self.gamesnumber_total -= 1
					if check == self.checks[CHECKS_YES]:
						self.gamesnumber_available -= 1
					elif check == self.checks[CHECKS_NO]:
						self.gamesnumber_not_available -= 1
					else: # CHECKS_CONVERT
						self.gamesnumber_fixable -= 1
					self.update_list_game_label()
				iter = iter_next
			# Games list is no more dirty
			self.dirty_gameslist = False
		else: # Games list is not dirty
			# Rebuild the list
			string = self.filter_name_entry.get_text()
			location_iter = self.filter_location_combobox.get_active_iter()
			location = self.filter_location_model.get_value(location_iter, 1)
			language_iter = self.filter_language_combobox.get_active_iter()
			language = self.filter_language_model.get_value(language_iter, 1)
			size_iter = self.filter_size_combobox.get_active_iter()
			size = self.filter_size_model.get_value(size_iter, 1)
			# Remove list from treeview for updating
			self.list_treeview.set_model(None)
			try:
				self.__update_list(self.db.filter_by(string, location, language, size))
			except:
				# Open a new database connection
				self.open_db()
				self.__update_list(self.db.filter_by(string, location, language, size))
		self.show_review_toolbutton.set_sensitive(False)
		self.show_review_menuitem.set_sensitive(False)
		# Set the model back to treeview
		self.list_treeview.set_model(self.list_treeview_model)
		# Restore previous selection
		self.set_previous_treeview_cursor()
	
	def __hide_infos(self):
		""" Hide game's info and disable review buttons """
		if self.quitting:
			return
		self.images_hbox.hide()
		self.info_title_label.hide()
		self.info_label_vbox.hide()
		self.images_window.hide()
		self.show_review_toolbutton.set_sensitive(False)
		self.show_review_menuitem.set_sensitive(False)
	
	def __show_infos(self):
		""" Show game's info and enable review buttons"""
		if self.quitting:
			return
		self.images_hbox.show()
		self.info_title_label.show()
		self.info_label_vbox.show()
		self.show_review_toolbutton.set_sensitive(True)
		self.show_review_menuitem.set_sensitive(True)
	
	### Callback functions
	
	def on_main_window_delete_event(self, window, event):
		""" Exit Application """
		if self.quitting: # we are already quitting
			return True
		self.quit()
		return True
	
	def on_statusicon_activate(self, statusicon):
		""" Hide/Restore the application in/from systray """
		if self.quitting:
			return
		if self.main_window_visible:
			self.main_window.hide()
			self.images_window.hide()
			self.toggle_main_window_menuitem.set_image(gtk.image_new_from_stock(gtk.STOCK_FULLSCREEN, gtk.ICON_SIZE_MENU))
			self.toggle_main_window_menuitem.get_children()[0].set_label(_("Show"))
			self.toggle_main_window_menuitem.set_tooltip_text(_("Show main window."))
			self.main_window_visible = False
		else:
			self.main_window.show()
			self.toggle_main_window_menuitem.set_image(gtk.image_new_from_stock(gtk.STOCK_LEAVE_FULLSCREEN, gtk.ICON_SIZE_MENU))
			self.toggle_main_window_menuitem.get_children()[0].set_label(_("Hide"))
			self.toggle_main_window_menuitem.set_tooltip_text(_("Hide main window."))
			self.main_window_visible = True
	
	def on_statusicon_toggle_main_window_activate(self, widget):
		""" Hide/Restore the application in/from systray """
		self.on_statusicon_activate(self.statusicon)
	
	def on_statusicon_dat_update_activate(self, widget):
		""" Start DAT Update """
		self.on_dat_update_toolbutton_clicked(self.dat_update_toolbutton)
	
	def on_statusicon_images_download_activate(self, widget):
		""" Start/Stop downloading of all images """
		self.on_images_download_toolbutton_clicked(self.images_download_toolbutton)
	
	def on_statusicon_rescan_roms_archives_activate(self, widget):
		""" Start rescan of roms archives """
		self.on_rescan_roms_archives_toolbutton_clicked(self.rescan_roms_archives_toolbutton)
	
	def on_statusicon_rebuild_roms_archives_activate(self, widget):
		""" Start/Stop rebuilding of roms archives """
		self.on_rebuild_roms_archives_toolbutton_clicked(self.rebuild_roms_archives_toolbutton)
	
	def on_statusicon_show_review_activate(self, widget):
		""" Show reviews for the current selected game """
		self.on_show_review_toolbutton_clicked(self.show_review_toolbutton)
	
	def on_statusicon_options_activate(self, widget):
		""" Show the options dialog """
		self.on_options_toolbutton_clicked(self.options_toolbutton)
	
	def on_statusicon_about_activate(self, widget):
		""" Show the info dialog """
		self.on_about_toolbutton_clicked(self.about_toolbutton)
	
	def on_statusicon_quit_activate(self, widget, data = None):
		""" Exit Application """
		self.quit()
	
	def on_statusicon_popup_menu(self, widget, button, time, data = None):
		""" Show the statusicon popup menu """
		if self.quitting:
			return
		if button == 3:
			if data:
				data.show_all()
				data.popup(None, None, None, button, time)
		pass
	
	def on_statusbar_text_pushed(self, statusbar, context_id, text):
		""" When text is pushed in statusbar, update statusicon tooltip """
		self.statusicon.set_tooltip(text)
	
	def on_list_treeview_selection_changed(self, selection):
		""" Show game info for the current selected game """
		if self.quitting:
			return

		# Disable previous info_title_eventbox signal
		if self.ite_sid != None:
			self.info_title_eventbox.disconnect(self.ite_sid)
			self.ite_sid = None
		
		# If more games are selected, return
		if selection.count_selected_rows() > 1:
			# There is no more a previous selected game
			self.previous_selection_release_number = None
			self.set_previous_treeview_cursor()
			return
		
		model, paths = selection.get_selected_rows()
		try:
			iter = model.get_iter(paths[0])
		except:
			return # treeview is changing
		
		try:
			relnum = model.get_value(iter, TVC_RELEASE_NUMBER)
		except:
			return # model is empty
		
		try:
			game = self.db.get_game(relnum)
		except:
			self.open_db()
			game = self.db.get_game(relnum)
		
		# Show images if available, or else download them
		img1 = game[GAME_IMG1_LOCAL_PATH]
		img2 = game[GAME_IMG2_LOCAL_PATH]
		
		if os.path.exists(img1) and os.path.exists(img2):
			try:
				pixbuf1 = gdk.pixbuf_new_from_file(img1)
				pixbuf2 = gdk.pixbuf_new_from_file(img2)
				if self.images_resize_rate != 1: # resize images and enable images_window
					self.images_window_image1.set_from_file(img1)
					self.images_window_image2.set_from_file(img2)
					pixbuf1_new_width = int(pixbuf1.get_width() * self.images_resize_rate)
					pixbuf1_new_height = int(pixbuf1.get_height() * self.images_resize_rate)
					pixbuf1 = pixbuf1.scale_simple(pixbuf1_new_width, pixbuf1_new_height, gdk.INTERP_BILINEAR)
					pixbuf2_new_width = int(pixbuf2.get_width() * self.images_resize_rate)
					pixbuf2_new_height = int(pixbuf2.get_height() * self.images_resize_rate)
					pixbuf2 = pixbuf2.scale_simple(pixbuf2_new_width, pixbuf2_new_height, gdk.INTERP_BILINEAR)
					# resize images frames too
					self.image1_frame.set_size_request(pixbuf1.get_width(), pixbuf1.get_height())
					self.image2_frame.set_size_request(pixbuf2.get_width(), pixbuf2.get_height())
				self.image1.set_from_pixbuf(pixbuf1)
				self.image2.set_from_pixbuf(pixbuf2)
			except:
				# Probably we were still downloading image files when we tried to load them.
				# In other words, file exists but it's not complete yet (ie, corrupt).
				# Well, ignore the problem.
				pass				
		else: # Images do not exist, download them
			self.image1.clear()
			self.image2.clear()
			if self.images_resize_rate != 1:
				self.images_window_image1.clear()
				self.images_window_image2.clear()
			thread = ImagesDownloader(self, game)
			self.threads.append(thread)
			thread.start()
		
		# Connect signal on images_eventbox in needed
		if self.images_resize_rate != 1:
			self.images_eventbox.connect("button-press-event", self.toggle_images_window, img1, img2)
			
		# Search for duplicates
		duplicates_fullinfo = []
		duplicates_relnum = []
		id = game[GAME_DUPLICATE_ID]
		relnum = game[GAME_RELEASE_NUMBER]
		if id != 0: # Games with id == 0 have no duplicates
			games = self.db.get_all_games()
			for g in games:
				if g[GAME_DUPLICATE_ID] == id and g[GAME_RELEASE_NUMBER] != relnum:
					duplicates_fullinfo.append(g[GAME_FULLINFO])
					duplicates_relnum.append(g[GAME_RELEASE_NUMBER])
		
		# Add duplicates to info_title_label tooltip
		if len(duplicates_fullinfo) != 0:
			text = _("Duplicates:")
			for d in reversed(duplicates_fullinfo):
				text += "\n" + d
				self.info_title_label.set_tooltip_text(text)
		else:
			self.info_title_label.set_tooltip_text(_("No duplicates"))
		
		# Enable info_title_eventbox to catch button presses in order to cycle duplicates
		self.ite_sid = self.info_title_eventbox.connect("button-press-event",
													    self.on_info_title_eventbox_button_press_event,
													    relnum, duplicates_relnum)
		
		# Show informations
		title = game[GAME_FULLINFO].replace("&", "&amp;")
		if self.images_resize_rate != 1: # Use a normal size for title on small screens
			self.info_title_label.set_markup("<span weight=\"bold\">" + title + "</span>")
		else:
			self.info_title_label.set_markup("<span size=\"x-large\" weight=\"bold\">" + title + "</span>")
		self.info_save_label.set_text(game[GAME_SAVE_TYPE])
		size = game[GAME_ROM_SIZE] / 1048576
		self.info_size_label.set_text(str(size) + " MB")
		self.info_publisher_label.set_text(game[GAME_PUBLISHER])
		self.info_location_label.set_text(_(game[GAME_LOCATION]))
		self.info_source_label.set_text(game[GAME_SOURCE_ROM])
		language = ""
		for lang in game[GAME_LANGUAGE].split(" - "):
			if len(language) != 0:
				language += " - "
			language += _(lang)
		self.info_language_label.set_text(language)
		self.info_crc_label.set_text(game[GAME_ROM_CRC])
		self.info_comment_label.set_text(game[GAME_COMMENT])
		
		# Enable review buttons
		self.show_review_toolbutton.set_sensitive(True)
		self.show_review_menuitem.set_sensitive(True)
		
		# This game now is the previous selected game
		self.previous_selection_release_number = game[GAME_RELEASE_NUMBER]
		self.__show_infos()
	
	def on_info_title_eventbox_button_press_event(self, widget, event, current, duplicates):
		""" Select in treeview the next game duplicate """
		if self.quitting or event.button != 1 or len(duplicates) == 0:
			# Nothing to do
			return

		# search for the next game to show
		next = 0
		for d in duplicates:
			# Take the max from the lessers
			if d > next and d < current:
				next = d
		if next == 0:
			# No max in the lessers, take the max from the greaters
			for d in duplicates:
				if d > next and d > current:
					next = d
		if next == 0: # Nothing to do then...
			return
		
		iter = self.list_treeview_model.get_iter_first()
		while self.list_treeview_model.get_value(iter, TVC_RELEASE_NUMBER) != next:
			next_iter = self.list_treeview_model.iter_next(iter)
			if next_iter == None or self.list_treeview_model.get_value(next_iter, TVC_RELEASE_NUMBER) < next:
				# Not found in current treeview.
				# Then, add the game we need to the treeview
				try:
					game = self.db.get_game(next)
				except:
					self.open_db()
					game = self.db.get_game(next)
				# Insert game into the model, the next cycle will find the iter we are searching for
				self.__add_game_to_list(game, insert_before_iter = next_iter, anyway = True)
				# Update statistic labels
				self.update_list_game_label()
			else: # Not found yet
				iter = next_iter
		
		# Finally, select the next game in the treeview
		path = self.list_treeview_model.get_path(iter)
		self.list_treeview.set_cursor(path)
	
	def on_list_treeview_button_press_event(self, treeview, event):
		""" Open popup menu in treeview when mouse button 3 is pressed """
		if self.quitting:
			return True
		if event.button == 3:
			x = int(event.x)
			y = int(event.y)
			# Figure out which item has been clicked on
			try:
				path = treeview.get_path_at_pos(x, y)[0]
			except:
				return
			# Get selection
			selection = treeview.get_selection()
			# Get selected paths
			model, paths = selection.get_selected_rows()
			
			# Check if clicked item is in selected paths.
			# If not, move cursor on it and create a new 'paths'.
			if not path in paths:
				treeview.set_cursor(path)
				paths = [path, ]
			
			check_yes = False
			check_convert = False
			
			# get selected games check status in order to check what options we can enable
			for p in paths:
				iter = model.get_iter(p)
				if iter == None:
					return
				check = model.get_value(iter, TVC_CHECK)
				if check == self.checks[CHECKS_YES]:
					check_yes = True
				elif check == self.checks[CHECKS_CONVERT]:
					check_convert = True
			
			# Let's see what options we can enable
			if check_yes and check_convert:
				self.list_treeview_popup_extract_menuitem.set_sensitive(True)
				self.list_treeview_popup_extractin_menuitem.set_sensitive(True)
				self.list_treeview_popup_rebuildarchive_menuitem.set_sensitive(True)
			if check_yes and not check_convert:
				self.list_treeview_popup_extract_menuitem.set_sensitive(True)
				self.list_treeview_popup_extractin_menuitem.set_sensitive(True)
				self.list_treeview_popup_rebuildarchive_menuitem.set_sensitive(False)
			if not check_yes and check_convert:
				self.list_treeview_popup_extract_menuitem.set_sensitive(False)
				self.list_treeview_popup_extractin_menuitem.set_sensitive(False)
				self.list_treeview_popup_rebuildarchive_menuitem.set_sensitive(True)
			if not check_yes and not check_convert:
				self.list_treeview_popup_extract_menuitem.set_sensitive(False)
				self.list_treeview_popup_extractin_menuitem.set_sensitive(False)
				self.list_treeview_popup_rebuildarchive_menuitem.set_sensitive(False)

			# Check if default extract directory exists and we have write permissions in it.
			# If not, disable the "Extract" option. 
			default_extract_directory = config.get_option("default_extract_directory")
			if not os.path.exists(default_extract_directory) or not os.access(default_extract_directory, os.W_OK):
				self.list_treeview_popup_extract_menuitem.set_sensitive(False)
			
			# If we are already rebuilding archives, we can't start another process
			for thread in self.threads:
				if thread.isAlive() and thread.getName() == "RomArchivesRebuild":
					self.list_treeview_popup_rebuildarchive_menuitem.set_sensitive(False)
					break
			
			# If we are already extracting archives, it's better if we avoid to start a new extract process
			for thread in self.threads:
				if thread.isAlive() and thread.getName() == "RomArchivesExtract":
					self.list_treeview_popup_extract_menuitem.set_sensitive(False)
					self.list_treeview_popup_extractin_menuitem.set_sensitive(False)
					break
			
			# Finally show the popup menu
			self.list_treeview_popup_menu.popup(None, None, None, event.button, event.time)			
			return True
	
	def on_list_treeview_popup_extract_menuitem_activate(self, button):
		""" Extract selected games in the default extract directory """
		target = config.get_option("default_extract_directory")
		self.on_list_treeview_popup_extractin_menuitem_activate(button, target = target)
	
	def on_list_treeview_popup_extractin_menuitem_activate(self, button, target = None):
		"""
		Extract selected games in 'target'.
		If 'target' is None, open a filechooserdialog to let the user select
		the target directory.
		"""
		if self.quitting:
			return

		dict = {} # games to extract, in format { fullinfo : zipfile }
		
		selection = self.list_treeview.get_selection()
		model, paths = selection.get_selected_rows()
		
		# Add all selected games with CHECKS_YES status to games dictionary
		for path in paths:
			iter = model.get_iter(path)
			if model.get_value(iter, TVC_CHECK) != self.checks[CHECKS_YES]: # skip game
				continue
			relnum = model.get_value(iter, TVC_RELEASE_NUMBER)
			try:
				game = self.db.get_game(relnum)
			except:
				self.open_db()
				game = self.db.get_game(relnum)
			# Get zipfile
			zipfile = self.checksums[game[GAME_ROM_CRC]]
			# Add game to games dictionary
			dict[game[GAME_FULLINFO]] = zipfile
		
		if target == None:
			# Open a filechooserdialog to select the target directory
			fcd = gtk.FileChooserDialog(_("Select destination directory"),
									    self.main_window,
									    gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
									    ("gtk-cancel", gtk.RESPONSE_CANCEL, "gtk-ok", gtk.RESPONSE_ACCEPT))
			fcd.set_current_folder(os.path.expandvars("$HOME"))
			if fcd.run() == gtk.RESPONSE_ACCEPT:
				target = fcd.get_current_folder()
			fcd.destroy()
			if target == None:
				return
		
		# Check if we want and we can trim
		trim = None
		if config.get_option("trim_roms"): # we want to trim, check if we can
			for path in os.path.expandvars("$PATH").split(":"):
				temp = os.path.join(path, "trim")
				if os.path.exists(temp):
					trim = temp
					break
		# if here trim is None, we don't want or we can't trim.
		trim_temp_path = config.get_option("trim_temp_path")
		show_trim_details = config.get_option("show_trim_details")
		rae = RomArchivesExtract(self, dict, target, trim, trim_temp_path, show_trim_details)
		self.threads.append(rae)
		rae.start()

	def on_list_treeview_popup_extract_stop_menuitem_activate(self, button):
		""" Stop the currenct extraction process """
		self.update_statusbar("RomArchivesExtract", _("Waiting while the current extraction is completed..."))
		for thread in self.threads:
			if thread.isAlive() and thread.getName() == "RomArchivesExtract":
				thread.stop()
				break
		self.list_treeview_popup_extract_stop_menuitem.set_sensitive(False)
	
	def on_list_treeview_popup_rebuildarchive_menuitem_activate(self, button):
		""" Rebuild archives for selected games. """
		if self.quitting:
			return
		
		dict = {} # games to extract, in format { fullinfo : (filename, fileondisk, relnum) }
		
		selection = self.list_treeview.get_selection()
		model, paths = selection.get_selected_rows()
		
		# Add all selected games with CHECKS_CONVERT status to games dictionary
		for path in paths:
			iter = model.get_iter(path)
			if model.get_value(iter, TVC_CHECK) != self.checks[CHECKS_CONVERT]: # skip game
				continue
			relnum = model.get_value(iter, TVC_RELEASE_NUMBER)
			try:
				game = self.db.get_game(relnum)
			except:
				self.open_db()
				game = self.db.get_game(relnum)
			dict[game[GAME_FULLINFO]] = (game[GAME_FILENAME], self.checksums[game[GAME_ROM_CRC]], relnum)
		
		self.on_rebuild_roms_archives_toolbutton_clicked(self.rebuild_roms_archives_toolbutton, dict = dict)
			
	def on_show_review_toolbutton_clicked(self, button):
		"""
		Open the web browser to show reviews for the current selected game.
		If more games are selected, do nothing.
		"""
		if self.quitting:
			return
		selection = self.list_treeview.get_selection()
		if selection.count_selected_rows() > 1: # Multiple selected games, nothing to do
			return
		model, paths = selection.get_selected_rows()
		iter = model.get_iter(paths[0])
		relnum = str(model.get_value(iter, TVC_RELEASE_NUMBER))
		title = model.get_value(iter, TVC_TITLE)
		title = title.replace("&", " ")
		title = title.replace("-", " ")
		url = config.get_option("review_url").replace("{TITLE}", title).replace("{RELNUM}", relnum)
		import webbrowser
		webbrowser.open(url)
	
	def on_dat_update_toolbutton_clicked(self, button):
		""" Check if DAT can be updated. If so, update it. """
		if self.quitting:
			return
		try:
			info = self.db.get_info()
		except:
			self.open_db()
			info = self.db.get_info()
		
		buttons = [] # buttons that need to be disabled while updating
		buttons.append(self.dat_update_toolbutton)
		buttons.append(self.dat_update_menuitem)
		
		# Check if we have to rescan roms archives after update
		rescan = config.get_option("autoscan_archives_at_datupdate")		
		
		thread = DatUpdater(self, self.threads, buttons, info[INFO_DAT_VERSION], info[INFO_DAT_VERSION_URL], rescan)
		self.threads.append(thread)
		thread.start()
	
	def on_images_download_toolbutton_clicked(self, button):
		""" Start/Stop all images download """
		if self.quitting:
			return
		try:
			games_number = self.db.get_games_number()
		except:
			self.open_db()
			games_number = self.db.get_games_number()
		
		if button.get_stock_id() == gtk.STOCK_JUMP_TO: # Let's start download
			if games_number == 0:
				return
			try:
				aid = AllImagesDownloader(self, self.db.get_all_games())
			except:
				self.open_db()
				aid = AllImagesDownloader(self, self.db.get_all_games())
			self.threads.append(aid)
			aid.start()
		else: # stop download
			for thread in self.threads:
				if thread.isAlive() and thread.getName() == "AllImagesDownloader":
					thread.stop()
					break
	
	def on_rescan_roms_archives_toolbutton_clicked(self, button, confirm = True):
		"""
		Rescan for roms archives on disk.
		If previously roms archives were already scanned, ask for confirmation.
		"""
		if self.quitting:
			return
		if confirm and self.archives_already_scanned:
			message = _("Rescan roms archives and rebuild games list?")
			if self.show_okcancel_question_dialog(message) == False:
				return
		self.previous_selection_release_number = None
		rar = RomArchivesRescan(self)
		self.threads.append(rar)
		rar.start()
	
	def on_rebuild_roms_archives_toolbutton_clicked(self, button, dict = None):
		"""
		Start rebuilding of archives for games listed in 'dict'.
		If 'dict' is None, rebuild archives for games listed in global
		variable 'self.games_to_rebuild' (ie, all rebuildable games).
		"""
		if self.quitting:
			return
		if button.get_stock_id() == gtk.STOCK_CONVERT: # Start rebuilding
			widgets = [] # widgets that need to be disabled while updating
			widgets.append(self.dat_update_toolbutton)
			widgets.append(self.dat_update_menuitem)
			widgets.append(self.rescan_roms_archives_toolbutton)
			widgets.append(self.rescan_roms_archives_menuitem)
			
			if dict == None:
				dict = self.games_to_rebuild

			rar = RomArchivesRebuild(self, widgets, dict)
			self.threads.append(rar)
			rar.start()
		else: # Stop rebuilding
			self.update_statusbar("RomArchivesRebuild", _("Waiting while the current archive rebuild is completed..."))
			self.rebuild_roms_archives_toolbutton.set_sensitive(False)
			self.rebuild_roms_archives_menuitem.set_sensitive(False)
			for thread in self.threads:
				if thread.isAlive() and thread.getName() == "RomArchivesRebuild":
					thread.stop()
					break
	
	def on_filter_triggered(self, widget):
		""" Filter list """
		if self.quitting:
			return
		self.dirty_gameslist = False
		self.__filter()
	
	def on_filter_clear_button_clicked(self, button):
		"""
		If global variable 'self.dirty_gameslist' is False and filters are not cleared,
		clear all filters.
		If global variable 'self.dirty_gamelist' is False and filters are already cleared,
		just unselect the current selected games.
		If 'self.dirty_gamelist' is True, just remove games that should be already filter
		from the games list.
		"""
		if self.quitting:
			return
		filter = 0
		if self.filter_name_entry.get_text() != "":
			filter = 1
		if self.filter_location_combobox.get_active() != 0:
			filter = 2
		if self.filter_language_combobox.get_active() != 0:
			filter = 3
		if self.filter_size_combobox.get_active() != 0:
			filter = 4
			
		if self.dirty_gameslist:
			self.__filter(dirty_list = True)
			return
		
		if filter == 0:
			# Just clear current selection in treeview and hide infos
			self.list_treeview.get_selection().unselect_all()
			self.previous_selection_release_number = None
			self.set_previous_treeview_cursor()
		elif filter == 1:
			self.filter_location_combobox.handler_block(self.flocc_sid)
			self.filter_language_combobox.handler_block(self.flanc_sid)
			self.filter_size_combobox.handler_block(self.fsc_sid)
			self.filter_name_entry.set_text("")
			self.filter_location_combobox.set_active(0)
			self.filter_language_combobox.set_active(0)
			self.filter_size_combobox.set_active(0)
			self.filter_location_combobox.handler_unblock(self.flocc_sid)
			self.filter_language_combobox.handler_unblock(self.flanc_sid)
			self.filter_size_combobox.handler_unblock(self.fsc_sid)
		elif filter == 2:
			self.filter_name_entry.handler_block(self.fne_sid)
			self.filter_language_combobox.handler_block(self.flanc_sid)
			self.filter_size_combobox.handler_block(self.fsc_sid)
			self.filter_name_entry.set_text("")
			self.filter_location_combobox.set_active(0)
			self.filter_language_combobox.set_active(0)
			self.filter_size_combobox.set_active(0)
			self.filter_name_entry.handler_unblock(self.fne_sid)
			self.filter_language_combobox.handler_unblock(self.flanc_sid)
			self.filter_size_combobox.handler_unblock(self.fsc_sid)
		elif filter == 3:
			self.filter_name_entry.handler_block(self.fne_sid)
			self.filter_location_combobox.handler_block(self.flocc_sid)
			self.filter_size_combobox.handler_block(self.fsc_sid)
			self.filter_name_entry.set_text("")
			self.filter_location_combobox.set_active(0)
			self.filter_language_combobox.set_active(0)
			self.filter_size_combobox.set_active(0)
			self.filter_name_entry.handler_unblock(self.fne_sid)
			self.filter_location_combobox.handler_unblock(self.flocc_sid)
			self.filter_size_combobox.handler_unblock(self.fsc_sid)
		else:
			self.filter_name_entry.handler_block(self.fne_sid)
			self.filter_location_combobox.handler_block(self.flocc_sid)
			self.filter_language_combobox.handler_block(self.flanc_sid)
			self.filter_name_entry.set_text("")
			self.filter_location_combobox.set_active(0)
			self.filter_language_combobox.set_active(0)
			self.filter_size_combobox.set_active(0)
			self.filter_name_entry.handler_unblock(self.fne_sid)
			self.filter_location_combobox.handler_unblock(self.flocc_sid)
			self.filter_language_combobox.handler_unblock(self.flanc_sid)
	
	def on_games_check_ok_checkbutton_toggled(self, widget):
		""" Set/unset filter of games with CHECKS_OK status  """
		config.set_option("show_available_games", widget.get_active())
		self.__filter()
	
	def on_games_check_no_checkbutton_toggled(self, widget):
		""" Set/unset filter of games with CHECKS_NO status  """
		config.set_option("show_not_available_games", widget.get_active())
		self.__filter()
	
	def on_games_check_convert_checkbutton_toggled(self, widget):
		""" Set/unset filter of games with CHECKS_CONVERT status  """
		config.set_option("show_rebuildable_games", widget.get_active())
		self.__filter()
	
	def on_options_trim_roms_checkbutton_toggled(self, widget):
		"""	Enable/disable all the other options depending on 'options_trim_roms_checkbutton' """
		if not self.options_trim_roms_checkbutton.get_property("sensitive"):
			return
		if self.options_trim_roms_checkbutton.get_active():
			self.options_trim_roms_details_checkbutton.set_sensitive(True)
		else:
			self.options_trim_roms_details_checkbutton.set_sensitive(False)
	
	def on_trim_details_window_delete_event(self, window, event):
		""" Close the trim details window and clear the textbuffer """
		if self.quitting:
		  return True
		self.trim_details_textbuffer.set_text("")
		self.trim_details_window.hide()
		return True
	
	def on_options_toolbutton_clicked(self, menuitem):
		""" Open the options dialog """
		if self.quitting:
			return
		self.options_check_images_crc_checkbutton.set_active(config.get_option("check_images_crc"))
		self.options_autoscan_archives_at_start_checkbutton.set_active(config.get_option("autoscan_archives_at_start"))
		self.options_autoscan_archives_at_datupdate_checkbutton.set_active(config.get_option("autoscan_archives_at_datupdate"))
		self.options_trim_roms_checkbutton.set_active(config.get_option("trim_roms"))
		self.options_trim_roms_details_checkbutton.set_active(config.get_option("show_trim_details"))
		
		# Check if 'trim' in installed and disable/enable options as needed
		trim = None
		for path in os.path.expandvars("$PATH").split(":"):
			temp = os.path.join(path, "trim")
			if os.path.exists(temp):
				trim = temp
				break
		if trim == None: # 'trim' not available
			self.options_trim_roms_checkbutton.set_sensitive(False)
			self.options_trim_roms_details_checkbutton.set_sensitive(False)
		else: # 'trim' available
			self.options_trim_roms_checkbutton.set_sensitive(True)
			self.options_trim_roms_details_checkbutton.set_sensitive(True) 
		
		roms_path = config.get_option("roms_path")
		if not os.path.exists(roms_path):
			self.show_info_dialog(_("Current 'Roms' path does not exist.\nThe default path will be used."))
			roms_path = config.get_option_default("roms_path")
		self.options_roms_path_filechooserbutton.set_current_folder(roms_path)
		
		unknown_roms_path = config.get_option("unknown_roms_path")
		if not os.path.exists(unknown_roms_path):
			self.show_info_dialog(_("Current 'Unknown roms' path does not exist.\nThe default path will be used."))
			unknown_roms_path = config.get_option_default("unknown_roms_path")
		self.options_unknown_roms_path_filechooserbutton.set_current_folder(unknown_roms_path)
		
		new_roms_path = config.get_option("new_roms_path")
		if not os.path.exists(new_roms_path):
			self.show_info_dialog(_("Current 'New roms' path does not exist.\nThe default path will be used."))
			new_roms_path = config.get_option_default("new_roms_path")
		self.options_new_roms_path_filechooserbutton.set_current_folder(new_roms_path)
		
		images_path = config.get_option("images_path")
		if not os.path.exists(images_path):
			self.show_info_dialog(_("Current 'Images' path does not exist.\nThe default path will be used."))
			images_path = config.get_option_default("images_path")
		self.options_images_path_filechooserbutton.set_current_folder(images_path)
		
		extractin_path = config.get_option("default_extract_directory")
		if os.path.exists(extractin_path) and os.access(extractin_path, os.W_OK):
			self.options_extractin_path_enable_button.hide()
			self.options_extractin_path_hbox.show()
		else:
			self.options_extractin_path_enable_button.show()
			self.options_extractin_path_hbox.hide()
			extractin_path = config.get_option_default("default_extract_directory")
		self.options_extractin_path_filechooserbutton.set_current_folder(extractin_path)			
		
		self.options_review_url_entry.set_text(config.get_option("review_url"))
				
		self.options_toolbutton.set_sensitive(False)
		self.options_menuitem.set_sensitive(False)
		self.options_dialog.show()
	
	def on_options_dialog_response(self, dialog, response_id):
		""" Check if options in options dialog are valid, then save them in 'config' """
		if self.quitting:
			return
		if response_id == 0: # options dialog closed clicking on 'OK'
			# Get new paths
			unknown_roms_path_new = self.options_unknown_roms_path_filechooserbutton.get_current_folder()
			roms_path_new = self.options_roms_path_filechooserbutton.get_current_folder()
			new_roms_path_new = self.options_new_roms_path_filechooserbutton.get_current_folder()
			images_path_new = self.options_images_path_filechooserbutton.get_current_folder()
			extractin_path_new = None
			if self.options_extractin_path_hbox.get_property("visible"):
				extractin_path_new = self.options_extractin_path_filechooserbutton.get_current_folder()
			# Check if new paths are ok
			if roms_path_new == WORK_DIR:
			 	message = _("'DsRomsManager' working directory has been selected as 'Roms' path, but it can't be used.")
			 	message += _("\n\nThe 'Roms' path will be restored to its default value.")
				roms_path_new = config.get_option_default("roms_path")
				self.show_info_dialog(message)
			if unknown_roms_path_new == WORK_DIR:
				message = _("'DsRomsManager' working directory has been selected as 'Unknown roms' path, but it can't be used.")
				message += _("\n\nThe 'Unknown roms' path will be restored to its default value.")
				unknown_roms_path_new = config.get_option_default("unknown_roms_path")
				self.show_info_dialog(message)			 	 
			if new_roms_path_new == WORK_DIR:
				message = _("'DsRomsManager' working directory has been selected as 'New roms' path, but it can't be used.")
				message += _("\n\nThe 'New roms' path will be restored to its default value.")
				new_roms_path_new = config.get_option_default("new_roms_path")
				self.show_info_dialog(message)
			if unknown_roms_path_new == roms_path_new or unknown_roms_path_new == new_roms_path_new:
				message = _("'Unknown roms' path can't be the same as 'Roms' or 'New roms' paths.")
				message += _("\n\nSelect a different path.")
				self.show_info_dialog(message)
				return False # Do not close options dialog
			if images_path_new == WORK_DIR:
			 	message = _("'DsRomsManager' working directory has been selected as 'Images' path, but it can't be used.")
			 	message += _("\n\nThe 'Images' path will be restored to its default value.")
				images_path_new = config.get_option_default("images_path")
				self.show_info_dialog(message)
			if images_path_new == roms_path_new:
				message = _("'Images' path can't be the same as 'Roms' path.")
				message += _("\n\nSelect a different path.")
				self.show_info_dialog(message)
				return False # Do not close options dialog
			if extractin_path_new != None and not os.access(extractin_path_new, os.W_OK):
				message = _("Write permissions are not granted for the current 'Extract in' path.")
				message += _("\n\nSelect a different path.")
				self.show_info_dialog(message)
				return False # Do not close options dialog
			# Get old roms paths
			roms_path_old = config.get_option("roms_path")
			unknown_roms_path_old = config.get_option("unknown_roms_path")
			new_roms_path_old = config.get_option("new_roms_path")
			# Check if roms paths have been changed
			romspaths_changed = False
			if roms_path_old != roms_path_new:
				romspaths_changed = True
			if unknown_roms_path_old != unknown_roms_path_new:
				romspaths_changed = True
			if new_roms_path_old != new_roms_path_new:
				romspaths_changed = True
			# Save new roms paths
			config.set_option("roms_path", roms_path_new)
			config.set_option("unknown_roms_path", unknown_roms_path_new)
			config.set_option("new_roms_path", new_roms_path_new)
			# Get old images path
			images_path_old = config.get_option("images_path")
			# Check if images paths in database must be updated.
			dbupdate = False
			if images_path_old != images_path_new:
				dbupdate = True
			# Save new images path
			config.set_option("images_path", images_path_new)
			# Save extract in path
			if extractin_path_new != None:
				config.set_option("default_extract_directory", extractin_path_new)
			# Save checkbuttons status
			config.set_option("check_images_crc", self.options_check_images_crc_checkbutton.get_active())
			config.set_option("autoscan_archives_at_start", self.options_autoscan_archives_at_start_checkbutton.get_active())
			config.set_option("autoscan_archives_at_datupdate", self.options_autoscan_archives_at_datupdate_checkbutton.get_active())
			config.set_option("trim_roms", self.options_trim_roms_checkbutton.get_active())
			config.set_option("show_trim_details", self.options_trim_roms_details_checkbutton.get_active())
			# Save review_url
			text = self.options_review_url_entry.get_text()
			if len(text) != 0:
				config.set_option("review_url", text)
			else: # An empty text means 'use the default url'
				config.set_option_default("review_url")			
			# Apply changes
			if dbupdate:
				# We need to update images paths into database with the new path.
				# Stop the all images downloader thread, if it's running.
				for thread in self.threads:
					if thread.isAlive() and thread.getName() == "AllImagesDownloader":
						self.on_images_download_toolbutton_clicked(self.images_download_toolbutton)
						break
				message = _("'Images' path has changed.")
				message += _("\n\nDatabase will be updated with the new path.")
				self.show_info_dialog(message)
				# Rebuild database
				diu = DBImagesUpdater(self, images_path_new)
				self.threads.append(diu)
				diu.start()
			if romspaths_changed:
				# we need to rescan for games on disk.
				# Stop the archive rebuilding thread, if it's running.
				for thread in self.threads:
					if thread.isAlive() and thread.getName() == "RomArchivesRebuild":
						self.on_rebuild_roms_archives_toolbutton_clicked(self.rebuild_roms_archives_toolbutton)
						break
				message = _("Roms paths have changed.")
				message += _("\n\nGames list will be reloaded.")
				self.show_info_dialog(message)
				# Rescan archives
				self.on_rescan_roms_archives_toolbutton_clicked(self.rescan_roms_archives_toolbutton, confirm = False)
		# Re-enable options buttons and close dialog
		self.options_toolbutton.set_sensitive(True)
		self.options_menuitem.set_sensitive(True)
		dialog.hide()
	
	def on_options_extractin_path_enable_button_clicked(self, button):
		""" Enable the 'Extract in' path to be changed """
		self.options_extractin_path_hbox.show()
		self.options_extractin_path_enable_button.hide()
	
	def on_images_window_delete_event(self, window, event):
		""" Hide images_window """
		if self.quitting:
			return True
		window.hide()
		return True
	
	def on_options_dialog_delete_event(self, window, event):
		""" Close options dialog without saving changes to options """
		if self.quitting:
			return True
		window.hide()
		return True
	
	def on_about_toolbutton_clicked(self, button):
		""" Show the about dialog """
		if self.quitting:
			return
		self.about_dialog.run()
	
	def on_about_dialog_response(self, dialog, response_id):
		""" Hide the about dialog """
		if self.quitting:
			return
		dialog.hide()
	
	### General functions
	
	def deactivate_widgets(self, use_threads = False):
		""" Disable all widgets' sensitiveness """
		if self.quitting:
			return
		if use_threads:
			gdk.threads_enter()
		self.list_scrolledwindow.set_sensitive(False)
		self.dat_update_toolbutton.set_sensitive(False)
		self.dat_update_menuitem.set_sensitive(False)
		if self.images_download_toolbutton.get_stock_id() != gtk.STOCK_CANCEL:
			self.images_download_toolbutton.set_sensitive(False)
			self.images_download_menuitem.set_sensitive(False)
		self.rescan_roms_archives_toolbutton.set_sensitive(False)
		self.rescan_roms_archives_menuitem.set_sensitive(False)
		if self.rebuild_roms_archives_toolbutton.get_stock_id() != gtk.STOCK_CANCEL:
			self.rebuild_roms_archives_toolbutton.set_sensitive(False)
			self.rebuild_roms_archives_menuitem.set_sensitive(False)
		self.show_review_toolbutton.set_sensitive(False)
		self.show_review_menuitem.set_sensitive(False)
		self.options_toolbutton.set_sensitive(False)
		self.options_menuitem.set_sensitive(False)
		self.games_check_ok_checkbutton.set_sensitive(False)
		self.games_check_no_checkbutton.set_sensitive(False)
		self.games_check_convert_checkbutton.set_sensitive(False)
		self.info_title_eventbox.set_sensitive(False)
		self.info_label_vbox.set_sensitive(False)
		self.filter_name_entry.set_sensitive(False)
		self.filter_clear_button.set_sensitive(False)
		self.filter_location_combobox.set_sensitive(False)
		self.filter_language_combobox.set_sensitive(False)
		self.filter_size_combobox.set_sensitive(False)
		self.__hide_infos()
		if use_threads:
			gdk.threads_leave()
	
	def activate_widgets(self, use_threads = False):
		""" Enable all widgets' sensitiveness """
		if self.quitting:
			return
		if use_threads:
			gdk.threads_enter()
		self.list_scrolledwindow.set_sensitive(True)
		self.dat_update_toolbutton.set_sensitive(True)
		self.dat_update_menuitem.set_sensitive(True)
		self.images_download_toolbutton.set_sensitive(True)
		self.images_download_menuitem.set_sensitive(True)
		self.rescan_roms_archives_toolbutton.set_sensitive(True)
		self.rescan_roms_archives_menuitem.set_sensitive(True)
		if len(self.games_to_rebuild) > 0:
			self.rebuild_roms_archives_toolbutton.set_sensitive(True)
			self.rebuild_roms_archives_menuitem.set_sensitive(True)
		else:
			self.rebuild_roms_archives_toolbutton.set_sensitive(False)
			self.rebuild_roms_archives_menuitem.set_sensitive(False)
		if not self.options_dialog.get_property("visible"):
			self.options_toolbutton.set_sensitive(True)
			self.options_menuitem.set_sensitive(True)
		self.games_check_ok_checkbutton.set_sensitive(True)
		self.games_check_no_checkbutton.set_sensitive(True)
		self.games_check_convert_checkbutton.set_sensitive(True)
		self.info_title_eventbox.set_sensitive(True)
		self.info_label_vbox.set_sensitive(True)
		self.filter_name_entry.set_sensitive(True)
		self.filter_clear_button.set_sensitive(True)
		self.filter_location_combobox.set_sensitive(True)
		self.filter_language_combobox.set_sensitive(True)
		self.filter_size_combobox.set_sensitive(True)
		if use_threads:
			gdk.threads_leave()
		self.set_previous_treeview_cursor(use_threads = use_threads)
	
	def toggle_images_window(self, widget, event, img1 = None, img2 = None):
		""" When mouse button 1 is clicked, toggle images_window """
		if self.quitting or event.button != 1:
			return
		if img1 == None and img2 == None:
			self.images_window.hide()
		else:
			self.images_window.set_title(_("Images"))
			if img1 != None and os.path.exists(img1):
				self.images_window_image1.set_from_file(img1)
			else:
				self.images_window_image1.clear()
			if img2 != None and os.path.exists(img2):
				self.images_window_image2.set_from_file(img2)
			else:
				self.images_window_image2.clear()
			self.images_window.show()
	
	def show_okcancel_question_dialog(self, message, use_threads = False):
		"""
		Show a question dialog with 'OK' and 'Cancel' buttons, showing 'message'.
		Return True if 'OK' is pressed, or else return False.
		"""
		if self.quitting:
			return False
		if use_threads:
			gdk.threads_enter()
		dialog = gtk.MessageDialog(self.main_window, 0, gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK_CANCEL, message)
		response = dialog.run()
		dialog.destroy()
		if use_threads:
			gdk.threads_leave()		
		if response == gtk.RESPONSE_OK:
			return True
		else:
			return False
	
	def show_yesno_question_dialog(self, message, use_threads = False):
		"""
		Show a question dialog with 'Yes' and 'No' buttons, showing 'message'.
		Return True if 'YES' is pressed, or else return False.
		"""
		if self.quitting:
			return False
		if use_threads:
			gdk.threads_enter()
		dialog = gtk.MessageDialog(self.main_window, 0, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, message)
		response = dialog.run()
		dialog.destroy()
		if use_threads:
			gdk.threads_leave()		
		if response == gtk.RESPONSE_YES:
			return True
		else:
			return False
	
	def show_yesnoalwaysnever_question_dialog(self, message, use_threads = False):
		"""
		Show a question dialog with 'Yes', 'Yes for all', 'No', 'No for all' buttons, showing 'message'.
		Return 1 if 'Yes', 2 if 'Yes for all', 0 if 'No', -1 if 'No for all'.
		"""
		if self.quitting:
			return 0
		if use_threads:
			gdk.threads_enter()
		dialog = gtk.MessageDialog(self.main_window, 0, gtk.MESSAGE_QUESTION, gtk.BUTTONS_NONE, message)
		button = gtk.Button(_("_No to all"))
		button.set_image(gtk.image_new_from_stock(gtk.STOCK_NO, gtk.ICON_SIZE_BUTTON))
		button.set_flags(gtk.CAN_DEFAULT)
		button.show()
		dialog.add_action_widget(button, -1)
		button = gtk.Button(None, gtk.STOCK_NO)
		button.set_flags(gtk.CAN_DEFAULT)
		dialog.set_default(button)
		button.show()
		dialog.add_action_widget(button, 0)
		button = gtk.Button(_("_Yes to all"))
		button.set_image(gtk.image_new_from_stock(gtk.STOCK_YES, gtk.ICON_SIZE_BUTTON))
		button.set_flags(gtk.CAN_DEFAULT)
		button.show()
		dialog.add_action_widget(button, 2)
		button = gtk.Button(None, gtk.STOCK_YES)
		button.set_flags(gtk.CAN_DEFAULT)
		button.show()
		dialog.add_action_widget(button, 1)
		response = dialog.run()
		dialog.destroy()
		if use_threads:
			gdk.threads_leave()
		if response == gtk.RESPONSE_DELETE_EVENT: # user has closed the dialog: return 'No'
			response = 0
		return response
	
	def show_info_dialog(self, message, use_threads = False):
		""" Show an info dialog with an OK button, showing 'message' """
		if self.quitting:
			return
		if use_threads:
			gdk.threads_enter()
		dialog = gtk.MessageDialog(self.main_window, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, message)
		dialog.run()
		dialog.destroy()
		if use_threads:
			gdk.threads_leave()
	
	def show_error_dialog(self, message, use_threads = False):
		""" Show an error dialog with an OK button, showing 'message' """
		if self.quitting:
			return
		if use_threads:
			gdk.threads_enter()
		dialog = gtk.MessageDialog(self.main_window, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, message)
		dialog.run()
		dialog.destroy()
		if use_threads:
			gdk.threads_leave()
	
	def show_trim_details_window(self, text, use_threads = False):
		""" Show the trim details window and add 'text' to its textbuffer """
		if self.quitting:
			return
		if use_threads:
			gdk.threads_enter()
		self.trim_details_window.show()
		end_iter = self.trim_details_textbuffer.get_end_iter()
		self.trim_details_textbuffer.insert(end_iter, text)
		self.trim_details_textview.scroll_to_mark(self.trim_details_textbuffer.get_insert(), 0)
		if use_threads:
			gdk.threads_leave()
	
	def update_list_game_label(self):
		""" Update games statistics labels """
		if self.quitting:
			return
		if self.gamesnumber_total != 0:
			if self.gamesnumber_total == 1:
				text = _("%d game shown") % self.gamesnumber_total
			else:
				text = _("%d games shown") % self.gamesnumber_total
			if self.gamesnumber_available > 0:
				text += _(" - %d available") % self.gamesnumber_available
			if self.gamesnumber_fixable > 0:
				text += _(" - %d to rebuild") % self.gamesnumber_fixable
			if self.gamesnumber_not_available > 0:
				text += _(" - %d not available") % self.gamesnumber_not_available
		else:
			text = _("No games shown")
		self.list_game_label.set_text(text)
		
	def update_statusbar(self, context, text, use_threads = False):
		""" Push 'text' in the statusbar, using 'context' as context """
		if self.quitting:
			return
		if use_threads:
			gdk.threads_enter()
		self.statusbar.push(self.statusbar.get_context_id(context), text)
		if use_threads:
			gdk.threads_leave()
	
	def update_game(self, game_release_number, new_zip_file, use_threads = False):
		""" Update game's check status in treeview """
		if self.quitting:
			return
		# Update self.checksums
		try:
			game = self.db.get_game(game_release_number)
		except:
			self.open_db()
			game = self.db.get_game(game_release_number)	
		
		self.checksums[game[GAME_ROM_CRC]] = new_zip_file
		
		try:
			if use_threads:
				gdk.threads_enter()
			# Search for the game in current treeview and update it
			iter = self.list_treeview_model.get_iter_first()
			if iter == None: # Treeview is empty, nothing to do.
				return
			while self.list_treeview_model.get_value(iter, TVC_RELEASE_NUMBER) != game_release_number:
				iter = self.list_treeview_model.iter_next(iter)
				if iter == None: # Not found in current treeview. Nothing to do.
					return
			self.list_treeview_model.set_value(iter, TVC_CHECK, self.checks[CHECKS_YES])
			if not self.games_check_ok_checkbutton.get_active(): # Check if games list is dirty now
				self.dirty_gameslist = True
			# remove the current game from the dictionary of games to rebuild
			del self.games_to_rebuild[game[GAME_FULLINFO]]
			# Update counters and label
			self.gamesnumber_fixable -= 1
			self.gamesnumber_available += 1
			self.update_list_game_label()
		finally:
			if use_threads:
				gdk.threads_leave()
	
	def update_image(self, game_release_number, image_index, filename, use_threads = False):
		""" Update shown image if needed """
		if self.quitting:
			return
		if use_threads:
			gdk.threads_enter()
		selection = self.list_treeview.get_selection()
		selected_rows_number = selection.count_selected_rows()
		if use_threads:
			gdk.threads_leave()
		if selected_rows_number > 1:
			return
		try:
			if use_threads:
				gdk.threads_enter()
			model, paths = selection.get_selected_rows()
			path = paths[0]
			if path == None:
				return
			iter = model.get_iter(path)
			if model.get_value(iter, TVC_RELEASE_NUMBER) == game_release_number:
				pixbuf = gdk.pixbuf_new_from_file(filename)
				if self.images_resize_rate != 1: #resize images
					pixbuf_new_width = int(pixbuf.get_width() * self.images_resize_rate)
					pixbuf_new_height = int(pixbuf.get_height() * self.images_resize_rate)
					pixbuf = pixbuf.scale_simple(pixbuf_new_width, pixbuf_new_height, gdk.INTERP_BILINEAR)
				if image_index == 1:
					self.image1.set_from_pixbuf(pixbuf)
					self.image1_frame.set_size_request(pixbuf.get_width(), pixbuf.get_height())
					if self.images_resize_rate != None:
						self.images_window_image1.set_from_file(filename)
				else:
					self.image2.set_from_pixbuf(pixbuf)
					self.image2_frame.set_size_request(pixbuf.get_width(), pixbuf.get_height())
					if self.images_resize_rate != None:
						self.images_window_image2.set_from_file(filename)
		except:
			pass
		finally:
			if use_threads:
				gdk.threads_leave()
	
	def set_previous_treeview_cursor(self, use_threads = False):
		"""
		If there was a previous treeview selection, restore it.
		Or else, hide games info.
		"""
		if self.quitting:
			return
		if use_threads:
			gdk.threads_enter()
		try:
			if self.previous_selection_release_number == None:
				self.__hide_infos()
			else:
				# check if we are already on the game we are searching for
				path, column = self.list_treeview.get_cursor()
				if path != None:
					iter = self.list_treeview_model.get_iter(path)
					if self.list_treeview_model.get_value(iter, TVC_RELEASE_NUMBER) == self.previous_selection_release_number:
						# we are already on the previous selection, nothing to do
						# just make sure info are shown
						self.__show_infos()
						return
				# search for the previous selection
				iter = self.list_treeview_model.get_iter_first()
				if iter == None: # Treeview is empty, nothing to do.
					self.previous_selection_release_number = None
					self.__hide_infos()
					return
				while self.list_treeview_model.get_value(iter, TVC_RELEASE_NUMBER) != self.previous_selection_release_number:
					iter = self.list_treeview_model.iter_next(iter)
					if iter == None:
						# game not found in list
						self.previous_selection_release_number = None
						self.__hide_infos()
						return
				if iter != None: # previous selection found, set the cursor on it
					path = self.list_treeview_model.get_path(iter)
					self.list_treeview.set_cursor(path)
		finally:
			if use_threads:
				gdk.threads_leave()
	
	def toggle_images_download_toolbutton(self, use_threads = False):
		""" Toggle icon and tooltip on 'Download images' toolbutton and menuitem """
		if self.quitting:
			return
		if use_threads:
			gdk.threads_enter()
		if self.images_download_toolbutton.get_stock_id() == gtk.STOCK_JUMP_TO:
			# switch to cancel button
			self.images_download_toolbutton.set_stock_id(gtk.STOCK_CANCEL)
			self.images_download_menuitem.set_image(gtk.image_new_from_stock(gtk.STOCK_CANCEL, gtk.ICON_SIZE_MENU))
			self.old_aidt_tooltip_text = self.images_download_toolbutton.get_tooltip_text()
			self.images_download_toolbutton.set_tooltip_text(_("Stop the download process.") + " (Ctrl+D)")
			self.images_download_menuitem.set_tooltip_text(_("Stop the download process.") + " (Ctrl+D)")
		else:
			# restore original button
			self.images_download_toolbutton.set_stock_id(gtk.STOCK_JUMP_TO)
			self.images_download_menuitem.set_image(gtk.image_new_from_stock(gtk.STOCK_JUMP_TO, gtk.ICON_SIZE_MENU))
			self.images_download_toolbutton.set_tooltip_text(self.old_aidt_tooltip_text)
			self.images_download_menuitem.set_tooltip_text(self.old_aidt_tooltip_text)
		if use_threads:
			gdk.threads_leave()
	
	def toggle_rebuild_roms_archives_toolbutton(self, use_threads = False):
		""" Toggle icon and tooltip on 'Rebuild archives' toolbutton and menuitem """
		if self.quitting:
			return
		if use_threads:
			gdk.threads_enter()
		if self.rebuild_roms_archives_toolbutton.get_stock_id() == gtk.STOCK_CONVERT:
			# switch to cancel button
			self.rebuild_roms_archives_toolbutton.set_stock_id(gtk.STOCK_CANCEL)
			self.rebuild_roms_archives_menuitem.set_image(gtk.image_new_from_stock(gtk.STOCK_CANCEL, gtk.ICON_SIZE_MENU))
			self.old_rrat_tooltip_text = self.rebuild_roms_archives_toolbutton.get_tooltip_text()
			self.rebuild_roms_archives_toolbutton.set_tooltip_text(_("Stop the rebuild process.") + " (Ctrl+F)")
			self.rebuild_roms_archives_menuitem.set_tooltip_text(_("Stop the rebuild process.") + " (Ctrl+F)")
			self.rebuild_roms_archives_toolbutton.set_sensitive(True)
			self.rebuild_roms_archives_menuitem.set_sensitive(True)
		else:
			# restore original button
			self.rebuild_roms_archives_toolbutton.set_stock_id(gtk.STOCK_CONVERT)
			self.rebuild_roms_archives_menuitem.set_image(gtk.image_new_from_stock(gtk.STOCK_CONVERT, gtk.ICON_SIZE_MENU))
			self.rebuild_roms_archives_toolbutton.set_tooltip_text(self.old_rrat_tooltip_text)
			self.rebuild_roms_archives_menuitem.set_tooltip_text(self.old_rrat_tooltip_text)
			if len(self.games_to_rebuild) > 0:
				self.rebuild_roms_archives_toolbutton.set_sensitive(True)
				self.rebuild_roms_archives_menuitem.set_sensitive(True)
		if use_threads:
			gdk.threads_leave()
	
	def toggle_extract_options_in_treeview_popupmenu(self, use_threads = False):
		""" Toggle extract, extractin and stop options in treeview popup menu"""
		if self.quitting:
			return
		if use_threads:
			gdk.threads_enter()
		if self.list_treeview_popup_extract_stop_menuitem.get_property("visible"):
			self.list_treeview_popup_extract_stop_menuitem.hide()
			self.list_treeview_popup_extract_menuitem.show()
			self.list_treeview_popup_extractin_menuitem.show()
		else:
			self.list_treeview_popup_extract_stop_menuitem.set_sensitive(True)
			self.list_treeview_popup_extract_menuitem.set_sensitive(False)
			self.list_treeview_popup_extractin_menuitem.set_sensitive(False)
			self.list_treeview_popup_extract_stop_menuitem.show()
			self.list_treeview_popup_extract_menuitem.hide()
			self.list_treeview_popup_extractin_menuitem.hide()
		if use_threads:
			gdk.threads_leave()
	
	def open_db(self):
		""" Open database """
		self.db = DB(DB_FILE)
	
	def add_games(self, scan_anyway = False, use_threads = False):
		"""
		Add games from database to the treeview model.
		While adding games, if 'scan_anyway' is True, scan for roms archives on disk.
		"""
		if self.quitting:
			return
		# Populate checksums dictionary
		self.checksums = {}
		try:
			crcs = self.db.get_all_games_crc()
		except:
			self.open_db()
			crcs = self.db.get_all_games_crc()
		for crc in crcs:
			self.checksums[crc[0]] = None
		
		# Deactivate widgets
		self.deactivate_widgets(use_threads)
		
		## Check the games we have on disk
		self.update_statusbar("Games", _("Scanning roms on disk..."), use_threads)
		
		# Check roms on disk
		unknown_roms_path = config.get_option("unknown_roms_path")
		roms_path = config.get_option("roms_path")
		new_roms_path = config.get_option("new_roms_path")
		images_path = config.get_option("images_path") # Useful to avoid scanning recursively in directories
		                                               # full of images, when 'images_path' is a subdirectory
		                                               # of 'roms_path'.		

		if scan_anyway or self.autoscan_archives_at_start:
			# Do it once only (at start).
			self.autoscan_archives_at_start = False
			# inform 'rescan archives' toolbutton that archives have been already scanned
			self.archives_already_scanned = True
			# Set archives to be scanned
			scan_archives = True
		else:
			self.archives_already_scanned = False
			scan_archives = False
					
		if scan_archives and os.path.exists(unknown_roms_path):
			# check in 'unknown_roms_path' directory for new roms.
			# If one is found, move it in 'new_roms_path' directory.
			for file in glob.iglob(os.path.join(unknown_roms_path, "*")):
				if self.quitting: # interrupt now
					return
				if os.path.isdir(file):
					continue # no recursive directory scan in 'unknown_roms_path'
				crc = None
				if file[len(file) - 4:].lower() == ".zip":
					crc = get_crc32_zip(file)
				elif file[len(file) - 4:].lower() == ".nds":
					crc = get_crc32(file)
				else: # Not a .zip or .nds file, leave it untouched and skip to next one.
					continue
				if crc != None and crc in self.checksums:
					if os.path.exists(new_roms_path) and os.access(new_roms_path, os.W_OK):
						try:
							shutil.move(file, new_roms_path)
						except:
							# Some kind of error. Well, redundant file anyway, remove it
							os.remove(file)
							message = _("'%s' was redundant. Deleted.") % file
							self.show_info_dialog(message, use_threads)
		
		if scan_archives and os.path.exists(roms_path):
			# recursively check games in 'roms_path' directory.
			# unknown roms are moved in 'unknown_roms_path' directory,
			# duplicate roms are moved to 'unknown_roms_path' or deleted.
			paths_to_check = []
			paths_to_check.append(roms_path)
			while len(paths_to_check) != 0:
				next_path = paths_to_check[0]
				paths_to_check[0:1] = []
				for file in glob.iglob(os.path.join(next_path, "*")):
					if self.quitting: # interrupt now
						return
					if os.path.isdir(file):
						if file != unknown_roms_path and file != new_roms_path and file != images_path:
							addpath = True
							for path in paths_to_check:
								if path == file: # we have already set this dir to be scanned
									addpath = False
									break
							if addpath:
								paths_to_check.append(file)
					else: # 'file' is not a directory
						crc = None
						if file[len(file) - 4:].lower() == ".zip":
							crc = get_crc32_zip(file)
						elif file[len(file) - 4:].lower() == ".nds":
							crc = get_crc32(file)
						else: # Not a .zip or .nds file, leave it untouched and skip to next one.
							continue
						if crc != None and crc in self.checksums:
							if self.checksums[crc] == None:
								self.checksums[crc] = file
							else:
								# Duplicate file
								message = _("'%s' is a duplicate file. Delete?") % file
								if self.show_yesno_question_dialog(message, use_threads) == True:
									os.remove(file)
								else:
									# Move in 'unknown_roms_path'
									if os.path.exists(unknown_roms_path) and os.access(unknown_roms_path, os.W_OK):
										try:
											shutil.move(file, unknown_roms_path)
										except:
											# Some kind of error. Well, redundant file anyway, remove it
											os.remove(file)
											message = _("'%s' was redundant. Deleted.") % file
											self.show_info_dialog(message, use_threads)
						else: # crc == None or crc not in self.checksums
							if os.path.exists(unknown_roms_path) and os.access(unknown_roms_path, os.W_OK):
								try:
									shutil.move(file, unknown_roms_path)
								except:
									# Some kind of error. Well, redundant file anyway, remove it
									os.remove(file)
									message = _("'%s' was redundant. Deleted.") % file
									self.show_info_dialog(message, use_threads)
		
		if scan_archives and os.path.exists(new_roms_path) and new_roms_path != roms_path:
			# check games in 'new_roms_path' directory.
			# unknown roms are moved in 'unknown_roms_path' directory,
			# duplicate roms are moved to 'unknown_roms_path' or deleted.
			for file in glob.iglob(os.path.join(new_roms_path, "*")):
				if self.quitting: # interrupt now
					return
				if os.path.isdir(file):
					continue # no recursive directory scan in 'new_roms_path'
				crc = None
				if file[len(file) - 4:].lower() == ".zip":
					crc = get_crc32_zip(file)
				elif file[len(file) - 4:].lower() == ".nds":
					crc = get_crc32(file)
				else: # Not a .zip or .nds file, leave it untouched and skip to next one.
					continue
				if crc != None and crc in self.checksums:
					if self.checksums[crc] == None:
						self.checksums[crc] = file
					else:
						# Duplicate file
						message = _("'%s' is a duplicate file. Delete?") % file
						if self.show_yesno_question_dialog(message, use_threads) == True:
					   	   os.remove(file)
					   	else:
							# Move in 'unknown_roms_path'
							if os.path.exists(unknown_roms_path) and os.access(unknown_roms_path, os.W_OK):
								try:
									shutil.move(file, unknown_roms_path)
								except:
									# Some kind of error. Well, redundant file anyway, remove it
									os.remove(file)
									message = _("'%s' was redundant. Deleted.") % file
									self.show_info_dialog(message, use_threads)
				else: # crc == None or crc not in self.checksums
					if os.path.exists(unknown_roms_path) and os.access(unknown_roms_path, os.W_OK):
						try:
							shutil.move(file, unknown_roms_path)
						except:
							# Some kind of error. Well, redundant file anyway, remove it
							os.remove(file)
							message = _("'%s' was redundant. Deleted.") % file
							self.show_info_dialog(message, use_threads)		
		
		self.update_statusbar("Games", _("Loading games list..."), use_threads)
		
		# Remove model from treeview for update
		if use_threads:
			gdk.threads_enter()
		self.list_treeview.set_model(None)
		if use_threads:
			gdk.threads_leave()
		
		# We can't exit while updating list
		self.canexitnow = False
		
		# Add games to model and rebuild dictionary of games to rebuild.
		try:
			self.__update_list(self.db.get_all_games(), anyway = True, rebuild_dict = True, use_threads = use_threads)
		except:
			self.open_db()
			self.__update_list(self.db.get_all_games(), anyway = True, rebuild_dict = True, use_threads = use_threads)
		
		# Now we can exit
		self.canexitnow = True
		
		# Set updated model back to treeview
		if use_threads:
			gdk.threads_enter()
		self.list_treeview.set_model(self.list_treeview_model)
		if use_threads:
			gdk.threads_leave()
		
		# Get total loaded games
		games_number = self.gamesnumber_total
		
		# Set back the games checks checkbuttons status
		if self.quitting: # interrupt now, if requested
			return
		if use_threads:
			gdk.threads_enter()
		if not self.games_check_ok_checkbutton.get_active():
			self.on_games_check_ok_checkbutton_toggled(self.games_check_ok_checkbutton)
		if not self.games_check_no_checkbutton.get_active():
			self.on_games_check_no_checkbutton_toggled(self.games_check_no_checkbutton)
		if not self.games_check_convert_checkbutton.get_active():
			self.on_games_check_convert_checkbutton_toggled(self.games_check_convert_checkbutton)
		if use_threads:
			gdk.threads_leave()
		
		text = _("%d games loaded succesfully.") % games_number
		self.update_statusbar("Games", text, use_threads)
		
		# Clear up all filter
		if self.quitting: # interrupt now, if requested
			return
		if use_threads:
			gdk.threads_enter()
		self.filter_name_entry.handler_block(self.fne_sid)
		self.filter_location_combobox.handler_block(self.flocc_sid)
		self.filter_language_combobox.handler_block(self.flanc_sid)
		self.filter_size_combobox.handler_block(self.fsc_sid)
		self.filter_clear_button.clicked()
		self.filter_name_entry.handler_unblock(self.fne_sid)
		self.filter_location_combobox.handler_unblock(self.flocc_sid)
		self.filter_language_combobox.handler_unblock(self.flanc_sid)
		self.filter_size_combobox.handler_unblock(self.fsc_sid)
		if use_threads:
			gdk.threads_leave()
		
		# Hide old infos
		self.previous_selection_release_number = None
		self.activate_widgets(use_threads)
	
	def quit(self):
		# Check if we can exit now
		if not self.canexitnow:
			gobject.timeout_add(100, self.quit) # retry in 100 milliseconds
			return True
		# Prepare for quitting
		self.quitting = True
		# Save config file
		config.save()
		# Stop all threads
		for thread in self.threads:
			if thread.isAlive() and thread.getName() != "Gui":
				thread.stop()
		# Exit
		gtk.main_quit()
