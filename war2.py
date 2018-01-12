#个人界面相册按钮：/html/body/div[4]/div/div[1]/ul/li[1]/span/a
#下一页按钮，先用正则匹配页数作循环终点：class="page-next J_AjaxifyTrigger"
#先用class="mm-photo-cell"获取列表长度得到index边界
#每一个相册进入点：//*[@id="J_HerPanel"]/div/div[index]/div/h4/a
#相册每张皂片缩略图class="mm-photoimg-area" click之
#相册又判断page数，每页index数。啊~好想自爆
#皂片元素正则匹配下载<img id="J_MmBigImg" width="100%" 
#src="//img.alicdn.com/imgextra/i2/1053440860
#/TB1QrsaKFXXXXaTXpXXXXXXXXXX_!!0-tstar.jpg_620x10000.jpg" 
#data-user-id="1053440860" data-album-id="10000946802" 
#data-pic-id="10003434334" isedit="false" ismanager="false">
#匹配完close掉
# -*- coding:utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import configparser

import sys
import os # for create file dir
import time
import random

#鼠标事件
from selenium.webdriver.common.action_chains import ActionChains

try:
	import urllib.request as urllib2 #3.x
except ImportError:
	import urllib2 #2.x
import re

class Taobao():
	

	def __init__(self):
		self.proxy_list = [
			'113.111.148.67:8421',
			'183.141.123.71:8631',
			'183.19.14.179:8818',
			'110.73.38.187:8632',
			'182.89.7.226:8506',
			'183.140.81.216:8897'
		]

		user_agent = ("Mozilla/5.0 (Windows NT 6.1; WOW64) "
			+"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 "
			+"Safari/537.36")

		self.change_proxy()
		dcap = dict(DesiredCapabilities.PHANTOMJS)
		dcap["phantomjs.page.settings.userAgent"] = user_agent
		
		self.gate = webdriver.PhantomJS(desired_capabilities=dcap)
		self.gate.get('https://mm.taobao.com/search_tstar_model.htm')

		print('正在前往 %s' %(self.gate.title))

	def mmListPage(self):
		#TODO 翻页(click 下一页？)
		try:
			mmsXPath = '//li[@class=\'item\']/a[@class=\'item-link\']'
			WebDriverWait(self.gate, 10).until(
			 EC.presence_of_all_elements_located((By.XPATH, mmsXPath)))
			mmlen = len(self.gate.find_elements(By.XPATH, mmsXPath))

			cf = configparser.ConfigParser()
			cf.read("taobaoConfig.ini")
			cookies = cf._sections['cookies']
			cookies = dict(cookies)
			

			for i in range(0, mmlen):
				WebDriverWait(self.gate, 10).until(
			 		EC.element_to_be_clickable((By.XPATH, mmsXPath)))
				mm = self.gate.find_elements(By.XPATH, mmsXPath)[i]
				#mmPage = mm.get_attribute('href')
				#mm.click()
				mm.send_keys(Keys.ENTER)
				#ActionChains(self.gate).click(mm).perform()
				self.gate.switch_to_window(self.gate.window_handles[-1])
				WebDriverWait(self.gate, 100).until(
			 		        EC.presence_of_all_elements_located((By.TAG_NAME, "img")))
				print(self.gate.title)
				path = self.samplePic() #文件夹路径
				time.sleep(1)
				info = self.gate.find_element_by_xpath('//ul[@class=\'m-p-menu\']/li[3]/span/a')
				
				self.gate.add_cookie(cookies)
				info.click() #无新页面
				#info.send_keys(Keys.ENTER)
				self.mmInfo(path)
				if '_blank' in info.get_attribute('target'):
					self.gate.close()
					self.gate.switch_to_window(self.gate.window_handles[-1])
				else:
					self.gate.back()
				

				#TODO goto album
				self.gate.close()
				self.gate.switch_to_window(self.gate.window_handles[0])
				print('one mm down...'+lne(self.gate.window_handles))	
		finally:
			self.gate.quit()
		
	def change_proxy(self):
			'''proxy = random.choice(self.proxy_list)
			print('改变代理ip为%s' %proxy)
			handle = urllib2.ProxyHandler({'http':proxy})
			opener = urllib2.build_opener(handle)
			urllib2.install_opener(opener)'''


	#模特自己写的自我介绍，有的没照片，也有很多照片，但非照片的入宝贝销量截图、二维码也混进来了。
	def samplePic(self):
		name = 'not fetch yet'
		packPath = 'not fetch path yet'
		try:
			content = self.gate.page_source
			namePat = re.compile('.*?<dl>.*?<dd><a.*?">(.*?)</a></dd>.*?', re.S)
			name = re.findall(namePat, content)
			imgPat = re.compile('.*?<img.*?src="(.*?)">.*?', re.S)
			imgs = re.findall(imgPat, content)
		finally:
			self.gate.quit()

		packPath = 'E:/ProgramCode/Python/war2pic/'+name[0]+'/'
		if not os.path.exists(packPath):
			#os.mkdir(packPath)
			os.makedirs(packPath) #多级路径

		index = 1
		print('简介图共%d张' % len(imgs))
		for img in imgs:
			try:
				path=str(packPath+str(index)+'.jpg')
				#声明存储地址及图片名称(某宝的图片都缺个协议头...)
				#方法1：urllib2.urlretrieve('https:'+img,path)
				html = urllib2.urlopen('https:'+img)
				data = html.read()
				fileName = path
				fp = open(fileName, 'wb')
				fp.write(data)
				print('save pic %d/%d' % (index, len(imgs)))
				index+=1
				if index > 10:
					break#time.sleep(300)
			except urllib2.URLError as e:
				print(str(e))
				self.change_proxy()
				time.sleep(600)
			time.sleep(10) #50ms->10s 防止：WinError 10061 由于目标计算机积极拒绝，无法连接。
		

		return packPath

	def mmInfo(self, path):
		content = self.gate.page_source.encode('utf-8')
		print("妹子信息页面：")
		print(content)
		pattern = re.compile('.*?<ul class="mm-p-info-cell clearfix">'+
			'.*?<li class=".*?<label>(.*?)</label><span>(.*?)'+
			'</span></li>.*?</ul>.*?', re.S)
		infoPairs = re.findAll(pattern, content)
		fo = open(path+'info.txt', 'w')
		for i in range(1,len(infoPairs)-1):
			key = infoPairs[i]
			value = infoPairs[i+1]
			i=i+1
			fo.write(key)
			fo.write(value + '\n')
		fo.close()

	def main(self):
		self.mmListPage()
		
if __name__ == '__main__':
	tb = Taobao()
	tb.main()