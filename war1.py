#糗事百科段子，不需要cookies，使用urllib
#每页20条
#2016年7月20日 网页不停改版，需根据最新的网页元素修改正则匹配
#偶尔会出现无内容的情况，如果此次直接next就没事
#，如果存就会报错，不会debug所以待改
#import six
try:
	import urllib.request as urllib2 #for 3.x
except ImportError:
	import urllib2 #for 2.x
import urllib
#正则匹配
import re

class War1:
	"""docstring for War1"""
	def __init__(self):
		super(War1, self).__init__()
		#self.arg = arg
		
	def onePage(self, pageIndex):
		#page = 1
		#一个验证
		headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'}
		url = 'http://www.qiushibaike.com/hot/page/' + str(pageIndex)
		try:
			req = urllib2.Request(url, headers = headers)
			response = urllib2.urlopen(req)
			#整个网页代码
			content = response.read().decode('utf-8')
			#(.*?)为分组，之后需要获取的内容。re.S:点任意匹配模式
			'''pattern = re.compile('div.*?author">.*?<a.*?<img.*?>(.*?)</a>.*?<div.*?'+
				'content">(.*?)<!--(.*?)-->.*?</div>(.*?)<div class="stats.*?number">(.*?)</i>',
				re.S)'''
			#作者，内容，图片，点赞数
			pattern = re.compile('<div.*?clearfix">.*?<h2>(.*?)</h2>.*?'+
				'class="content">(.*?)</div>(.*?)<div class="stats.*?number">(.*?)</i>',
				re.S)
			items = re.findall(pattern, content)
			return items
			'''for item in items:
				haveImg = re.search('img', item[2])
				if not haveImg:
					print ('作者:'+item[0])
					#a.replace('<br/>', '\n')
					webWrap = re.compile('<br/>')
					pyWrap = webWrap.sub('\n', item[1])
					print ('段子：'+pyWrap)
					print ('点赞数：'+item[3])'''
		except (urllib2.URLError) as e:
			if hasattr(e, "code"):
				print (e.code)
			if hasattr(e, "reason"):
				print (e.reason)

	def quickView(self, item):
		haveImg = re.search('img', item[2])
		if not haveImg:
			print('-----------------------------------')
			print ('作者:'+item[0])
			#a.replace('<br/>', '\n')
			webWrap = re.compile('<br/>')
			pyWrap = webWrap.sub('\n', item[1])
			print ('段子：'+pyWrap)
			print ('点赞数：'+item[3])
			print('-----------------------------------')

	def saveFile(self, item):
		fo = open('saveQ.txt', 'a+')
		fo.write('-----------------------------------\n')
		fo.write('author:' + item[0] + '\n')

		webWrap = re.compile('<br/>')
		pyWrap = webWrap.sub('\n', item[1])
		fo.write ('content:'+pyWrap+'\n')

		imgPa = re.compile('.*?<img src="(.*?)".*?', re.S)
		imgs = re.findall(imgPa, item[2])
		if len(imgs) > 0:
			pic=imgs[0]
			path='E:\ProgramCode\Python\war1pic\\'+item[0]+'.jpg'
			#声明存储地址及图片名称
			urllib2.urlretrieve(pic,path)

		fo.write ('vote:'+item[3]+'\n')
		fo.write ('-----------------------------------')
		fo.close()

	def begin(self):
		for i in range(1,100):
			items = self.onePage(i)
			for item in items:
				next = input('Enter to see story:(q to quit)')
				if next == 'q':
					return
				self.quickView(item)
				ans = input('存本条？y/n:')
				if ans == 'y':
					self.saveFile(item)

if __name__ == '__main__':
	warQ = War1()
	warQ.begin()