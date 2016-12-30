#!/usr/bin/env python
#-*- coding: utf-8 -*- 
import sys
import os
import shutil
import httplib2
from bs4 import BeautifulSoup
import pdb



def download(uri):
    
    h = httplib2.Http()
    resp, content = h.request(uri, 'GET')
    if resp.status == 200:
        content_type =  resp['content-type']
        if r'text/html' in content_type:
            soup = BeautifulSoup(content)
            tags = soup.find_all('a')
            for each in tags:
                link = each.attrs['href']
                if not link.startswith('..'):
                    #print os.path.join(uri, link)
                    download(os.path.join(uri, link))
        else:
            write_path = uri.replace(start_uri, '')
            _dir = os.path.dirname(write_path)
            if not os.path.exists(_dir):
                os.makedirs(_dir)
            with open(write_path, 'w') as f:
                print '[-] {}'.format(write_path)
                f.write(content)

    else:
        print 'get {} failed'.format(uri)


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    start_uri = r'http://mirrors.163.com/centos/7.2.1511/'
    #start_uri = r'http://mirrors.163.com/centos/7.2.1511/os/x86_64/Packages/389-ds-base-1.3.4.0-19.el7.x86_64.rpm'
    download(start_uri)

