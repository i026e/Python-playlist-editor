#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Created on Wed Apr 27 09:56:31 2016

@author: pavel
"""
import os
from sys import argv

import mconfig as conf
OUTPUT_FILE = "add.txt" #/usr/share/freetuxtv/tv_channels.xml

pattern = """
	<tvchannel name="{channel_name}">
		<logo_filename>{logo_name}</logo_filename>
	</tvchannel>
 """

def get_icons(folder):
    icons = {}
    for f_name in os.listdir(folder):
        path = os.path.join(folder, f_name)
        
        if os.path.isfile(path):
            channel_name = os.path.splitext( os.path.basename(f_name))[0]
            icons[channel_name] = f_name
    return icons  



def main(*args):
    icons  = get_icons(conf.ICONS_FOLDER)
    with open(OUTPUT_FILE, "w") as output:
        for channel_name, f_name in icons.items():
            s = pattern.format(channel_name=channel_name, logo_name = f_name)
            output.write(s)
        
    print(args)


if __name__ == "__main__":
    # execute only if run as a script
    main(argv)
