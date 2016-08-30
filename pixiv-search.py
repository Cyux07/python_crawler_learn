import sys
import io
import os
import time

try:
	import urllib.request as urllib2 #for 3.x
except ImportError:
	import urllib2 #for 2.x
import requests
import configparser
import emoji
#import unicodedata
import re
from multiprocessing.dummy import Pool as ThreadPool
#使用requests用户输入关键字进行搜索，结果保存在本地，以一张缩略图片和一个txt文本记录信息
#的形式，原图版稍作了些许，部分报错，流量大了也容易Protocol死掉
#TODO search ラブライブ!サンシャイン!
class Pixiv():
    def __init__(self):
        self.FAIL_LIMIT = 40
        self.limit = 1000 #检索门槛(收藏数)
        self.index_url = 'http://www.pixiv.net'
        self.login_url = 'https://accounts.pixiv.net/api/login?lang=zh'
        self.userAgent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'
        self.login_header = {
            'Accept':'*/*',
            'Accept-Encoding':'gzip, deflate, br',
            'Accept-Language':'zh-CN,zh;q=0.8',
            'Connection':'keep-alive',
            'Content-Length':'99',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            'Host':'accounts.pixiv.net',
            'Origin':'https://accounts.pixiv.net',
            'Referer':'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index',
            'User-Agent':self.userAgent
            ,'X-Requested-With':'XMLHttpRequest'
            ,'Upgrade-Insecure-Requests':'1'
            }
        self.header = {
            'Host':'www.pixiv.net',
            'Referer':'http://www.pixiv.net/',
            'User-Agent':self.userAgent
            }
        
        #作品地址(无主 /开头)、缩略图路径、title、作者id、作者名字、收藏数(int())
        '''self.pattern = re.compile('.*?<li class.*?image-item"><a href="(.*?)" class.*?thumb'
            +'nail"><img src="(.*?)" class.*?<h1 class="title.*?>(.*?)</h1>.*?data-'
            +'user_id="(.*?)" data-user_name.*?>(.*?)</a>.*?'
            +'mark-badge"></i>"(.*?)"</ul></li>.*?', re.S)'''
        self.pattern = re.compile('<li.*?image-item">(.*?)</ul></li>', re.S)

    def login(self):
        cf = configparser.ConfigParser()
        cf.read("pixivConfig.ini")
        cookies = cf._sections['cookies']

        pixivId = cf.get("info", "pixiv_id")
        password = cf.get("info", "password")
        #postKey = cf.get("info","post_key")
        source = cf.get("info", "source")
        self.cookies = dict(cookies)
        s = requests.session()
        pk = s.get('https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index')
        postKey = re.search(r'name="post_key" value="(\w+)"', pk.text).group(1)
        print(postKey)
        login_data = {"pixiv_id" : pixivId,
            "password" : password,
            'captcha': '',
            'g_recaptcha_response': '',
            "post_key" : postKey,
            "source":source}
        r = s.post(self.login_url, data = login_data)
        ''', headers = self.login_header, cookies=cookies'''
        print(r)
        print('登录是否成功：', end='')
        if r.status_code == 200:
            print(True)
        else:
            print(False)
        #r2 = s.get(self.index_url)
        #print(r2.text[:740])

        return s



    def get_search(self, url):
        time.sleep(3)
        success = False
        html = '' #response content
        while not success:
            try:
                html = self.s.get(url, headers = self.header).content.decode('utf-8')
                success = True
            except ConnectionError as e:
                print('raise error in get_search')
                time.sleep(10)
        #h = self.s.get(url, headers = self.header)
        #html = h.content.decode('utf-8')
        #print(html[64385:68030])
        ans = re.findall(self.pattern, html)
        if len(ans) < 1:
            return
        
        '''self.pattern = re.compile('.*?<li class.*?image-item"><a href="(.*?)" class.*?thumb'
            +'nail"><img src="(.*?)" class.*?<h1 class="title.*?>(.*?)</h1>.*?data-'
            +'user_id="(.*?)" data-user_name.*?>(.*?)</a>.*?'
            +'mark-badge"></i>"(.*?)"</a>.*?</li>.*?', re.S)'''
        for an in ans:
            votePat = re.compile('.*?mark-badge"></i>(.*?)</a>.*?')
            vote = re.findall(votePat, an)
            print(vote)
            if int(vote[0]) > self.limit:
                #print(vote)
                urlPat = re.compile('.*?<a href="(.*?)" class.*?')
                url = re.findall(urlPat, an)
                thumbPat = re.compile('.*?thumbnail"><img src="(.*?)" class.*?')
                thumb = re.findall(thumbPat, an)
                titlePat = re.compile('.*?<h1 class="title.*?le="(.*?)">.*?</h1>.*?')
                title = re.findall(titlePat, an)
                authoridPat = re.compile('.*?data-user_id="(.*?)" data-user_name.*?')
                authorid = re.findall(authoridPat, an)
                namePat = re.compile('.*?user_name.*?>(.*?)</a>.*?')
                name = re.findall(namePat, an)

                self.save_ans((url[0].replace('amp;', ''), thumb[0], title[0], authorid[0], name[0], vote[0]))
                
            
    #存储查询到的信息，目前到文件，TODO 更好的平台
    def save_ans(self, datas):
        time.sleep(3)
        title = datas[2] #.encode('utf-8').decode('unicode-escape')
        print(title)
        path = 'E:/ProgramCode/Python/pixivStar/'+self.keyword+'/'+title
        while os.path.exists(path):
            path = path + '(1)'
        try:
            os.mkdir(path)
        except FileNotFoundError as e:
            path = 'E:/ProgramCode/Python/pixivStar/'+self.keyword+'/' + title.replace('/','').replace('\\','').replace('.','')
            while os.path.exists(path):
                path = path + '(1)'
            os.mkdir(path)

        with open(path+'/data.txt', 'a+', encoding='utf-8') as f:
            f.write("地址:"+self.index_url+datas[0]+'\n')
            print("title:"+title, file=f)
            f.write("作者id:"+datas[3]+'\n')
            print('作者:'+datas[4], file=f) #.encode('utf-8').decode('unicode-escape')+'\n')
            f.write('收藏数:'+datas[5]+'\n')

        #urllib2.urlretrieve(datas[1],path+'\thumbnail.jpg')
        #img = self.s.get(datas[1], stream=True, headers=self.thumbHeader, cookies = self.cookies)
        img = self.getImg(datas[1], self.index_url+datas[0]) #TODO 原图还需传作品地址
        print(img)
        with open(path+'/thumbnail.jpg', 'wb') as f:
            f.write(img.content)
        

    def getImg(self, thumbUrl, url):
        imgPat = re.compile('tp://(.*?)net/.*?img-master/(.*?)_master1200', re.S)
        img_host,img_info = re.findall(imgPat, thumbUrl)[0]
        originalUrl = 'http://'+img_host+'net/img-original/'+img_info+'.jpg'
        header = {'Host':img_host+'net',
                'Referer':url,
                'If-Modified-Since':'Mon, 29 Aug 2016 05:17:31 GMT',
                'User-Agent':self.userAgent}
        fail = 0
        while fail < self.FAIL_LIMIT:
            try:
                #img = self.s.get(originalUrl, stream=True, headers=header, cookies = self.cookies)
                #img = self.s.get(thumbUrl, stream=True, headers=self.thumbHeader, cookies = self.cookies)
                img = self.s.get(thumbUrl, stream=True, headers=header, cookies = self.cookies)
                print(img)
                #if img.ok:
                if img.status_code != 403:
                    return img
                else:
                    print('code:%d' %img.status_code)
                    fail = fail + 1
                    time.sleep(10)
            except ConnectionError as e:
                print('img connect error in getImg:%s' %e)
                time.sleep(10)
            except ProtocolError as ex:
                print('img protocol error in getImg:%s' %ex)
                time.sleep(60)
            except Exception as unknown:
                print(unknown)

    def main(self):
        self.s = self.login()
        self.keyword = input('请输入要搜的图的关键字：') #raw_input(u'请输入...')输入中文？
        print(self.keyword)
        rootPath = 'E:\ProgramCode\Python\pixivStar\\'+self.keyword
        if not os.path.exists(rootPath):
            os.mkdir(rootPath) #TODO 自定义路径
        #TODO arg参数，收藏数
        #get_search(keyword)
        searchUrl = self.index_url + '/search.php?s_mode=s_tag&word='+self.keyword+'&order=date_d&p='+str(1)
        respo = self.s.get(searchUrl, headers=self.header)
        content1 = respo.content.decode('utf-8')
        '''with open('contentExample.txt', 'w', encoding='utf-8') as f:
            print(content1,f)'''
        descriPat = re.compile('<meta name="description" content="(.*?)">', re.S)
        descri = re.findall(descriPat, content1)[0]
        print(descri)
        amountPat = re.compile('count-badge">(.*?)\u4ef6</span>', re.S)
        amount = int(re.findall(amountPat, content1)[0]) // 20
        print('页数：'+str(amount))
        '''self.thumbHeader = {'Host':'i2.pixiv.net', #host i1 ~ i4
            'If-Modified-Since':'Thu, 11 Aug 2016 01:15:38 GMT',
            'Referer':searchUrl,
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36}'}

        signCheckPat = re.compile('signup-sina-button"(.*?)</button>')
        sign = re.findall(signCheckPat, content1)
        print(len(sign))'''
        '''signCheckPat2 = re.compile('bookmarks"(.*?)</li>')
        sign2 = re.findall(signCheckPat2, content1)
        print(len(sign2))'''
        #TODO 两种搜索模式
        #'s_mode=' 's_tag' #tag
        #'s_tc' #标题和介绍

        pool = ThreadPool(8)
        urls = []
        for page in range(1, amount):
            urls.append(self.index_url + '/search.php?word='+self.keyword+'&order=date_d&p='+str(page))
            #self.get_search(self.index_url + 'search.php?s_mode=s_tag&word='+self.keyword+'&order=date_d&p='+str(page))
        pool.map_async(self.get_search, urls)
        pool.close()
        pool.join()
        
        
        print('--mission complete--')
        #sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
        '''fileName = 'E:\ProgramCode\Python\searchPage.txt'
        fp = open(fileName, 'w')
        fp.write(html.encode('utf-8').decode('unicode-escape'))'''
        #print(html.encode('utf-8').decode('unicode-escape'))

if __name__ == '__main__':
    main = Pixiv()
    sys.exit(int(main.main() or 0))
