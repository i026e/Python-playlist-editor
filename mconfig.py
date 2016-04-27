#!/usr/bin/python3
# -*- coding: utf-8 -*-
NEW_LINE = "\r\n"
#where to get xml file with channel names
URLS = {"teleweb": "https://www.teleguide.info/download/new3/xmltv.xml.gz",
        "programtv" : "http://programtv.ru/xmltv.xml.gz"}
PROVIDER = "teleweb"
  
ICONS_FOLDER = "./icons" 
TMP_FOLDER = "./tmp"

#save channels list in
CHANNELS_FILE = "channels.txt" 

#playlist by default
PLAYLIST_FILE = "iptv.m3u"

#close player after
PLAYER_TIMEOUT = 5 #seconds
AUTOSAVE_PLAYLIST_ON_CLOSE = False