#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 26 07:00:33 2016

@author: pavel
"""
import concurrent.futures
import time

from urllib.request import urlopen
from ipaddress import IPv4Network

TIMEOUT = 2 #seconds
SLEEP_TIME=1
BYTES_TO_READ = 200
NUM_WORKERS = 3 #threads

UDPXY_URL = "http://192.168.0.200:4022/udp/"
RANGES_WIDE = ["233.26.128.0/17", "232.1.0.0/17", "233.30.128.0/17", "225.78.0.0/17", "233.31.128.0/17"]
RANGES_NARROW = ["233.31.198.0/24",]#"225.78.52.0/24", "233.26.198.0/24", "232.1.0.0/24", "232.1.10.0/24", "233.30.198.0/24"]

RANGES = RANGES_NARROW


PORT = "5000"

COUNT_FILE = "scan_status.txt"
UPDATE_COUNT_FILE_EVERY = 100
TEMP_FILE = "scan_iptv.txt"
OUTPUT_PLAYLIST = "scan_iptv.m3u"

HEADER = "#EXTM3U"
TITLE = "#EXTINF:-1,Unknown_"
END_LINE = "\r\n"

def check_url(url, timeout, bytes_to_read):
    try:
        with urlopen(url, timeout = timeout) as f:
            f.read(bytes_to_read)
            return True
    except:
        return False

def get_url(ip_addr):
    return UDPXY_URL + ip_addr +  ":" + PORT

def check_channel(ip_addr):
    url = get_url(ip_addr)
    return url, check_url(url, TIMEOUT, BYTES_TO_READ)
    
def addresses(skip = 0):
    count = 0
    for addr in RANGES:
        ip_network = IPv4Network(addr)
        for ip_addr in ip_network.hosts():            
            if count < skip:
                count += 1
            else:
                yield ip_addr.exploded

def num_scanned():
    count = 0
    try:
        with open(COUNT_FILE, 'r') as f:
            for line in f:
                count = max(count, int(line.strip()))
    except:
        pass
    return count
    
def scan_parallel():
    skip = num_scanned()
    count = skip
    
    with open(COUNT_FILE, 'w') as count_file:
        with open(TEMP_FILE, 'a') as output:
            with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
                future_to_ch = {executor.submit(check_channel, ip_addr): ip_addr for ip_addr in addresses(skip)}
                for future in concurrent.futures.as_completed(future_to_ch):
                    ip_addr = future_to_ch[future]
                
                    count += 1
                    if count % UPDATE_COUNT_FILE_EVERY == 0:
                        count_file.write(str(count)+END_LINE)
                        count_file.flush()
                        print(count, ip_addr)
                    
                    
                    url, status_ok = future.result()
                    if status_ok:
                        output.write(url + END_LINE)
                        output.flush()
                    
        
        
def scan():
    skip = num_scanned()
    count = skip
    
    with open(COUNT_FILE, 'w') as count_file:
        with open(TEMP_FILE, 'a') as output:
            for ip_addr in addresses(skip):
                count += 1
                if count % UPDATE_COUNT_FILE_EVERY == 0:
                    count_file.write(str(count)+END_LINE)
                    count_file.flush()
                    print(count, ip_addr)
                
                url, status_ok = check_channel(ip_addr)
                if status_ok:
                    output.write(url + END_LINE)
                    output.flush()
                time.sleep(SLEEP_TIME)    

def to_m3u():
    with open(TEMP_FILE, "r") as input_file:
        with open(OUTPUT_PLAYLIST, "w") as output_file:
            output_file.write(HEADER + END_LINE)
            
            count = 0
            for line in input_file:
                output_file.write(TITLE + str(count) + END_LINE)
                output_file.write(line.strip() + END_LINE)
                count += 1

if __name__ == "__main__":
    # execute only if run as a script
    #scan_parallel()	
    scan() 
    to_m3u()
