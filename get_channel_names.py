#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Created on Tue Apr 26 10:03:55 2016

@author: pavel
"""
import urllib.request as urllib2
import xml.etree.ElementTree as ET

import gzip
import os

import mconfig as conf

from urllib.parse import urlparse

def download(url, path):
    remote = urllib2.urlopen(url)
    with open(path, 'wb') as output:
        output.write(remote.read())
 
def extract(gz_file, output_file):    
    with gzip.open(gz_file) as gz:
        with open(output_file, "wb") as output:
            output.write(gz.read())

   
def get_path(folder, name, ext):    
    return os.path.join(folder, name + "." + ext)

def get_path_from_url(folder, url, name= None):
    path = urlparse(url).path
    if name is None:
        name = os.path.basename(path)
    else:
        name = name + os.path.splitext(path)[-1]
    return os.path.join(folder, name )
    

def get_channels(xml_file_path):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    print(root.tag)
    
    
    channels = {}
    
    for child in root:
        if child.tag == "channel":
            name = ""
            icon_url = None
            for element in child:
                if element.tag == "display-name":
                    name = element.text
                elif element.tag == "icon":
                    icon_url = element.attrib["src"]
            channels[name] = icon_url
    return channels

def save_channels_and_icons(channels, channels_file, icon_folder):
    with open(channels_file, "w") as output:    
        for channel in channels:
            print(channel)
            
            output.write(channel.strip() + conf.NEW_LINE)
            
            url = channels[channel]
            if url is not None:
                path = get_path_from_url(icon_folder, url, channel)
                
                if os.path.isfile(path):
                    print(path, "exists")
                else:
                    print("download", url)
                    download(url, path)
    
    
def process():
    os.makedirs(conf.ICONS_FOLDER, exist_ok=True)
    os.makedirs(conf.TMP_FOLDER, exist_ok=True)
    
    gz_url = conf.URLS[conf.PROVIDER]
    gz_path = get_path_from_url(conf.TMP_FOLDER, gz_url)
    download(gz_url, gz_path)
    
    xml_path = get_path(conf.TMP_FOLDER, "xmltv", ext = "xml")
    
    extract(gz_path, xml_path)
    
    
    channels = get_channels(xml_path)
    
    save_channels_and_icons(channels, conf.CHANNELS_FILE, conf.ICONS_FOLDER)


if __name__ == "__main__":
#    # execute only if run as a script
    process()
