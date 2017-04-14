#!/usr/bin/env python
import argparse
from bs4 import BeautifulSoup
import multiprocessing
import os
import Queue
import requests
import time
import threading
from urlparse import urlparse


def ensure_tree(path):
    if os.path.isdir(path):
        return
    try:
        os.makedirs(path)
    except:
        pass


def get_page_links(parent_url, page, jobs):
    soup = BeautifulSoup(page)
    hrefs = soup.findAll('a')
    for i in hrefs:
        lk = i.attrs['href']
        if not lk.startswith('..') and not lk == './':
            if lk.startswith('http') or lk.startswith('https'):
                jobs.put(lk)
            else:
                jobs.put(os.path.join(parent_url, lk))


def download(url, jobs):
    parts = urlparse(url)
    output = parts.path
    if output.startswith('/'):
        output = output[1:]
    if os.path.exists(output):
        return True, url
    try:
        r = requests.get(url, stream=True)
        content_type = r.headers.get('Content-Type')
        if content_type.lower() == 'text/html':
            links = get_page_links(url, r.content, jobs)
        else:
            path = os.path.dirname(output)
            ensure_tree(path)
            with open(output, 'wb') as hanle:
                if not r.ok:
                    print "download fail"
    
                for block in r.iter_content(1024):
                    hanle.write(block)
            
        # print "[x] %s" % output
        return True, url
    except:
        return False, url
    


def create_threads(jobs, results, concurrency):
    for _ in range(concurrency):
        thread = threading.Thread(target=worker, args=(jobs, results))

    thread.daemon = True
    thread.start()


def worker(jobs, results):
    while True:
        try:
            url = jobs.get()
            ok, result = download(url, jobs)
            if not ok:
                print "download %s not ok" % url
            else:
                results.put(result)
        finally:
            jobs.task_done()


def process(todo, jobs, results, concurrency):
    cancled = False
    try:
        jobs.join()
    except KeyboardInterrupt:
        cancled = True
    if cancled:
        done = results.qsize()
    else:
        print "task done"


def handle_commandline():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--concurrency', type=int,
                        default=multiprocessing.cpu_count()*4,
                        help='specify the concurrency')
    parser.add_argument('-f', '--file',
                        help='specify start file')
    args = parser.parse_args()
    return args.concurrency, args.file


def add_jobs(filename, jobs):
    with open(filename) as fp:
        lines = fp.readlines()
        for url in lines:
            jobs.put(url.strip())


if __name__ == '__main__':
    t1 = time.time()
    concurrency, filename = handle_commandline()
    jobs = Queue.Queue()
    results = Queue.Queue()
    create_threads(jobs, results, concurrency)
    todo = add_jobs(filename, jobs)
    process(todo, jobs, results, concurrency)
    t2 = time.time()
    print t2 - t1
