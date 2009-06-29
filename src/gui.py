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
import threading

import locale, gettext
_ = gettext.gettext

try:
	import gtk
	import gtk.glade
except:
	print "You have to install 'gtk' and 'gtk.glade' modules to run this application."
	from sys import exit
	exit(1)

from globals import *
from db import *
from downloaders import *
from files import *

import glob
import shutil

TVC_CHECK = 0
TVC_FLAG = 1
TVC_RELEASE_NUMBER = 2
TVC_TITLE = 3

gtk.gdk.threads_init()

class Gui(threading.Thread):
	""" Graphical User Interface """
	def __init__(self, threads):
		threading.Thread.__init__(self, name="Gui")
		
		self.threads = threads
		
		self.builder = gtk.Builder()
		self.builder.set_translation_domain(APP_NAME)
		self.builder.add_from_file(os.path.join(DATA_DIR, "drm.glade"))
		
		self.main_window = self.builder.get_object("main_window")
		self.images_window = self.builder.get_object("images_window")
		self.options_dialog = self.builder.get_object("options_dialog")
		self.dat_update_toolbutton = self.builder.get_object("dat_update_toolbutton")
		self.all_images_download_toolbutton = self.builder.get_object("all_images_download_toolbutton")
		self.rebuild_roms_archives_toolbutton = self.builder.get_object("rebuild_roms_archives_toolbutton")
		self.show_review_toolbutton = self.builder.get_object("show_review_toolbutton")
		self.options_toolbutton = self.builder.get_object("options_toolbutton")
		self.games_check_ok_checkbutton = self.builder.get_object("games_check_ok_checkbutton")
		self.games_check_no_checkbutton = self.builder.get_object("games_check_no_checkbutton")
		self.games_check_warn_checkbutton = self.builder.get_object("games_check_warn_checkbutton")
		self.options_check_images_crc_checkbutton = self.builder.get_object("options_check_images_crc_checkbutton")
		self.options_roms_path_filechooserbutton = self.builder.get_object("options_roms_path_filechooserbutton")
		self.options_unknown_roms_path_filechooserbutton = self.builder.get_object("options_unknown_roms_path_filechooserbutton")
		self.options_new_roms_path_filechooserbutton = self.builder.get_object("options_new_roms_path_filechooserbutton")
		self.options_review_url_entry = self.builder.get_object("options_review_url_entry")
		self.options_ok_button = self.builder.get_object("options_ok_button")
		self.options_cancel_button = self.builder.get_object("options_cancel_button")
		self.about_toolbutton = self.builder.get_object("about_toolbutton")
		self.images_window_eventbox = self.builder.get_object("images_window_eventbox")
		self.images_window_image1 = self.builder.get_object("images_window_image1")
		self.images_window_image2 = self.builder.get_object("images_window_image2")
		self.list_treeview = self.builder.get_object("list_treeview")
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
		# Widgets needed for hiding informations
		self.images_hbox = self.builder.get_object("images_hbox")
		self.info_label_vbox = self.builder.get_object("info_label_vbox")
		
		# Get screen's height
		self.screen_height = self.main_window.get_screen().get_height()
		
		self.main_window.set_title(APP_NAME + " - " + APP_VERSION)
		self.about_dialog.set_version(APP_VERSION)
		self.main_window_visible = True
		
		# Enable click on website url in about dialog
		def about_dialog_url_clicked(dialog, link, user_data):
			pass
		gtk.about_dialog_set_url_hook(about_dialog_url_clicked, None)
		
		# Set icon and logo in about_dialog
		try:
			self.about_dialog.set_icon_from_file(os.path.join(DATA_IMG_DIR, "icon.png"))
			self.about_dialog.set_logo(gtk.gdk.pixbuf_new_from_file(os.path.join(DATA_IMG_DIR, "icon.png")))
		except:
			pass
		
		try:
			self.main_window.set_icon_from_file(os.path.join(DATA_IMG_DIR, "icon.png"))
		except:
			pass
		
		## StatusIcon stuff
		# popup menu
		self.popup_menu = gtk.Menu()
		self.toggle_main_window_menuitem = gtk.ImageMenuItem(_("Hide"))
		self.toggle_main_window_menuitem.set_image(gtk.image_new_from_stock(gtk.STOCK_LEAVE_FULLSCREEN, gtk.ICON_SIZE_MENU))
		self.toggle_main_window_menuitem.connect('activate', self.on_statusicon_toggle_main_window_activate)
		self.popup_menu.append(self.toggle_main_window_menuitem)
		menuitem = gtk.SeparatorMenuItem()
		self.popup_menu.append(menuitem)
		self.dat_update_menuitem = gtk.ImageMenuItem(_("Update DAT"))
		self.dat_update_menuitem.set_image(gtk.image_new_from_stock(gtk.STOCK_REFRESH, gtk.ICON_SIZE_MENU))
		self.dat_update_menuitem.connect('activate', self.on_statusicon_dat_update_activate)
		self.popup_menu.append(self.dat_update_menuitem)
		self.all_images_download_menuitem = gtk.ImageMenuItem(_("Download all images"))
		self.all_images_download_menuitem.set_image(gtk.image_new_from_stock(gtk.STOCK_JUMP_TO, gtk.ICON_SIZE_MENU))
		self.all_images_download_menuitem.connect('activate', self.on_statusicon_all_images_download_activate)
		self.popup_menu.append(self.all_images_download_menuitem)
		self.rebuild_roms_archives_menuitem = gtk.ImageMenuItem(_("Rebuild archives"))
		self.rebuild_roms_archives_menuitem.set_image(gtk.image_new_from_stock(gtk.STOCK_DIALOG_WARNING, gtk.ICON_SIZE_MENU))
		self.rebuild_roms_archives_menuitem.connect('activate', self.on_statusicon_rebuild_roms_archives_activate)
		self.popup_menu.append(self.rebuild_roms_archives_menuitem)
		menuitem = gtk.SeparatorMenuItem()
		self.popup_menu.append(menuitem)
		self.show_review_menuitem = gtk.ImageMenuItem(_("Reviews"))
		self.show_review_menuitem.set_image(gtk.image_new_from_stock(gtk.STOCK_DIALOG_INFO, gtk.ICON_SIZE_MENU))
		self.show_review_menuitem.connect('activate', self.on_statusicon_show_review_activate)
		self.popup_menu.append(self.show_review_menuitem)
		menuitem = gtk.SeparatorMenuItem()
		self.popup_menu.append(menuitem)
		self.options_menuitem = gtk.ImageMenuItem(_("Options"))
		self.options_menuitem.set_image(gtk.image_new_from_stock(gtk.STOCK_PROPERTIES, gtk.ICON_SIZE_MENU))
		self.options_menuitem.connect('activate', self.on_statusicon_options_activate)
		self.popup_menu.append(self.options_menuitem)
		menuitem = gtk.SeparatorMenuItem()
		self.popup_menu.append(menuitem)
		self.about_menuitem = gtk.ImageMenuItem(_("About"))
		self.about_menuitem.set_image(gtk.image_new_from_stock(gtk.STOCK_ABOUT, gtk.ICON_SIZE_MENU))
		self.about_menuitem.connect('activate', self.on_statusicon_about_activate)
		self.popup_menu.append(self.about_menuitem)
		menuitem = gtk.SeparatorMenuItem()
		self.popup_menu.append(menuitem)
		self.quit_menuitem = gtk.ImageMenuItem(_("Quit"))
		self.quit_menuitem.set_image(gtk.image_new_from_stock(gtk.STOCK_QUIT, gtk.ICON_SIZE_MENU))
		self.quit_menuitem.connect('activate', self.on_statusicon_quit_activate)
		self.popup_menu.append(self.quit_menuitem)
		# status icon
		self.statusicon = gtk.StatusIcon()
		self.statusicon.set_from_file(os.path.join(DATA_IMG_DIR, "icon.png"))
		self.statusicon.set_tooltip(self.main_window.get_title())
		self.statusicon.connect('activate', self.on_statusicon_activate)
		self.statusicon.connect('popup-menu', self.on_statusicon_popup_menu, self.popup_menu)
		self.statusicon.set_visible(True)
		
		self.image1.clear()
		self.image2.clear()
		self.images_window_image1.clear()
		self.images_window_image2.clear()
		
		# Load flags images
		self.flags = []
		for i in countries_short.keys():
			file = os.path.join(DATA_IMG_DIR, countries_short[i].lower() + ".png")
			self.flags.append(gtk.gdk.pixbuf_new_from_file(file))
		
		# Load checks images
		self.checks = []
		image = gtk.Image()
		self.checks.append(image.render_icon(gtk.STOCK_NO, gtk.ICON_SIZE_BUTTON))
		self.checks.append(image.render_icon(gtk.STOCK_OK, gtk.ICON_SIZE_BUTTON))
		self.checks.append(image.render_icon(gtk.STOCK_DIALOG_WARNING, gtk.ICON_SIZE_BUTTON))
		
		# Setup all needed stuff for main list treeview
		self.list_treeview_model = gtk.ListStore(gtk.gdk.Pixbuf, gtk.gdk.Pixbuf, int, str)
		self.list_treeview.set_model(self.list_treeview_model)
		self.list_treeview_crt = gtk.CellRendererText()
		self.list_treeview_crt_img = gtk.CellRendererPixbuf()
		self.list_treeview_tvc_found = gtk.TreeViewColumn(_("Found"), self.list_treeview_crt_img, pixbuf=TVC_CHECK)
		self.list_treeview.append_column(self.list_treeview_tvc_found)
		self.list_treeview_tvc_region = gtk.TreeViewColumn(_("Region"), self.list_treeview_crt_img, pixbuf=TVC_FLAG)
		self.list_treeview.append_column(self.list_treeview_tvc_region)
		self.list_treeview_tvc_relnum = gtk.TreeViewColumn("#", self.list_treeview_crt, text=TVC_RELEASE_NUMBER)
		self.list_treeview_tvc_relnum.set_sort_column_id(TVC_RELEASE_NUMBER)
		self.list_treeview.append_column(self.list_treeview_tvc_relnum)
		self.list_treeview_tvc_name = gtk.TreeViewColumn(_("Name"), self.list_treeview_crt, text=TVC_TITLE)
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
		self.games_check_warn_checkbutton.set_active(config.get_option("show_fixable_games"))
		
		# Connect signals
		self.main_window.connect("delete_event", self.on_main_window_delete_event)
		self.statusbar.connect("text-pushed", self.on_statusbar_text_pushed)
		self.dat_update_toolbutton.connect("clicked", self.on_dat_update_toolbutton_clicked)
		self.filter_clear_button.connect("clicked", self.on_filter_clear_button_clicked)
		self.options_toolbutton.connect("clicked", self.on_options_toolbutton_clicked)
		self.options_dialog.connect("response", self.on_options_dialog_response)
		self.options_dialog.connect("delete_event", self.on_window_delete_event)
		self.images_window.connect("delete_event", self.on_window_delete_event)
		self.about_toolbutton.connect("clicked", self.on_about_toolbutton_clicked)
		self.about_dialog.connect("response", self.on_about_dialog_response)
		self.list_treeview.connect("cursor-changed", self.on_list_treeview_cursor_changed)
		self.show_review_toolbutton.connect("clicked", self.on_show_review_toolbutton_clicked)
		self.games_check_ok_checkbutton.connect("toggled", self.on_games_check_ok_checkbutton_toggled)
		self.games_check_no_checkbutton.connect("toggled", self.on_games_check_no_checkbutton_toggled)
		self.games_check_warn_checkbutton.connect("toggled", self.on_games_check_warn_checkbutton_toggled)
		# We need signal id for the following signals
		self.fne_sid = self.filter_name_entry.connect("changed",self.on_filter_triggered)
		self.flocc_sid = self.filter_location_combobox.connect("changed", self.on_filter_triggered)
		self.flanc_sid = self.filter_language_combobox.connect("changed", self.on_filter_triggered)
		self.fsc_sid = self.filter_size_combobox.connect("changed", self.on_filter_triggered)
		self.aidtb_sid = self.all_images_download_toolbutton.connect("clicked", self.on_all_images_download_toolbutton_clicked)
		self.rratb_sid = self.rebuild_roms_archives_toolbutton.connect("clicked", self.on_rebuild_roms_archives_toolbutton_clicked)
		self.ite_sid = None # info_title_eventbox signal
		
		self.quitting = False # Are we quitting?
		
		self.db = None
		
		self.gamesnumber = 0
		self.gamesnumber_available = 0
		self.gamesnumber_not_available = 0
		self.gamesnumber_fixable = 0 # Only fixable games showed in treeview
		self.games_to_be_fixed = {} # All fixable games
		
		self.dirty_gameslist = False
		
		self.checksums = {}	
		
		self.deactivate_widgets()
		
	def run(self):
		gtk.main()
	
	def stop(self):
		self.quit()
	
	def __add_game_to_list(self, game, anyway = False):
		""" Add 'game' in treeview """
		if self.quitting == True:
			return
		
		relnum = game[GAME_RELEASE_NUMBER]
		title = game[GAME_TITLE]
		region = game[GAME_LOCATION_INDEX]
		crc = game[GAME_ROM_CRC]
		flag = self.flags[countries_short.keys().index(region)]

		if self.checksums[crc] != None: # we have the game
			if anyway or self.games_check_ok_checkbutton.get_active() or self.games_check_warn_checkbutton.get_active():
				disk_filename = self.checksums[crc].split(os.sep)
				disk_filename = disk_filename[len(disk_filename)-1]
				db_filename = game[GAME_FULLINFO] + disk_filename[len(disk_filename)-4:]
				nds_filename = game[GAME_FULLINFO] + ".nds"
				if disk_filename == db_filename and get_nds_filename_from_zip(self.checksums[crc]) == nds_filename:
					check = self.checks[CHECKS_YES]
					if self.games_check_ok_checkbutton.get_active():
						self.gamesnumber_available += 1
					else:
						return
				else:
					check = self.checks[CHECKS_WARN]
					if self.games_check_warn_checkbutton.get_active():
						self.gamesnumber_fixable += 1
					else:
						return
			else:
				return
		else:
			if anyway or self.games_check_no_checkbutton.get_active():
				check = self.checks[CHECKS_NO]
				self.gamesnumber_not_available += 1
			else:
				return
			
		self.list_treeview_model.append((check, flag, relnum, title))
		self.gamesnumber += 1
	
	def __update_list(self, games):
		""" List 'games' in treeview """
		if self.quitting == True:
			return
		self.list_treeview_model.clear()
		self.gamesnumber = 0
		self.gamesnumber_available = 0
		self.gamesnumber_fixable = 0
		self.gamesnumber_not_available = 0
		for game in reversed(games):
			self.__add_game_to_list(game)
		self.update_list_game_label()
	
	def __filter(self):
		""" Filter list by all criteria """
		if self.quitting == True:
			return
		self.__hide_infos()
		self.images_window.hide()
		string = self.filter_name_entry.get_text()
		location_iter = self.filter_location_combobox.get_active_iter()
		location = self.filter_location_model.get_value(location_iter, 1)
		language_iter = self.filter_language_combobox.get_active_iter()
		language = self.filter_language_model.get_value(language_iter, 1)
		size_iter = self.filter_size_combobox.get_active_iter()
		size = self.filter_size_model.get_value(size_iter, 1)
		try:
			self.__update_list(self.db.filter_by(string, location, language, size))
		except:
			# Open a new database connection
			self.open_db()
			self.__update_list(self.db.filter_by(string, location, language, size))
		self.show_review_toolbutton.set_sensitive(False)
		self.show_review_menuitem.set_sensitive(False)
	
	def __hide_infos(self):
		""" Hide game's info """
		if self.quitting == True:
			return
		self.images_hbox.hide()
		self.info_title_label.hide()
		self.info_label_vbox.hide()
	
	def __show_infos(self):
		""" Show game's info """
		if self.quitting == True:
			return
		self.images_hbox.show()
		self.info_title_label.show()
		self.info_label_vbox.show()
	
	# Callback functions
	def on_main_window_delete_event(self, window, event):
		self.quit()
	
	def on_statusicon_activate(self, statusicon):
		if self.quitting == True:
			return
		if self.main_window_visible:
			self.main_window.hide()
			self.images_window.hide()
			self.toggle_main_window_menuitem.set_image(gtk.image_new_from_stock(gtk.STOCK_FULLSCREEN, gtk.ICON_SIZE_MENU))
			self.toggle_main_window_menuitem.get_children()[0].set_label(_("Show"))
			self.main_window_visible = False
		else:
			self.main_window.show()
			self.toggle_main_window_menuitem.set_image(gtk.image_new_from_stock(gtk.STOCK_LEAVE_FULLSCREEN, gtk.ICON_SIZE_MENU))
			self.toggle_main_window_menuitem.get_children()[0].set_label(_("Hide"))
			self.main_window_visible = True
	
	def on_statusicon_toggle_main_window_activate(self, widget):
		self.on_statusicon_activate(self.statusicon)
	
	def on_statusicon_dat_update_activate(self, widget):
		self.on_dat_update_toolbutton_clicked(self.dat_update_toolbutton)
	
	def on_statusicon_all_images_download_activate(self, widget):
		self.on_all_images_download_toolbutton_clicked(self.all_images_download_toolbutton)
	
	def on_statusicon_rebuild_roms_archives_activate(self, widget):
		self.on_rebuild_roms_archives_toolbutton_clicked(self.rebuild_roms_archives_toolbutton)
	
	def on_statusicon_show_review_activate(self, widget):
		self.on_show_review_toolbutton_clicked(self.show_review_toolbutton)
	
	def on_statusicon_options_activate(self, widget):
		self.on_options_toolbutton_clicked(self.options_toolbutton)
	
	def on_statusicon_about_activate(self, widget):
		self.on_about_toolbutton_clicked(widget)
	
	def on_statusicon_quit_activate(self, widget, data = None):
		self.quit()
	
	def on_statusicon_popup_menu(self, widget, button, time, data = None):
		if button == 3:
			if data:
				data.show_all()
				data.popup(None, None, None, button, time)
		pass
	
	def on_statusbar_text_pushed(self, statusbar, context_id, text):
		self.statusicon.set_tooltip(text)
	
	def on_list_treeview_cursor_changed(self, treeview):
		if self.ite_sid != None:
			self.info_title_eventbox.disconnect(self.ite_sid)
			self.ite_sid = None
					
		selection = treeview.get_selection()
		model, iter = selection.get_selected()
		
		try:
			relnum = model.get_value(iter, TVC_RELEASE_NUMBER)
		except: # model is empty
			return
		
		try:
			game = self.db.get_game(relnum)
		except:
			self.open_db()
			game = self.db.get_game(relnum)
		
		# Show images if available, or else download them
		img1 = game[GAME_IMG1_LOCAL_PATH]
		img2 = game[GAME_IMG2_LOCAL_PATH]
		
		if os.path.exists(img1) and os.path.exists(img2):
			pixbuf1 = gtk.gdk.pixbuf_new_from_file(img1)
			pixbuf2 = gtk.gdk.pixbuf_new_from_file(img2)
			if self.screen_height < 800: # resize images to 50% and enable images_window
				self.images_eventbox.connect("button-press-event", self.toggle_images_window,
											 game[GAME_FULLINFO], img1, img2)
				self.images_window_eventbox.connect("button-press-event", self.toggle_images_window)
				self.images_window_image1.set_from_file(img1)
				self.images_window_image2.set_from_file(img2)
				pixbuf1 = pixbuf1.scale_simple(pixbuf1.get_width()/2, pixbuf1.get_height()/2, gtk.gdk.INTERP_BILINEAR)
				pixbuf2 = pixbuf2.scale_simple(pixbuf2.get_width()/2, pixbuf2.get_height()/2, gtk.gdk.INTERP_BILINEAR)
				# resize images frames too
				self.image1_frame.set_size_request(pixbuf1.get_width(), pixbuf1.get_height())
				self.image2_frame.set_size_request(pixbuf2.get_width(), pixbuf2.get_height())
				
			self.image1.set_from_pixbuf(pixbuf1)
			self.image2.set_from_pixbuf(pixbuf2)
		else:
			self.image1.clear()
			self.image2.clear()
			if self.screen_height < 800:
				self.images_window_image1.clear()
				self.images_window_image2.clear()
			thread = ImagesDownloader(self, game)
			self.threads.append(thread)
			thread.start()
		
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
		
		if len(duplicates_fullinfo) != 0:
			text = _("Duplicates:")
			for d in reversed(duplicates_fullinfo):
				text += "\n" + d
				self.info_title_label.set_tooltip_text(text)
		else:
			self.info_title_label.set_tooltip_text(_("No duplicates"))

		self.ite_sid = self.info_title_eventbox.connect("button-press-event", self.on_info_title_eventbox_button_press_event,
										 relnum, duplicates_relnum)
		
		# Show informations
		title = game[GAME_FULLINFO].replace("&", "&amp;")
		if self.screen_height < 800:
			self.info_title_label.set_markup("<span weight=\"bold\">" + title + "</span>")
		else:
			self.info_title_label.set_markup("<span size=\"x-large\" weight=\"bold\">" +
											  title + "</span>")
		self.info_save_label.set_text(game[GAME_SAVE_TYPE])
		size = game[GAME_ROM_SIZE]/1048576
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
		
		self.show_review_toolbutton.set_sensitive(True)
		self.show_review_menuitem.set_sensitive(True)
		self.__show_infos()
	
	def on_info_title_eventbox_button_press_event(self, widget, event, current, duplicates):
		if event.button != 1 or len(duplicates) == 0:
			return
		# search for the next game to show
		next = 0
		for d in duplicates:
			# Take the max from the lessers
			if d > next and d < current:
				next = d
		if next == 0:
			# No max in the lessers, then take the max from the greaters
			for d in duplicates:
				if d > next and d > current:
					next = d
		if next == 0: # Nothing to do then...
			return
		
		iter = self.list_treeview_model.get_iter_first()
		while self.list_treeview_model.get_value(iter, TVC_RELEASE_NUMBER) != next:
			iter = self.list_treeview_model.iter_next(iter)
			if iter == None:
				# Not found in current treeview.
				# Then, add the game we need to the treeview
				self.dirty_gameslist = True
				try:
					game = self.db.get_game(next)
				except:
					self.open_db()
					game = self.db.get_game(next)
				self.__add_game_to_list(game, True)
				self.list_treeview_tvc_relnum.clicked()
				self.list_treeview_tvc_relnum.clicked()
				self.update_list_game_label()
				iter = self.list_treeview_model.get_iter_first()
				
		path = self.list_treeview_model.get_path(iter)
		self.list_treeview.set_cursor(path)
	
	def on_show_review_toolbutton_clicked(self, button):
		selection = self.list_treeview.get_selection()
		model, iter = selection.get_selected()
		relnum = model.get_value(iter, TVC_RELEASE_NUMBER)
		try:
			game = self.db.get_game(relnum)
		except:
			self.open_db()
			game = self.db.get_game(relnum) 
		
		title = game[GAME_TITLE]
		title = title.replace("&", " ")
		title = title.replace("-", " ")
		url = config.get_option("review_url").replace("{FOOBAR}", title)
		import webbrowser
		webbrowser.open(url)
	
	def on_dat_update_toolbutton_clicked(self, button):
		try:
			info = self.db.get_info()
		except:
			self.open_db()
			info = self.db.get_info()
		
		buttons = [] # buttons that need to be disabled while updating
		buttons.append(self.dat_update_toolbutton)
		buttons.append(self.dat_update_menuitem)
		
		thread = DatUpdater(self, self.threads, buttons, info[INFO_DAT_VERSION], info[INFO_DAT_VERSION_URL])
		self.threads.append(thread)
		thread.start()
	
	def on_all_images_download_toolbutton_clicked(self, button):
		try:
			games_number = self.db.get_games_number()
		except:
			self.open_db()
			games_number = self.db.get_games_number()
		
		if button.get_stock_id() == gtk.STOCK_JUMP_TO:
			if games_number == 0:
				return
			try:
				aid = AllImagesDownloader(self, self.db.get_all_games())
			except:
				self.open_db()
				aid = AllImagesDownloader(self, self.db.get_all_games())
			self.threads.append(aid)
			aid.start()
		else: # stop images downloading
			for thread in self.threads:
				if thread.isAlive() and thread.getName() == "AllImagesDownloader":
					thread.stop()
					break
	
	def on_rebuild_roms_archives_toolbutton_clicked(self, button):
		self.on_filter_clear_button_clicked(self.filter_clear_button)
		
		if button.get_stock_id() == gtk.STOCK_DIALOG_WARNING:
			widgets = [] # widgets that need to be disabled while updating
			widgets.append(self.dat_update_toolbutton)
			widgets.append(self.dat_update_menuitem)
			
			rar = RomArchivesRebuild(self, widgets, self.games_to_be_fixed)
			self.threads.append(rar)
			rar.start()
		else: # Stop thread
			self.update_statusbar("RomArchivesRebuild", _("Waiting while the current job is finished..."), False)
			self.rebuild_roms_archives_toolbutton.set_sensitive(False)
			self.rebuild_roms_archives_menuitem.set_sensitive(False)
			for thread in self.threads:
				if thread.isAlive() and thread.getName() == "RomArchivesRebuild":
					thread.stop()
					break
	
	def on_filter_triggered(self, widget):
		""" Filter list """
		self.__filter()
	
	def on_filter_clear_button_clicked(self, button):
		""" Clear all filters """
		filter = 0
		if self.filter_name_entry.get_text() != "":
			filter = 1
		if self.filter_location_combobox.get_active() != 0:
			filter = 2
		if self.filter_language_combobox.get_active() != 0:
			filter = 3
		if self.filter_size_combobox.get_active() != 0:
			filter = 4
			
		if filter == 0:
			if self.dirty_gameslist == False: # No need to clear anything
				return
			else:
				self.__filter()
				self.dirty_gameslist = False
				return
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
		config.set_option("show_available_games", widget.get_active())
		self.__filter()
	
	def on_games_check_no_checkbutton_toggled(self, widget):
		config.set_option("show_not_available_games", widget.get_active())
		self.__filter()
	
	def on_games_check_warn_checkbutton_toggled(self, widget):
		config.set_option("show_fixable_games", widget.get_active())
		self.__filter()
	
	def on_options_toolbutton_clicked(self, menuitem):
		self.options_check_images_crc_checkbutton.set_active(config.get_option("check_images_crc"))
		self.options_roms_path_filechooserbutton.set_current_folder(config.get_option("roms_path"))
		self.options_unknown_roms_path_filechooserbutton.set_current_folder(config.get_option("unknown_roms_path"))
		self.options_new_roms_path_filechooserbutton.set_current_folder(config.get_option("new_roms_path"))
		self.options_review_url_entry.set_text(config.get_option("review_url"))
		self.options_dialog.show()
	
	def on_options_dialog_response(self, dialog, response_id):
		if response_id == 0: # ok
			config.set_option("check_images_crc", self.options_check_images_crc_checkbutton.get_active())
			
			text = self.options_review_url_entry.get_text()
			if len(text) != 0:
				config.set_option("review_url", text)
			else:
				config.set_option_default("review_url")
				
			config.set_option("unknown_roms_path", self.options_unknown_roms_path_filechooserbutton.get_current_folder())
			
			old_roms_path = config.get_option("roms_path")
			config.set_option("new_roms_path", self.options_new_roms_path_filechooserbutton.get_current_folder())
			config.set_option("roms_path", self.options_roms_path_filechooserbutton.get_current_folder())
			if config.get_option("roms_path") != old_roms_path:
				# we need to recheck for games on disk, because path has changed
				self.add_games(False)
			
		self.options_dialog.hide()
	
	def on_window_delete_event(self, window, event):
		window.hide()
		return True
	
	def on_about_toolbutton_clicked(self, menuitem):
		self.about_dialog.run()
	
	def on_about_dialog_response(self, dialog, response_id):
		dialog.hide()
			
	# General functions
	def deactivate_widgets(self):
		""" Disable all widgets' sensitiveness """
		if self.quitting == True:
			return
		self.list_treeview.set_sensitive(False)
		self.dat_update_toolbutton.set_sensitive(False)
		self.dat_update_menuitem.set_sensitive(False)
		self.all_images_download_toolbutton.set_sensitive(False)
		self.all_images_download_menuitem.set_sensitive(False)
		self.rebuild_roms_archives_toolbutton.set_sensitive(False)
		self.rebuild_roms_archives_menuitem.set_sensitive(False)
		self.show_review_toolbutton.set_sensitive(False)
		self.show_review_menuitem.set_sensitive(False)
		self.options_toolbutton.set_sensitive(False)
		self.options_menuitem.set_sensitive(False)
		self.games_check_ok_checkbutton.set_sensitive(False)
		self.games_check_no_checkbutton.set_sensitive(False)
		self.games_check_warn_checkbutton.set_sensitive(False)
		self.filter_name_entry.set_sensitive(False)
		self.filter_clear_button.set_sensitive(False)
		self.filter_location_combobox.set_sensitive(False)
		self.filter_language_combobox.set_sensitive(False)
		self.filter_size_combobox.set_sensitive(False)
	
	def activate_widgets(self):
		""" Enable all widgets' sensitiveness """
		if self.quitting == True:
			return
		if len(self.games_to_be_fixed) > 0:
			self.rebuild_roms_archives_toolbutton.set_sensitive(True)
			self.rebuild_roms_archives_menuitem.set_sensitive(True)
		self.list_treeview.set_sensitive(True)
		self.dat_update_toolbutton.set_sensitive(True)
		self.dat_update_menuitem.set_sensitive(True)
		self.all_images_download_toolbutton.set_sensitive(True)
		self.all_images_download_menuitem.set_sensitive(True)
		self.options_toolbutton.set_sensitive(True)
		self.options_menuitem.set_sensitive(True)
		self.games_check_ok_checkbutton.set_sensitive(True)
		self.games_check_no_checkbutton.set_sensitive(True)
		self.games_check_warn_checkbutton.set_sensitive(True)
		self.filter_name_entry.set_sensitive(True)
		self.filter_clear_button.set_sensitive(True)
		self.filter_location_combobox.set_sensitive(True)
		self.filter_language_combobox.set_sensitive(True)
		self.filter_size_combobox.set_sensitive(True)
	
	def toggle_images_window(self, widget, event, title = None, img1 = None, img2 = None):
		if event.button != 1:
			return
		if img1 != None and img2 != None:
			self.images_window.set_title(title)
			self.images_window_image1.set_from_file(img1)
			self.images_window_image2.set_from_file(img2)
			self.images_window.show()
		else:
			self.images_window.hide()
	
	def show_info_dialog(self, message):
		""" Show an info dialog with just an OK button, showing 'message' """
		gtk.gdk.threads_enter()
		dialog = gtk.MessageDialog(self.main_window, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, message)
		dialog.run()
		dialog.destroy()
		gtk.gdk.threads_leave()
	
	def update_list_game_label(self):
		if self.quitting == True:
			return
		if self.gamesnumber != 0:
			if self.gamesnumber == 1:
				text = _("%d game in list") % self.gamesnumber
			else:
				text = _("%d games in list") % self.gamesnumber
			if self.gamesnumber_available > 0:
				text += _(" - %d available") % self.gamesnumber_available
			if self.gamesnumber_fixable > 0:
				text += _(" - %d to be fixed") % self.gamesnumber_fixable
			if self.gamesnumber_not_available > 0:
				text += _(" - %d not available") % self.gamesnumber_not_available
		else:
			text = _("No games in list")
		
		self.list_game_label.set_text(text)
		
	def update_statusbar(self, context, text, threads = True):
		if self.quitting == True:
			return
		if threads == True:
			gtk.gdk.threads_enter()
		self.statusbar.push(self.statusbar.get_context_id(context), text)
		if threads == True:
			gtk.gdk.threads_leave()
	
	def update_image(self, game_release_number, image_index, filename):
		""" Update showed image if needed """
		if self.quitting == True:
			return
		selection = self.list_treeview.get_selection()
		try:
			model, iter = selection.get_selected()
			if model.get_value(iter, TVC_RELEASE_NUMBER) == game_release_number:
				pixbuf = gtk.gdk.pixbuf_new_from_file(filename)
				if self.screen_height < 800: #resize images to 50%
					pixbuf = pixbuf.scale_simple(pixbuf.get_width()/2, pixbuf.get_height()/2, gtk.gdk.INTERP_BILINEAR)
				if image_index == 1:
					self.image1.set_from_pixbuf(pixbuf)
					self.image1_frame.set_size_request(pixbuf.get_width(), pixbuf.get_height())
					if self.screen_height < 800:
						self.images_window_image1.set_from_file(filename)
				else:
					self.image2.set_from_pixbuf(pixbuf)
					self.image2_frame.set_size_request(pixbuf.get_width(), pixbuf.get_height())
					if self.screen_height < 800:
						self.images_window_image2.set_from_file(filename)
		except:
			pass
	
	def get_games_to_be_fixed(self):
		""" Return a dictionary with ('game_fullinfo': 'actual_path') of
		all the games that need to be fixed """
		# Dictionary of all the games to be fixed
		games = {}
		if self.quitting == True:
			return games
		
		iter = self.list_treeview_model.get_iter_first()
		while iter != None:
			if self.list_treeview_model.get_value(iter, TVC_CHECK) == self.checks[CHECKS_WARN]:
				relnum = self.list_treeview_model.get_value(iter, TVC_RELEASE_NUMBER)
				try:
					game = self.db.get_game(relnum)
				except:
					self.open_db()
					game = self.db.get_game(relnum)
				# Populate the dictionary
				games[game[GAME_FULLINFO]] = self.checksums[game[GAME_ROM_CRC]]
			iter = self.list_treeview_model.iter_next(iter)
		return games
	
	def toggle_all_images_download_toolbutton(self):
		if self.quitting == True:
			return
		gtk.gdk.threads_enter()
		if self.all_images_download_toolbutton.get_stock_id() == gtk.STOCK_JUMP_TO:
			# switch to cancel button
			self.all_images_download_toolbutton.set_stock_id(gtk.STOCK_CANCEL)
			self.all_images_download_menuitem.set_image(gtk.image_new_from_stock(gtk.STOCK_CANCEL, gtk.ICON_SIZE_MENU))
			self.old_aidt_tooltip_text = self.all_images_download_toolbutton.get_tooltip_text()
			self.all_images_download_toolbutton.set_tooltip_text(_("Stop download.") + " (Ctrl+D)")
		else:
			# restore original button
			self.all_images_download_toolbutton.set_stock_id(gtk.STOCK_JUMP_TO)
			self.all_images_download_menuitem.set_image(gtk.image_new_from_stock(gtk.STOCK_JUMP_TO, gtk.ICON_SIZE_MENU))
			self.all_images_download_toolbutton.set_tooltip_text(self.old_aidt_tooltip_text)
		gtk.gdk.threads_leave()
	
	def toggle_rebuild_roms_archives_toolbutton(self):
		if self.quitting == True:
			return
		gtk.gdk.threads_enter()
		if self.rebuild_roms_archives_toolbutton.get_stock_id() == gtk.STOCK_DIALOG_WARNING:
			# switch to cancel button
			self.rebuild_roms_archives_toolbutton.set_stock_id(gtk.STOCK_CANCEL)
			self.rebuild_roms_archives_menuitem.set_image(gtk.image_new_from_stock(gtk.STOCK_CANCEL, gtk.ICON_SIZE_MENU))
			self.old_rrat_tooltip_text = self.rebuild_roms_archives_toolbutton.get_tooltip_text()
			self.rebuild_roms_archives_toolbutton.set_tooltip_text(_("Stop rebuild.") + " (Ctrl+F)")
			self.rebuild_roms_archives_toolbutton.set_sensitive(True)
			self.rebuild_roms_archives_menuitem.set_sensitive(True)
		else:
			# restore original button
			self.rebuild_roms_archives_toolbutton.set_stock_id(gtk.STOCK_DIALOG_WARNING)
			self.rebuild_roms_archives_menuitem.set_image(gtk.image_new_from_stock(gtk.STOCK_DIALOG_WARNING, gtk.ICON_SIZE_MENU))
			self.rebuild_roms_archives_toolbutton.set_tooltip_text(self.old_rrat_tooltip_text)
		gtk.gdk.threads_leave()
		
	
	def open_db(self):
		""" Open database """
		self.db = DB(DB_FILE)
	
	def add_games(self, threads = True):
		""" Add games from database to the treeview model. """
		if self.quitting == True:
			return
		# Populate checksums dictionary
		try:
			crcs = self.db.get_all_games_crc()
		except:
			self.open_db()
			crcs = self.db.get_all_games_crc()
		
		self.checksums = {}
		for crc in crcs:
			self.checksums[crc[0]] = None
		
		## Check the games we have on disk
		self.update_statusbar("Games", _("Checking games on disk..."), threads)
		
		# check in 'unknown_roms_path' directory for new roms.
		# If found, move them in 'new_roms_path' directory.
		for file in glob.iglob(os.path.join(config.get_option("unknown_roms_path"), "*")):
			if file[len(file)-4:].lower() == ".zip":
				crc = get_crc32_zip(file)
				if crc != None and crc in self.checksums:
					shutil.move(file, config.get_option("new_roms_path"))	  
		
		# recursively check games in 'roms_path' directory.
		# unknown roms are moved in 'unknown_roms_path' directory. 
		paths_to_check = []
		paths_to_check.append(config.get_option("roms_path"))
		paths_to_check.append(config.get_option("new_roms_path"))
		while len(paths_to_check) != 0:
			next_path = paths_to_check[0]
			for file in glob.iglob(os.path.join(next_path, "*")):
				if os.path.isdir(file) and file != config.get_option("unknown_roms_path"):
					addpath = True
					for path in paths_to_check:
						if path == file:
							addpath = False
							break
					if addpath:
						paths_to_check.append(file)
				if file[len(file)-4:].lower() == ".zip":
					crc = get_crc32_zip(file)
					if crc != None:
						if crc in self.checksums:
							self.checksums[crc] = file
						else:
							shutil.move(file, config.get_option("unknown_roms_path"))
			paths_to_check[0:1] = []
	
		self.deactivate_widgets()
		self.update_statusbar("Games", _("Loading games list..."), threads)
		try:
			self.__update_list(self.db.get_all_games())
		except:
			self.open_db()
			self.__update_list(self.db.get_all_games())
			
		# Look for games to be fixed
		self.games_to_be_fixed = self.get_games_to_be_fixed()
		
		self.update_statusbar("Games", _("Games list loaded."), threads)
		
		self.activate_widgets()
		
		# Clear up all filter
		if self.quitting == False:		
			self.filter_name_entry.handler_block(self.fne_sid)
			self.filter_location_combobox.handler_block(self.flocc_sid)
			self.filter_language_combobox.handler_block(self.flanc_sid)
			self.filter_size_combobox.handler_block(self.fsc_sid)
			self.filter_clear_button.clicked()
			self.filter_name_entry.handler_unblock(self.fne_sid)
			self.filter_location_combobox.handler_unblock(self.flocc_sid)
			self.filter_language_combobox.handler_unblock(self.flanc_sid)
			self.filter_size_combobox.handler_unblock(self.fsc_sid)
		
		# Hide old infos
		self.__hide_infos()
	
	def quit(self):
		# Prepare for quitting
		self.quitting = True
		# Save config file
		config.save()
		
		for thread in self.threads:
			if thread.isAlive() and thread.getName() != "Gui":
				thread.stop()
		gtk.main_quit()
