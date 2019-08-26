#-*-  coding:utf-8 -*-
import sys,os,re,Queue,pdfkit,time
reload(sys)
sys.setdefaultencoding('utf-8')
from PyPDF2 import PdfFileMerger
#多线程
from threading import Thread
import threading
#使用selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains

#设置firefox
profile_directory='rust_mozprofile.a1dxoYnWNfeH'
profile=webdriver.FirefoxProfile(profile_directory)
profile.set_preference('browser.download.folderList', 2)
profile.set_preference('permissions.default.image',2)
profile.set_preference('browser.download.dir', os.getcwd())
profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/zip/doc')
profile_options=webdriver.FirefoxOptions()
profile_options.add_argument('-headless')
driver=webdriver.Firefox(profile,executable_path="geckodriver.exe",firefox_binary="Mozilla Firefox/firefox.exe")

#链接队列
linkQuence=Queue.Queue()

#访问百度，并添加入访问字段
def visited_BD(county,num):
  driver.implicitly_wait(10)
  driver.get("http://www.baidu.com")
  driver.find_element_by_id("kw").send_keys(county+u"2018预算执行和2019预算")
  for i in range(num):
    try:
      target_url= driver.find_element_by_xpath("//div[@id="+str(i+1)+"]//h3//a")
      linkQuence.put(target_url.get_attribute("href"))
    except:
      break
  try:
    while linkQuence.empty!=True:
        checkPage(linkQuence.get(block=False),driver,county)
  except:
    print u"链接访问结束"

#页面检查
def checkPage(url,driver,county):
  driver.set_page_load_timeout(10)
  try:
    driver.get(url)
    #匹配主要字段
    param_one=county+u".*?2018.*?执行.*?2019.*?预算"
    pattern_one = re.compile(param_one)
    match_one=pattern_one.findall(driver.page_source)
    #主要字段只有一次，匹配更多字段
    pattern_two=re.compile(u"一般公共预算")
    match_two=pattern_two.findall(driver.page_source)
    pattern_five=re.compile(u"政府性基金")
    match_five=pattern_five.findall(driver.page_source)
    #从title中筛选掉不要的页面
    pattern_three=re.compile(u"镇|乡|部|局|学|校|会|馆|委|院|室|街|2017|2016|2015|2014|2013|2012")
    match_three=pattern_three.search(driver.title)
    #如果页面出现两次匹配先寻找下载目标
    if len(match_one)>=1:
      downloadfile(driver)
      if len(match_two)!=0 and match_three==None and len(match_five)!=0:
        if os.path.exists(driver.title+'.pdf')==False:
          save_pdf(url)
          os.rename('file.pdf',driver.title+'.pdf')
        else:
          save_pdf(url)
          os.rename('file.pdf',driver.title+str(num)+'.pdf')
      else:
        print u"页面不符合"
    else:
        print u"页面不符合"
  except:
    pass

#firefox下载
def downloadfile(driver):
  #匹配主要字段
  param_one=u"2018.*?执行.*?2019.*?预算"
  pattern_one = re.compile(param_one)
  param_three=u"2019.*?预算.*?草案|2019.*?预算.*?报告"
  pattern_three = re.compile(param_three)
  #不包括字段
  param_two=u"镇|乡|部|局|学|校|会|馆|委|院|室|街|2017|2016|2015|2014|2013|2012"
  pattern_two = re.compile(param_two)
  target_list=driver.find_elements_by_tag_name("a")
  #记录是否发生点击事件
  for target in target_list:
    text=target.get_attribute('innerHTML')
    if pattern_two.search(text)==None:
      if pattern_one.search(text)!=None or pattern_three.search(text)!=None:
        #在页面找
        num=0
        for i in range(50):
          try:
            time.sleep(0.2)
            js="var q=document.documentElement.scrollTop="+str(num)
            driver.execute_script(js)
            ActionChains(driver).move_to_element(target).click(target).perform()
            break
          except: 
            num+=1000

#pdf转换
def save_pdf(htmls):
  #添加了环境变量还是搞不成，只有代码找位置
  path_wk = r'D:\wkhtmltox\bin\wkhtmltopdf.exe' #安装位置
  config = pdfkit.configuration(wkhtmltopdf = path_wk)
  try:
    pdfkit.from_url(htmls, 'file.pdf',configuration=config)
  except:
    print u"pdf转换有问题"

count_list=[u"金县",u"理县",u"通江县",u"金牛区",u"简阳",u"都江堰",u"大竹",u"通川",u"广汉",u"新龙县",u"九龙县",u"炉霍县",u"石渠县",u"稻城县",u"岳池",
u"华蓥",u"邻水",u"剑阁",u"夹江",u"峨边",u"犍为",u"德昌",u"昭觉",u"布拖",u"美姑",u"盐源",u"江阳",u"纳溪",u"古蔺",u"彭山",u"仁寿",u"江油",u"北川",u"阆中",
u"南部县",u"西充",u"内江市市中区",u"内江市东兴区",u"雨城",u"乐至",u"雁江区"]
for target in count_list:
  visited_BD(target,5)

driver.quit()