from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote
import time
import os
from urllib.request import urlretrieve

url = 'https://mp.weixin.qq.com/mp/homepage?__biz=MzI0MTA2MDk3MA==&hid=28&sn=a9d5bea6dc313eee96a1dd79ab9d5f10&scene=18&devicetype=android-29&version=27000f3d&lang=zh_CN&nettype=WIFI&ascene=7&session_us=gh_f2631d699e12&pass_ticket=4grhxozRhAev9IGqdIFiuiTbY8jJbL4C9zQQ20RQLsW%2BeKOlhG1fjP4%2BE7OcYMoQ&wx_header=1'

opt = Options()
opt.add_argument('--no-sandbox')                # 解决DevToolsActivePort文件不存在的报错
opt.add_argument('--disable-gpu')               # 谷歌文档提到需要加上这个属性来规避bug
opt.add_argument('blink-settings=imagesEnabled=false')      # 不加载图片，提升运行速度
opt.add_argument('--headless')                  # 浏览器不提供可视化界面。Linux下如果系统不支持可视化不加这条会启动失败

browser = webdriver.Chrome(options=opt)
sub_browser = webdriver.Chrome(options=opt)
img_browser = webdriver.Chrome(options=opt)

def get_gage(url):
    try:
        browser.get(url)
        # 获取页面初始高度
        js = "return action=document.body.scrollHeight"
        height = browser.execute_script(js)
        # 将滚动条调整至页面底部
        browser.execute_script('window.scrollTo(0, document.body.scrollHeight)')
        #定义初始时间戳（秒）
        t1 = int(time.time())
        # 重试次数
        num=0

        while True:
	        # 获取当前时间戳（秒）
            t2 = int(time.time())
            # 判断时间初始时间戳和当前时间戳相差是否大于2秒，小于2秒则下拉滚动条
            if t2-t1 < 2:
                new_height = browser.execute_script(js)
                if new_height > height :
                    browser.execute_script('window.scrollTo(0, document.body.scrollHeight)')
                    # 重置初始页面高度
                    height = new_height
                    # 重置初始时间戳，重新计时
                    t1 = int(time.time())
            elif num < 3:                        # 当超过2秒页面高度仍然没有更新时，进入重试逻辑，重试3次，每次等待2秒
                num = num+1
            else:    # 超时并超过重试次数，程序结束跳出循环，并认为页面已经加载完毕！
                print("滚动条已经处于页面最下方！")
                break
        
        # 获取路径和标题
        links = browser.find_elements_by_class_name('js_post')
        titles = browser.find_elements_by_class_name('js_title')
        
        for i in range(len(links)):
            sub_url = links[i].get_attribute('href')
            title = titles[i].text
            title = title_pre(title)
            # 创建文件夹
            if not os.path.exists('./图片集/'+title):
                os.mkdir('./图片集/'+title)
            get_sub_page(sub_url, title)
        
        print("图片下载完成！")
    except Exception as e:
        print(e)     


def get_sub_page(url, title):
    try:
        sub_browser.get(url)
        tables = sub_browser.find_elements_by_xpath('//td/a')
        tables_2 = sub_browser.find_elements_by_xpath('//td/p/a')
        for link in tables:
            sub_url = link.get_attribute('href')
            get_imgs(sub_url, title)
        for link in tables_2:
            sub_url = link.get_attribute('href')
            get_imgs(sub_url, title)
    except Exception as e:
        print(e)


def get_imgs(url, title):
    try:
        img_browser.get(url)
        sub_title = img_browser.find_element_by_id('activity-name').text
        print('正在下载：'+ sub_title)
        sub_title = title_pre(sub_title)
        # 创建子文件夹
        if not os.path.exists('./图片集/'+title+'/'+sub_title):
            os.mkdir('./图片集/'+title+'/'+sub_title)
            # 匹配图片
            imgs = img_browser.find_elements_by_xpath('//td/p/img')
            imgs_2 = img_browser.find_elements_by_xpath('//td/img')
            index = 0
            for i in range(len(imgs)):
                # 获取图片路径
                img_url = imgs[i].get_attribute('data-src')
                img_url += '&tp=webp&wxfrom=5&wx_lazy=1&wx_co=1'
                # 保存到本地
                urlretrieve(img_url, './图片集/'+title+'/'+sub_title+'/'+str(index)+'.png')
                index += 1
            for i in range(len(imgs_2)):
                # 获取图片路径
                img_url = imgs_2[i].get_attribute('data-src')
                img_url += '&tp=webp&wxfrom=5&wx_lazy=1&wx_co=1'
                # 保存到本地
                urlretrieve(img_url, './图片集/'+title+'/'+sub_title+'/'+str(index)+'.png')
                index += 1
        else:
            return
    except Exception as e:
        print(e)


# 替换文件名中不能出现的字符
def title_pre(title):
    ng_word = ['\\', '/', ':', '：', '*', '?', '？', '\"', '“', '”', '<', '>', '|',]
    for word in ng_word:
        title = title.replace(word, ' ')
    title = title.rstrip()
    return title


get_gage(url)
