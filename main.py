#!/usr/bin/env python
# encoding: utf-8
import os
import requests
import sys
import threading
import urllib2
from Queue import Queue
from bs4 import BeautifulSoup


def ensure_tree(path):
    if os.path.isdir(path):
        return
    try:
        os.makedirs(path)
    except:
        pass


def add_link(jobs, content, url):
    soup = BeautifulSoup(content)
    hrefs = soup.findAll('a')
    alist = [i.attrs['href'] for i in hrefs]
    for each in alist:
        if each.startswith('..'):
            continue
        if each.startswith('http') or each.startswith('www'):
            jobs.put(each)
        else:
            jobs.put(os.path.join(url, each))


def download_to_file(url, start_url, jobs):
    print '[-] {}'.format(url)
    response = urllib2.urlopen(url)
    link_type = response.headers.getheader('content-type')
    if 'text/html' in link_type:
        add_link(jobs, response.read(), url)
    else:
        rel_link = url.replace(start_url, '')
        if rel_link.startswith('/'):
            rel_link = rel_link[1:]
        dl_dir, dl_name = os.path.split(rel_link)
        ensure_tree(dl_dir)
        CHUNK = 1024
        with open(rel_link, 'wb') as f:
            while True:
                chunk = response.read(CHUNK)
                if not chunk:
                    break
                f.write(chunk)


def get_page_type(url):
    req = requests.head()
    response = urllib2.urlopen(url)


def create_threads(jobs, concurrency, start_url):
    for _ in xrange(concurrency):
        thread = threading.Thread(target=worker, args=(jobs, start_url,))
        thread.daemon = True
        thread.start()


def worker(jobs, start_url):
    while True:
        try:
            link = jobs.get()
            download_to_file(link, start_url, jobs)
        finally:
            jobs.task_done()


def process(jobs):
    try:
        jobs.join()
    except KeyboardInterrupt:
        sys.exit(1)


if __name__ == '__main__':
    start_url = r'http://mirrors.163.com/centos/7.2.1511/'

    jobs = Queue()
    create_threads(jobs, 8, start_url)

    jobs.put(start_url)

    process(jobs)

