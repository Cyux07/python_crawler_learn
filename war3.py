# coding=utf-8
# 准备做爬取杂志扫图，
# 要点：这个网站有移动端适配，移动端浏览不限制，
# 但是pc端浏览多了会要求登陆，并且有滑块验证
# 列表页：div class="n5_tpbk cl"
#            div class="n5_tpbkn cl"
#               a href="forum.php?mod=viewthread&tid=293512&extra=page%3D1" class="n5_tpbki"
#                   img alt=""(标题)

#详情页：div class="postlist n5-bbsnr"
#           <h2>"标题内容"</h2>
#           div class="plc cl"
#               div class="display pi"
#                   div class="message"
#                       div class="IndexImgDiv"
#                           div class="IndexImgDiv_1"
#                               div class="IndexImgDiv_4"
#                                   a class="orange"
#                                       img id="" src="" alt="" title=""

#http://www.taotushe.cc/forum.php?mod=forumdisplay&fid=97&mobile=2 (即第一页)(moblie=1脑年人界面)
#or http://www.taotushe.cc/forum.php?mod=forumdisplay&fid=97&page=1（page=1~130）
#headers里：referer：http://www.taotushe.cc/forum.php?mod=forumdisplay&fid=97&mobile=2

import requests
import os
import time
from bs4 import BeautifulSoup

class Magazine:
    local_path = 'E:\\M&M\\CrawlerMagazine\\%s'

    def __init__(self, local=local_path, web=None):
        self.file_url = local
        self.root_url = web
        self.headers = {"User-Agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Mobile Safari/537.36"}

    def doRequest(self, url):
        html = requests.get(url, headers = self.headers)
        return html.text

    #find every magazine in ONE page
    def doMageSoup(self, content):
        con_soup = BeautifulSoup(content, 'lxml')
        img_list = con_soup.find('div', class_="n5_tpbk cl").find_all('a', class_="n5_tpbki")
        #for item in img_list:
        #    #magazine name
        #    title = item.find('img')['alt']
        #    page = item.find('a')['href']
        #    yield page_html = self.doRequest(page)
        #return {'title' : item.find('img')['alt'],
        #    'link' : item.find('a')['href']} for item in img_list
        return (item['href'] for item in img_list if item is not None) #return tuple

    #TODO async
    #find every img in ONE magazine
    def doImgSoup(self, page):
        content = self.doRequest(self.root_url.format(page))
        con_soup = BeautifulSoup(content, 'lxml')

        #or con_soup.title.string
        #print(con_soup.find('div', class_='postlist n5-bbsnr'))
        title_head2 = con_soup.find('h2')
        title = title_head2.string.strip().replace("\r\n","")
        self.mkdir(title)

        img_list = con_soup.find('div', class_="message").find_all('img')
        for item in img_list:
            name = item['title']
            src = item['src']
            img = requests.get(src, headers = self.headers)
            self.writeToFile(name, img.content)

    def writeToFile(self, filename, content):
        f = open(filename, 'wb')
        f.write(content)
        f.close()

    def mkdir(self, path):
        print('before', path) #已是u'....'
        isExists = os.path.exists(self.file_url%(path)) #os.path.join(self.file_url, path)
        if not isExists:
            print('made a new Dir ~%s'%(path)) #u:python2
            os.makedirs(self.file_url%(path))
        else:
            print('name is', path, 'already have there!')
        #go inside the dir
        os.chdir(self.file_url%(path)) #os.path.join(self.file_url, path)

    #TODO log info and time in the local_root_dir
    def log(self, info):
        pass

    def start(self, url):
        content = self.doRequest(url)
        magas = self.doMageSoup(content) 
        map(self.doImgSoup, magas) #TODO
        # self.writeToFile(content) #TODO

        #TODO next page

if __name__ == '__main__':
    root_url = 'http://www.taotushe.cc/{}'
    main_url = 'http://www.taotushe.cc/forum.php?mod=forumdisplay&fid=97&page={}'
    warTTS = Magazine(web=root_url)
    for i in range(1, 130):
        warTTS.start(main_url.format(i))