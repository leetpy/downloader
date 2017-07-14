#!/usr/bin/env python
# -*- coding: utf-8 -*-
import eventlet
import os
import requests
import time
import urlparse
from bs4 import BeautifulSoup


headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36',
    'Connection': 'keep-alive',
}

def get_pages(url, pages):
    zero_page = '{}?page={}'.format(url, 0)
    r = requests.get(zero_page, headers=headers)

    soup = BeautifulSoup(r.text, 'lxml')
    links = soup.findAll('a')
    sz_href = None
    for i in xrange(len(links)):
        if links[i].string == u'下一页':
            sz_href = links[i-1]
            break
    sz = int(sz_href.string)
    for i in xrange(sz):
        pages.put('{}?page={}'.format(url, i+1))


def get_questions(pages, questions):
    pool = eventlet.GreenPool()
    while True:
        while not pages.empty():
            page = pages.get()
            # print '[x] start page {}'.format(page)
            pool.spawn_n(get_questions_links, page, questions)
        pool.waitall()
        if pages.empty():
            break

def get_questions_links(page, questions):
    r = requests.get(page, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    links = soup.select('.zm-item-title a')
    for each in links:
        lk = urlparse.urljoin(page, each.get('href'))
        # print '[x] get questions link {}'.format(lk)
        questions.put(lk)


def get_imgs(questions, imgs):
    pool = eventlet.GreenPool()
    while True:
        while not imgs.empty():
            img = imgs.get()
            print '[x] start download {}'.format(img)
            pool.spawn_n(download_img, img)
        pool.waitall()
        if imgs.empty():
            break


def get_img_links(url, imgs):
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    links = soup.select('.RichContent-inner img')
    print links
    for each in links:
        lk = urlparse.urljoin(url, each.get('data-original'))
        print '[x] get image link {}'.format(lk)
        imgs.put(lk)


def download_img(url):
    name = url.split(r'/')[-1]
    img_path = os.path.join('img', name)
    r = requests.get(url, headers=headers)
    with open(img_path, 'w') as fp:
        fp.write(r.content)


def ensure_tree(path):
    if os.path.isdir(path):
        return
    try:
        os.makedirs(path)
    except:
        pass

if __name__ == '__main__':

    t1 = time.time()
    start = 'https://www.zhihu.com/collection/69135664'
    ensure_tree('img')

    pages = eventlet.Queue()
    questions = eventlet.Queue()
    imgs = eventlet.Queue()

    get_pages(start, pages)
    get_questions(pages, questions)
    # time.sleep(10)
    print 'done stage 1'
    get_imgs(questions, imgs)
    print 'done stage two'

    print time.time() - t1
