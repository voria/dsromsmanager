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

try:
	import gtk
	import gtk.glade
except:
	print "You have to install 'gtk' and 'gtk.glade' modules to run this application."
	from sys import exit
	exit(1)

from globals import *
from db import DB

from downloaders import *

gtk.gdk.threads_init()

class Gui(threading.Thread):
	""" Graphical User Interface """
	def __init__(self, threads):
		threading.Thread.__init__(self, name="Gui")
		
		self.threads = threads
		
		self.builder = gtk.Builder()
		self.builder.add_from_file(os.path.join(DATA_DIR, "drm.glade"))
		
		self.main_window = self.builder.get_object("main_window")
		self.dat_update_toolbutton = self.builder.get_object("dat_update_toolbutton")
		self.all_images_download_toolbutton = self.builder.get_object("all_images_download_toolbutton")
		self.show_review_toolbutton = self.builder.get_object("show_review_toolbutton")
		self.about_toolbutton = self.builder.get_object("about_toolbutton")
		self.list_treeview = self.builder.get_object("list_treeview")
		self.list_game_label = self.builder.get_object("list_games_label")
		self.image1 = self.builder.get_object("image1")
		self.image2 = self.builder.get_object("image2")
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
		
		
		self.main_window.set_title(APP_NAME + " - " + APP_VERSION)
		self.main_window_visible = True
		
		try:
			self.main_window.set_icon_from_file(os.path.join(DATA_IMG_DIR, "icon.png"))
		except:
			pass
		
		self.statusicon = gtk.StatusIcon()
		self.statusicon.set_from_file(os.path.join(DATA_IMG_DIR, "icon.png"))
		self.statusicon.set_tooltip(self.main_window.get_title())
		self.statusicon.set_visible(True)
		
		
		self.image1.clear()
		self.image2.clear()
		
		# Load flags images
		self.flags = []
		for i in countries_short.keys():
			file = os.path.join(DATA_IMG_DIR, countries_short[i].lower() + ".png")
			self.flags.append(gtk.gdk.pixbuf_new_from_file(file))
		
		# Setup all needed stuff for main list treeview
		self.list_treeview_model = gtk.ListStore(gtk.gdk.Pixbuf, int, str)
		self.list_treeview.set_model(self.list_treeview_model)
		self.list_treeview_crt = gtk.CellRendererText()
		self.list_treeview_crt_img = gtk.CellRendererPixbuf()
		self.list_treeview_tvc1 = gtk.TreeViewColumn("Region", self.list_treeview_crt_img, pixbuf=0)
		self.list_treeview.append_column(self.list_treeview_tvc1)
		self.list_treeview_tvc2 = gtk.TreeViewColumn("#", self.list_treeview_crt, text=1)
		self.list_treeview_tvc2.set_sort_column_id(1)
		self.list_treeview.append_column(self.list_treeview_tvc2)
		self.list_treeview_tvc3 = gtk.TreeViewColumn("Name", self.list_treeview_crt, text=2)
		self.list_treeview_tvc3.set_sort_column_id(2)
		self.list_treeview.append_column(self.list_treeview_tvc3)
		
		# Setup all needed stuff for location combobox
		self.filter_location_model = gtk.ListStore(str)
		self.filter_location_combobox.set_model(self.filter_location_model)
		self.filter_location_crt = gtk.CellRendererText()
		self.filter_location_combobox.pack_start(self.filter_location_crt)
		self.filter_location_combobox.add_attribute(self.filter_location_crt, 'text', 0)  
		self.filter_location_model.append(["All"])
		for i in countries.keys():
			self.filter_location_model.append([countries[i]])
		self.filter_location_combobox.set_active(0)
		
		# Setup all needed stuff for language combobox
		self.filter_language_model = gtk.ListStore(str)
		self.filter_language_combobox.set_model(self.filter_language_model)
		self.filter_language_crt = gtk.CellRendererText()
		self.filter_language_combobox.pack_start(self.filter_language_crt)
		self.filter_language_combobox.add_attribute(self.filter_language_crt, 'text', 0)  
		self.filter_language_model.append(["All"])
		for i in langs.keys():
			if langs[i] != "Unknown":
				self.filter_language_model.append([langs[i]])
		self.filter_language_combobox.set_active(0)
		
		# Setup all needed stuff for size combobox
		self.filter_size_model = gtk.ListStore(str)
		self.filter_size_combobox.set_model(self.filter_size_model)
		self.filter_size_crt = gtk.CellRendererText()
		self.filter_size_combobox.pack_start(self.filter_size_crt)
		self.filter_size_combobox.add_attribute(self.filter_size_crt, 'text', 0)  
		self.filter_size_model.append(["All"])
		for size in sizes:
			self.filter_size_model.append([size])
		self.filter_size_combobox.set_active(0)
		
		# Connect signals
		self.main_window.connect("delete_event", self.on_main_window_delete_event)
		self.statusicon.connect('activate', self.on_statusicon_activate)
		self.statusbar.connect("text-pushed", self.on_statusbar_text_pushed)
		self.dat_update_toolbutton.connect("clicked", self.on_dat_update_toolbutton_clicked)
		self.filter_clear_button.connect("clicked", self.on_filter_clear_button_clicked)
		self.about_toolbutton.connect("clicked", self.on_about_toolbutton_clicked)
		self.about_dialog.connect("response", self.on_about_dialog_response)
		self.list_treeview.connect("cursor-changed", self.on_list_treeview_cursor_changed)
		self.show_review_toolbutton.connect("clicked", self.on_show_review_toolbutton_clicked)
		# We need signal id for the following signals
		self.fne_sid = self.filter_name_entry.connect("changed",self.on_filter_triggered)
		self.flocc_sid = self.filter_location_combobox.connect("changed", self.on_filter_triggered)
		self.flanc_sid = self.filter_language_combobox.connect("changed", self.on_filter_triggered)
		self.fsc_sid = self.filter_size_combobox.connect("changed", self.on_filter_triggered)
		self.aidtb_sid = self.all_images_download_toolbutton.connect("clicked", self.on_all_images_download_toolbutton_clicked)
		
		self.__deactivate_widgets()
		
		self.games = []
		self.db = None
		
	def run(self):
		gtk.main()
	
	def stop(self):
		self.quit()
	
	def __prepare_db(self):
		""" Create games' database if it does not exist """
		if self.db == None:
			self.db = DB()
			self.db.adds(self.games)
	
	def __update_list(self, games):
		""" List 'games' in treeview """
		num = 0
		self.list_treeview_model.clear()
		for game in reversed(games):
			region = game.get_location_index()
			flag = self.flags[countries_short.keys().index(region)]
			relnum = game.get_release_number()
			title = game.get_title()
			self.list_treeview_model.append((flag, relnum, title))
			num += 1
		if num != 0:
			self.list_game_label.set_text(str(num) + " games in list")
		else:
			self.list_game_label.set_text("No games in list")
	
	def __update_list_from_db(self, games):
		""" List 'games' infos (taken from database) in treeview """
		num = 0
		self.list_treeview_model.clear()
		for game in reversed(games):
			relnum = game[1]
			region = game[8]
			key = -1
			for i in countries_short.keys():
				if countries_short[i] == region:
					key = i
					break
			flag = self.flags[countries_short.keys().index(key)]
			title = game[2]
			self.list_treeview_model.append((flag, relnum, title))
			num += 1
		if num != 0:
			self.list_game_label.set_text(str(num) + " games in list")
		else:
			self.list_game_label.set_text("No games in list")
		self.list_treeview.set_cursor(0)
	
	def __filter(self):
		""" Filter list by all criteria """
		self.__prepare_db()
				
		self.__hide_infos()
		
		string = self.filter_name_entry.get_text()
		location_iter = self.filter_location_combobox.get_active_iter()
		location = self.filter_location_model.get_value(location_iter, 0)
		language_iter = self.filter_language_combobox.get_active_iter()
		language = self.filter_language_model.get_value(language_iter, 0)
		size_iter = self.filter_size_combobox.get_active_iter()
		size = self.filter_size_model.get_value(size_iter, 0)
		self.__update_list_from_db(self.db.filter_by(string, location, language, size))
		self.show_review_toolbutton.set_sensitive(False)
	
	def __deactivate_widgets(self):
		""" Disable all widgets' sensitiveness """
		self.list_treeview.set_sensitive(False)
		self.dat_update_toolbutton.set_sensitive(False)
		self.all_images_download_toolbutton.set_sensitive(False)
		self.show_review_toolbutton.set_sensitive(False)
		self.filter_name_entry.set_sensitive(False)
		self.filter_clear_button.set_sensitive(False)
		self.filter_location_combobox.set_sensitive(False)
		self.filter_language_combobox.set_sensitive(False)
		self.filter_size_combobox.set_sensitive(False)
	
	def __activate_widgets(self):
		""" Enable all widgets' sensitiveness """
		self.list_treeview.set_sensitive(True)
		self.dat_update_toolbutton.set_sensitive(True)
		self.all_images_download_toolbutton.set_sensitive(True)
		self.filter_name_entry.set_sensitive(True)
		self.filter_clear_button.set_sensitive(True)
		self.filter_location_combobox.set_sensitive(True)
		self.filter_language_combobox.set_sensitive(True)
		self.filter_size_combobox.set_sensitive(True)
	
	def __hide_infos(self):
		""" Hide game's info """
		self.images_hbox.hide()
		self.info_title_label.hide()
		self.info_label_vbox.hide()
	
	def __show_infos(self):
		""" Show game's info """
		self.images_hbox.show()
		self.info_title_label.show()
		self.info_label_vbox.show()
	
	# Callback functions
	def on_main_window_delete_event(self, window, event):
		self.quit()
	
	def on_statusicon_activate(self, statusicon):
		if self.main_window_visible:
			self.main_window.hide()
			self.main_window_visible = False
		else:
			self.main_window.show()
			self.main_window_visible = True
	
	def on_statusbar_text_pushed(self, statusbar, context_id, text):
		self.statusicon.set_tooltip(APP_NAME + " - " + text)
	
	def on_list_treeview_cursor_changed(self, treeview):
		self.__prepare_db()
		selection = treeview.get_selection()
		model, iter = selection.get_selected()
		
		try:
			relnum = model.get_value(iter, 1)
		except: # model is empty
			return
		
		game = self.games[relnum-1]
		
		# Show images if available, or else download them
		img1 = os.path.join(IMG_DIR, game.get_img1_local())
		img2 = os.path.join(IMG_DIR, game.get_img2_local())	
		
		if os.path.exists(img1) and os.path.exists(img2):
			self.image1.set_from_file(img1)
			self.image2.set_from_file(img2)
		else:
			self.image1.clear()
			self.image2.clear()
			thread = ImagesDownloader(self, game)
			thread.start()
		
		# Search for duplicates
		duplicates = []
		id = game.get_duplicate_id()
		relnum = game.get_release_number()
		if id != 0: # Games with id == 0 have no duplicates
			for g in self.games:
				if g.get_duplicate_id() == id and g.get_release_number() != relnum:
					duplicates.append(str(g))
		
		if len(duplicates) != 0:
			text = "Duplicates:"
			for d in duplicates:
				text += "\n" + d
				self.info_title_label.set_tooltip_text(text)
		else:
			self.info_title_label.set_tooltip_text("No duplicates")
		
		
		# Show informations
		#self.info_title_label.set_text(str(game))
		title = str(game).replace("&", "&amp;")
		self.info_title_label.set_markup("<span size=\"x-large\" weight=\"bold\">" + title + "</span>")
		self.info_location_label.set_text(game.get_location())
		self.info_publisher_label.set_text(game.get_publisher())
		self.info_source_label.set_text(game.get_source_rom())
		self.info_save_label.set_text(game.get_save_type())
		size = game.get_rom_size()/1048576
		self.info_size_label.set_text(str(size) + " MB")
		self.info_comment_label.set_text(game.get_comment())
		self.info_crc_label.set_text(game.get_rom_crc())
		self.info_language_label.set_text(game.get_language())
		
		self.show_review_toolbutton.set_sensitive(True)
		self.__show_infos()
	
	def on_show_review_toolbutton_clicked(self, button):
		selection = self.list_treeview.get_selection()
		model, iter = selection.get_selected()
		relnum = model.get_value(iter, 1)
		title = self.games[relnum-1].get_title()
		title = title.replace("&", " ")
		url = "http://www.google.com/search?hl=en&q="
		url += title + " NDS site:metacritic.com" 
		url += "&btnI=I%27m+Feeling+Lucky&aq=f&oq="
		import webbrowser
		webbrowser.open(url)
	
	def on_dat_update_toolbutton_clicked(self, button):
		thread = DatUpdater(self, self.dat.get_version(), self.dat.get_version_url())
		self.threads.append(thread)
		thread.start()
	
	def on_all_images_download_toolbutton_clicked(self, button):
		if button.get_stock_id() == gtk.STOCK_JUMP_TO:
			if len(self.games) == 0:
				return
			aid = AllImagesDownloader(self, self.games)
			self.threads.append(aid)
			aid.start()
		else: # stop images downloading
			for thread in self.threads:
				if thread.isAlive() and thread.getName() == "AllImagesDownloader":
					thread.stop()
					while thread.isAlive(): # wait while the thread finishs its job 
						pass
					break
			self.statusbar.push(self.statusbar.get_context_id("AllImagesDownloader"), "Download of all images stopped")
	
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
			
		if filter == 0: # No need to clear anything
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
	
	def on_about_toolbutton_clicked(self, menuitem):
		self.about_dialog.run()
	
	def on_about_dialog_response(self, dialog, response_id):
		dialog.hide()
			
	# General functions
	def show_info_dialog(self, message):
		""" Show an info dialog with just an OK button, showing 'message' """
		gtk.gdk.threads_enter()
		dialog = gtk.MessageDialog(self.main_window, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, message)
		dialog.run()
		dialog.destroy()
		gtk.gdk.threads_leave()
		
	def update_statusbar(self, context, text):
		gtk.gdk.threads_enter()
		self.statusbar.push(self.statusbar.get_context_id(context), text)
		gtk.gdk.threads_leave()
	
	def update_image(self, game_release_number, image_index, filename):
		""" Update showed image if needed """
		gtk.gdk.threads_enter()
		selection = self.list_treeview.get_selection()
		model, iter = selection.get_selected()
		try:
			if model.get_value(iter, 1) == game_release_number:
				if image_index == 1:
					self.image1.set_from_file(filename)
				else:
					self.image2.set_from_file(filename)
		except:
			pass
		gtk.gdk.threads_leave()
	
	def toggle_all_images_download_toolbutton(self):
		if self.all_images_download_toolbutton.get_stock_id() == gtk.STOCK_JUMP_TO:
			# switch to cancel button
			self.all_images_download_toolbutton.set_stock_id(gtk.STOCK_CANCEL)
			self.all_images_download_toolbutton.set_label("Stop images download")
		else:
			# restore original button
			self.all_images_download_toolbutton.set_stock_id(gtk.STOCK_JUMP_TO)
			self.all_images_download_toolbutton.set_label("Download all images")
	
	def add(self, dat):
		""" Add games from 'dat' to the treeview model.
		This function must be used only once per DAT file """
		self.db = None
		self.dat = dat
		self.games = self.dat.get_games()
		self.__deactivate_widgets()
		self.__update_list(self.games)
		self.__activate_widgets()
		# Clear up all filter
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
		for thread in self.threads:
			if thread.isAlive() and thread.getName() != "Gui":
				thread.stop()
				thread.join()
		gtk.main_quit()
