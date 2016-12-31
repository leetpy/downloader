#!/usr/bin/env python
#-*- coding: utf-8 -*- 
import sys
import os
import shutil
import httplib2
import threading
import Queue
from bs4 import BeautifulSoup
import pdb
import time
import commands


class DownloadThread(threading.Thread):
    def __init__(self, uri, base_uri, queue):
        super(DownloadThread, self).__init__()
        self.uri = uri
        self.base_uri = base_uri
        self.queue = queue

    def run(self):
        print '[+] {}'.format(self.uri)
        h = httplib2.Http()
        resp, content = h.request(self.uri, 'GET')
        if resp.status == 200:
            content_type = resp['content-type']
            if r'text/html' in content_type:
                soup = BeautifulSoup(content)
                tags = soup.find_all('a')
                for each in tags:
                    link = each.attrs['href']
                    if not link.startswith('..'):
                        self.queue.put(os.path.join(self.uri, link))
            else:
                file_path = self.uri.replace(self.base_uri, '')
                if file_path.startswith('/'):
                    file_path = file_path[1:]
                save_file(file_path, content)


def save_file(file_path, content):
    target_dir = os.path.dirname(file_path)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    with open(file_path, 'w') as f:
        print '[-] {}'.format(file_path)
        f.write(content)


def start_download(queue, base_uri):
    while not queue.empty():
        uri = queue.get()
        dl = DownloadThread(uri, base_uri, queue)
        dl.start()
        dl.join()


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    start_uri = r'http://mirrors.163.com/centos/7.2.1511/atomic'
    
    queue = Queue.Queue()
    queue.put(start_uri)
    start_download(queue, start_uri)
    #start_uri = r'http://mirrors.163.com/centos/7.2.1511/os/x86_64/Packages/389-ds-base-1.3.4.0-19.el7.x86_64.rpm'
    # download(start_uri)


