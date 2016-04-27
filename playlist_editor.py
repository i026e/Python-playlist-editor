#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Created on Tue Apr 26 11:13:04 2016

@author: pavel
"""

import os

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, GObject



import mconfig as conf
from sys import argv


def get_channels_list(channels_file):
    channels = []
    with open(channels_file, "r") as f:
        for line in f:
            channels.append(line.strip())
    channels.sort()
    return channels

def backup(fname_src, fname_dst):
    with open(fname_src, "r") as src:
        with open(fname_dst, "w") as dst:
            dst.write(src.read())

def get_icons(folder):
    icons = {}
    for f_name in os.listdir(folder):
        path = os.path.join(folder, f_name)
        
        if os.path.isfile(path):
            channel_name = os.path.splitext( os.path.basename(f_name))[0]
            icons[channel_name] = path
    return icons  
    
class external_player:
    from subprocess import call
    PLAYER = "mplayer"
    
    def play(self, url):
        external_player.call([external_player.PLAYER, url])

class vlc_player:
    import time
    import vlc    
    
    def __init__(self):
        self.vlc_instance = vlc_player.vlc.Instance()
        self.player = None
    def play(self, url):
        self.playstop(url, conf.PLAYER_TIMEOUT)
        
    def playstop(self, url, timeout = None):
        if self.player is None:
            self._setup(url)
            self._start()
            if timeout is not None:
                vlc_player.time.sleep(timeout)
                self._stop()
            
        else:
            self._stop()
        
        
    def _setup(self, url):        
        self.media = self.vlc_instance.media_new(url)
        self.player = self.vlc_instance.media_player_new()
        self.player.set_media(self.media)
    def _start(self):
        if self.player is not None:
            self.player.play()
    def _stop(self):
        if self.player is not None:
            self.player.stop()
            self.player = None
            
class playlist:    
    HEADER = "#EXTM3U"
    TITLE = "#EXTINF:-1,"    
    TITLE_LEN = len(TITLE)
        
    def __init__(self, filename):
        self.channels = []
        self.filename = filename
        
        try:
            with open(self.filename, "r") as f:
                name = None
                url = None
                for line in f:
                    if name is not None:
                        url = line.strip()
                        self.channels.append((name, url))
                        name = None
                    else:
                        ind = line.find(playlist.TITLE)
                        if ind != -1:
                            name = line[ind+playlist.TITLE_LEN:].strip()
        except FileNotFoundError:
            print("File does not exist")
    def clear(self):    
        self.channels = []
        #print(channels)
    def add(self, name, url):
        self.channels.append((name, url))
    
    def save(self):
        with open(self.filename, "w") as f:
            f.write(playlist.HEADER + conf.NEW_LINE)
            
            for (name, url) in self.channels:
                f.write(playlist.TITLE + name + conf.NEW_LINE)
                f.write(url + conf.NEW_LINE)
                


class playlist_editor:
    GLADE_FILE = "playlist_editor.glade"
    
    
    def __init__(self, playlist_, channels, icons, player):
        self.playlist_ = playlist_
        self.channels = channels
        self.icons = icons
        self.player = player
        
        self.builder = Gtk.Builder()
        self.builder.add_from_file(playlist_editor.GLADE_FILE)
        
        self._init_channels_panel()
        
        self._init_edit_panel()
        self._init_channels_autocomplete()
        
        
        self.builder.connect_signals(self)
        self.builder.get_object("application_window").show_all()
    
    
    
    def _init_channels_panel(self):
        self.pl_store = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_STRING)
        for channel in self.playlist_.channels:
            self.pl_store.append((channel[0], channel[1]))
        
        treeview = self.builder.get_object("channels_treeview")
        treeview.set_model(self.pl_store)
        
        
        column = Gtk.TreeViewColumn("channel and url")
        
        name = Gtk.CellRendererText()
        url = Gtk.CellRendererText()
        
        column.pack_start(name, True)
        column.pack_start(url, True)
        
        column.add_attribute(name,'text',0)
        column.add_attribute(url,'text',1)
        
        treeview.append_column(column)
        
        self.selected_model = None
        self.selected_iter = None
        
    def _init_edit_panel(self):
        self.name_edit = self.builder.get_object("name_entry")
        self.url_edit = self.builder.get_object("url_entry")
        self.channel_logo = self.builder.get_object("channel_logo")
        
    def _init_channels_autocomplete(self):
        ch_store = Gtk.ListStore(GObject.TYPE_STRING)
        for ch in self.channels:
            ch_store.append((ch, ))
        
        completion = Gtk.EntryCompletion()
        completion.set_model(ch_store)
        completion.set_text_column(0)
        
        self.name_edit.set_completion(completion)
    
    def _save_results(self):
        self.playlist_.clear()
        for name, url in self.pl_store:
            self.playlist_.add(name, url)
            #print(name, url)
        self.playlist_.save()
    
    def _update_logo(self, channel_name):
        if channel_name in self.icons:
            path = self.icons[channel_name]
            try:
                self.channel_logo.set_from_file(path)            
            except:
                pass
        else:
            self.channel_logo.set_from_stock("gtk-missing-image", 1)
        self.channel_logo.show()
    def on_application_window_destroy_event(self, *args):
        Gtk.main_quit()
    def on_application_window_delete_event(self, *args):
        if conf.AUTOSAVE_PLAYLIST_ON_CLOSE:
            self._save_results()
        Gtk.main_quit()
        
    def on_channelstreeview_selection_changed(self, selection):
        self.selected_model, self.selected_iter = selection.get_selected()
        if self.selected_iter != None:
            name = self.selected_model[self.selected_iter][0]
            url = self.selected_model[self.selected_iter][1]
            self.name_edit.set_text(name)
            self.url_edit.set_text(url)
            
            self._update_logo(name)
            #model[treeiter][0] = "Selected"
            #print("You selected", model[treeiter][0])

    def on_update_button_clicked(self, *args):
        if self.selected_iter != None:
            name = self.name_edit.get_text()
            url = self.url_edit.get_text()
            
            self.selected_model[self.selected_iter][0] = name
            self.selected_model[self.selected_iter][1] = url
            
            self._update_logo(name)
    def on_play_button_clicked(self, *args)  :
        url = self.url_edit.get_text()
        if url is not None and len(url) > 0:
            self.player.play(url)
    def on_save_all_button_clicked(self, *args):
        self._save_results()
        
def main(playlist_file=None):
    pl_in = playlist(conf.PLAYLIST_FILE) if playlist_file is None else \
                                            playlist(playlist_file)

    
    channels = get_channels_list(conf.CHANNELS_FILE)    
    
    icons = get_icons(conf.ICONS_FOLDER)
    player = vlc_player()
    #print(icons)
    
    editor = playlist_editor(pl_in, channels, icons, player)
    Gtk.main()


if __name__ == "__main__":
    # execute only if run as a script
    if len(argv) > 1:
        main(argv[1])
    else:    
        main()
