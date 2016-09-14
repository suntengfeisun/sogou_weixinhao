# -*- coding: utf-8 -*-

import sys
import csv
import platform
import requests
import time
from config import Config
from headers import Headers
from lxml import etree
from selenium import webdriver
from multiprocessing.dummy import Pool as ThreadPool
from mysqldao import MysqlDao
import random


def getWeixinhaoList():
    if 'Windows' in platform.system():
        csv_path = ''
    else:
        csv_path = Config.headers_path
    csv_file = file(csv_path + 'weixinhao.csv', 'rb')
    csv_content = csv.reader(csv_file)
    weixinhao_list = []
    for c in csv_content:
        if len(c) > 0:
            weixinhao_list.append(c[0])
    csv_file.close()
    return weixinhao_list


def getWeixinhaoUrl(weixinhao):
    n = 1
    while True:
        if n > 1:
            break
        url = 'http://weixin.sogou.com/weixin?type=1&query=' + weixinhao
        print(url)
        headers = Headers().getHeaders()
        req = requests.get(url, headers=headers, timeout=30)
        if req.status_code == 200:
            html = req.content
            selector = etree.HTML(html)
            weixinhao_urls = selector.xpath('//div[@class="wx-rb bg-blue wx-rb_v1 _item"][1]/@href')
            if len(weixinhao_urls) > 0:
                break
            else:
                print(html)
                print('sleep' + str(10 * n))
                time.sleep(10 * n)
                n = n + 1
    if len(weixinhao_urls) > 0:
        weixinhao_url = weixinhao_urls[0]
        print(weixinhao_url)
        """
        帅呆了,phantomjs添加头请求动态网页
        """
        cap = webdriver.DesiredCapabilities.PHANTOMJS
        cap['phantomjs.page.customHeaders.Referer'] = headers['Referer']
        cap['phantomjs.page.settings.userAgent'] = headers['User-Agent']
        cap['phantomjs.page.settings.resourceTimeout'] = '1000'
        driver = webdriver.PhantomJS(service_args=['--load-images=no'], desired_capabilities=cap)
        driver.get(weixinhao_url)
        html = driver.page_source
        driver.close()
        selector = etree.HTML(html)
        urls = selector.xpath('//*[@class="weui_media_title"]/@hrefs')
        ret = []
        for url in urls:
            time.sleep(1)
            url = 'http://mp.weixin.qq.com' + url
            print(url)
            saveWeixinhaoContent((weixinhao, url))
            # return ret


def saveWeixinhaoContent(content_url):
    author = content_url[0]
    url = content_url[1]
    headers = Headers().getHeaders()
    req = requests.get(url, headers=headers, timeout=20)
    html = req.content
    selector = etree.HTML(html)
    titles = selector.xpath('//title/text()')
    contents = selector.xpath('//*[contains(@class,"rich_media_content")]/descendant::text()')
    imgs = selector.xpath('//*[contains(@class,"rich_media_content")]/descendant::img/@data-src')
    times = selector.xpath('//*[contains(@id,"post-date")]/text()')
    if len(times) > 0:
        time_t = times[0]
    else:
        time_t = ''
    if len(titles) > 0:
        title = titles[0].replace('"', '').replace(' ', '')
        ct = ''
        ig = ''
        for content in contents:
            content = content.replace('"', '').replace('\n', '').replace('\t', '').replace('\r', '').replace(
                    ' ', '')
            if content != '':
                ct = ct + '{ycontent}' + content
        for img in imgs:
            ig = ig + '{yimg}' + img
        time_now = time.strftime('%Y-%m-%d %H:%M:%S')
        insert_value = '"' + title + '","' + ct + '","' + url + '","' + ig + '","' + author + '","' + time_t + '","' + time_now + '","' + time_now + '"';
        sql = 'insert ignore into weixinhao_content (`title`,`content`,`url`,`img`,`author`,`time`,`created_at`,`updated_at`) values (' + insert_value + ')'
        mysqlDao = MysqlDao()
        print(sql)
        mysqlDao.execute(sql)


if __name__ == '__main__':
    weixinhao_list = getWeixinhaoList()
    random.shuffle(weixinhao_list)
    for weixinhao in weixinhao_list:
        print(weixinhao)
        try:
            getWeixinhaoUrl(weixinhao)
        except:
            pass
        time.sleep(600)
