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

#设置chrome浏览器
chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument("--headless")
chrome_options.add_argument('log-level=3')
prefs = {"profile.managed_default_content_settings.images":2,
"download.default_directory": 'F:\\a\python\selenium',
"download.prompt_for_download": False}
chrome_options.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome(chrome_options=chrome_options)
#设置firefox
profile_directory='rust_mozprofile.p0ku2nHQI68s'
profile=webdriver.FirefoxProfile(profile_directory)
profile.set_preference('browser.download.folderList', 2)
profile.set_preference('browser.download.dir', os.getcwd())
profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/zip/doc')

#链接队列
linkQuence=Queue.Queue()

#统计已访问链接数
num=0
def addnum():
  global num
  numlock.acquire()
  num+=1
  print (u"正在访问第 %d 个页面" %num)
  numlock.release()

#访问过的链接列表
visitedLink=[]
def addLinkToList(url):
  global visitedLink
  listlock.acquire()
  visitedLink.append(url)
  listlock.release()

#时间限制装饰器
class TimeoutException(Exception):
  pass
ThreadStop = Thread._Thread__stop
def timelimited(timeout):
  def decorator(function):
    def decorator2(*args,**kwargs):
      class TimeLimited(Thread):
        def __init__(self,_error= None,):
          Thread.__init__(self)
          self._error = _error
        def run(self):
          try:
            self.result = function(*args,**kwargs)
          except Exception,e:
            self._error = str(e)
        def _stop(self):
          if self.isAlive():
            ThreadStop(self)
      t = TimeLimited()
      t.start()
      t.join(timeout)
      if isinstance(t._error,TimeoutException):
        t._stop()
        raise TimeoutException('timeout for %s' % (repr(function)))
      if t.isAlive():
        t._stop()
        raise TimeoutException('timeout for %s' % (repr(function)))
      if t._error is None:
        return t.result
    return decorator2
  return decorator

#对爬取的url去重，传入的参数为列表形式的Url集合,返回的是符合条件的URL集合
def url_filtrate(pagelinks,officialWeb):
    # 设置链接匹配格式
    same_target_url = []
    # 只要官网下的网站
    #以./开头
    pattern1=re.compile("./")
    #以/开头，不要//开头
    pattern2=re.compile("/")
    pattern5=re.compile("//")
    #如果以http开头了就需要求网址包含官网
    pattern4=re.compile(officialWeb)
    #以直接字母开头，不能是http
    pattern6=re.compile('[a-z]',re.I)
    pattern7=re.compile('http',re.I)
    #不要图片、pdf、doc等链接
    pattern3=re.compile("javascript|jpg$|pdf$|doc$|mp3$|png$|xls$|ppt$|zip$|rar$|xml$|css$|js$|gif$|jpeg$|exe$|@|docx$|pptx$|xlsx$|mp4$",re.I)
    #不要JavaScript字段
    pattern8=re.compile("javascript|#|2018|2017|2016|2015|2014|2013|2012|2011|2010|2009|2008|2007|2006|2005|2004|2003")
    #匹配链接文本内容
    pattern9=re.compile("公告|财政|预算|信息|公开|更多|决算|进入|资金")
    #文本只有数字的链接不要
    pattern10=re.compile('^\d+$')
    for link in pagelinks:
      htmltext=link.get_attribute("innerHTML")
      text=link.get_attribute("textContent")
      if pattern9.search(htmltext.encode('utf-8'))!=None:
        if pattern10.search(text)==None:
          try:
            l=link.get_attribute('href')
            #只有官网加/的不要
            if l!=(officialWeb+'/') or l!=(officialWeb+'/index.html'):
              if pattern8.search(l)==None:
                if pattern3.search(l,re.I)==None:
                  if pattern1.match(l,re.I)!=None:
                      link=officialWeb+l[1:]
                      same_target_url.append(link)
                  elif pattern2.match(l)!=None and pattern5.match(l)==None:
                      link=officialWeb+l
                      same_target_url.append(link)
                  elif pattern6.match(l)!=None and pattern7.match(l)==None:
                      link=officialWeb+'/'+l
                      same_target_url.append(link)
                  elif pattern4.search(l)!=None:
                      same_target_url.append(l)
                  else:
                      pass
                else:
                    pass
          except:
              pass
    # 去除重复url
    unrepect_url = []
    for l in same_target_url:
        if l not in unrepect_url:
            unrepect_url.append(l)
    return unrepect_url

#判断此页面是否是具有“首页、尾页（末页）、下一页”
def is_first_page(pageContent):
  pattern1=re.compile(u"下一页")
  pattern2=re.compile(u"首页")
  pattern3=re.compile(u"尾页|末页")
  pattern4=re.compile(u"预算|决算")
  if pattern4.search(pageContent)!=None:
    if pattern1.search(pageContent)!=None and pattern2.search(pageContent)!=None and pattern3.search(pageContent)!=None:
        return 1
  else:
    return 0

#判断下一页字段在什么标签中
def judge_label(judge_driver):
    flag=0
    pattern1=re.compile(u"下一页")
    #判断下一页在什么标签中
    try:
      a_links=judge_driver.find_elements_by_tag_name("a")
      for a_target in a_links:
          text=a_target.get_attribute("innerHTML")
          if pattern1.search(text)!=None:
              flag=1
              return flag
      p_links=judge_driver.find_elements_by_tag_name("p")
      for p_target in p_links:
          text=p_target.get_attribute("innerHTML")
          if pattern1.search(text)!=None:
              flag=2
              return flag
      span_links=judge_driver.find_elements_by_tag_name("span")
      for span_target in span_links:
          text=span_target.get_attribute("innerHTML")
          if pattern1.search(text)!=None:
              flag=3
              return flag
    except:
      return 0

#将表格中的链接加入list中
def get_table_list(newdriver,officialWeb):
  print u"有大表格，可能很慢"
  #链接临时存储
  link_list=[]
  pattern1=re.compile(u"下一页")
  pagenum=10
  #a标签处理
  if judge_label(newdriver)==1:
    #设置下一页的次数
    for i in range(pagenum):
      #页面刷新了获取新元素需等新时间
      time.sleep(5)
      initial_links=driver.find_elements_by_tag_name("a")
      page_list=url_filtrate(initial_links,officialWeb)
      #第一页放进去
      for right_link in page_list:
        if right_link not in link_list:
          link_list.append(right_link)
      try:
        for target in initial_links:
          #找到下一页按钮点击
          text=target.get_attribute("innerHTML")
          if pattern1.search(text)!=None:
            js="var q=document.documentElement.scrollTop=20000"
            driver.execute_script(js)
            ActionChains(driver).move_to_element(target).click(target).perform()
      except:
        break
  #p标签处理
  if judge_label(newdriver)==2:
    #设置下一页的次数
    for i in range(pagenum):
      #页面刷新了获取新元素需等新时间
      time.sleep(3)
      initial_links=driver.find_elements_by_tag_name("a")
      p_links=driver.find_elements_by_tag_name("p")
      page_list=url_filtrate(initial_links,officialWeb)
      #第一页放进去
      for right_link in page_list:
        if right_link not in link_list:
          link_list.append(right_link)
      try:
        for target in p_links:
          #找到下一页按钮点击
          text=target.get_attribute("innerHTML")
          if pattern1.search(text)!=None:
            js="var q=document.documentElement.scrollTop=20000"
            driver.execute_script(js)
            ActionChains(driver).move_to_element(target).click(target).perform()
      except:
          break
  #span标签处理
  if judge_label(newdriver)==3:
    #设置下一页的次数
    for i in range(pagenum):
      #页面刷新了获取新元素需等新时间
      time.sleep(3)
      initial_links=driver.find_elements_by_tag_name("a")
      span_links=driver.find_elements_by_tag_name("span")
      page_list=url_filtrate(initial_links,officialWeb)
      #第一页放进去
      for right_link in page_list:
        if right_link not in link_list:
          link_list.append(right_link)
      try:
        for target in span_links:
          #找到下一页按钮点击
          text=target.get_attribute("innerHTML")
          if pattern1.search(text)!=None:
            js="var q=document.documentElement.scrollTop=20000"
            driver.execute_script(js)
            ActionChains(driver).move_to_element(target).click(target).perform()
      except:
          break
  return link_list

#链接搜索
def getPageLink(url,officialWeb):
  try:
    #隐性等待
    driver.implicitly_wait(15)
    driver.get(url)
    if is_first_page(driver.page_source)==1:
      right_links=get_table_list(driver,officialWeb)
      for link in right_links:
        linkQuence.put(link)
    else:
      #获取官网页面的链接并格式化链接
      initial_links=driver.find_elements_by_tag_name("a")
      right_links = url_filtrate(initial_links,officialWeb)
      #放入队列中
      for link in right_links:
        linkQuence.put(link)
    #检查页面内容
    checkPage(driver.page_source,url,driver.title)
  except:
    print u"获取页面失败"


#页面检查
def checkPage(pageContent,url,title):
  #匹配主要字段
  param_one=u"县.*?2018年.*?预算执行.*?2019年.*?预算|区.*?2018年.*?预算执行.*?2019年.*?预算|市.*?2018年.*?预算执行.*?2019年.*?预算"
  pattern_one = re.compile(param_one)
  match_one=pattern_one.findall(pageContent)
  #主要字段只有一次，匹配更多字段
  pattern_two=re.compile(u"一般公共预算")
  match_two=pattern_two.findall(pageContent)
  pattern_five=re.compile(u"政府性基金")
  match_five=pattern_five.findall(pageContent)
  #从title中筛选掉不要的页面
  pattern_three=re.compile(u"镇|乡|部|局|学|校|会|馆|委|院")
  match_three=pattern_three.search(title)
  #匹配信息公开类型
  pattern_four=re.compile(u"预.*?算信息公开|预.*?算公开信息")
  match_four=pattern_four.findall(pageContent)
  #如果页面出现两次匹配先寻找下载目标
  if len(match_one)>=1:
    if downloadfile(url)==0:
      if len(match_two)!=0 and match_three==None and len(match_five)!=0:
        if os.path.exists(title+'.pdf')==False:
          save_pdf(url)
          os.rename('file.pdf',title+'.pdf')
      else:
        print u"页面不符合"
  #这种页面只有标题，直接找
  elif len(match_four)!=0 and len(match_one)!=0:
    if downloadfile(url)==0:
      print u"页面不符合"
  else:
      print u"页面不符合"

#firefox下载
def downloadfile(url):
  #匹配主要字段
  param_one=u"2018年.*?预算执行.*?2019年.*?预算"
  pattern_one = re.compile(param_one)
  param_three=u"2019.*?预算.*?草案|2019.*?预算.*?报告"
  pattern_three = re.compile(param_three)
  #不包括字段
  param_two=u"镇|乡|部|局|学|校|会|馆|委|院"
  pattern_two = re.compile(param_two)
  browser = webdriver.Firefox(profile,executable_path="geckodriver.exe",firefox_binary="Mozilla Firefox/firefox.exe")
  #隐性等待
  browser.implicitly_wait(3)
  browser.get(url)
  target_list=browser.find_elements_by_tag_name("a")
  #记录是否发生点击事件
  count=0
  for target in target_list:
    text=target.get_attribute('textContent')
    if pattern_two.search(text)==None:
      if pattern_one.search(text)!=None or pattern_three.search(text)!=None:
        #在页面找
        num=0
        for i in range(50):
          try:
            time.sleep(0.2)
            js="var q=document.documentElement.scrollTop="+str(num)
            browser.execute_script(js)
            ActionChains(browser).move_to_element(target).click(target).perform()
            count+=1
            break
          except: 
            num+=1000
  if count!=0:
    return 1
  else:
    return 0

#pdf转换
def save_pdf(htmls):
    #添加了环境变量还是搞不成，只有代码找位置
    path_wk = r'D:\wkhtmltox\bin\wkhtmltopdf.exe' #安装位置
    config = pdfkit.configuration(wkhtmltopdf = path_wk)
    try:
      pdfkit.from_url(htmls, 'file.pdf',configuration=config)
    except:
      print u"pdf转换有问题"

#爬虫
def Spider(officialWeb):
  try:
    #在队列不为空的时候
    while linkQuence.empty!=True:
      visitUrl=linkQuence.get(block=False)
      if visitUrl in visitedLink:
        continue
      else:
        addnum()
        addLinkToList(visitUrl)
        print visitUrl
        try:
          getPageLink(visitUrl,officialWeb)
        except:
          continue
  except:
    print u"链接访问结束"

#多线程爬虫
def threadSpider(number,officialWeb):
  for i in range(number):
    t = Thread(target=Spider,args=(officialWeb,))
    t.start()
    t.join()

def start(url,number):
  #创建文件夹
  startTime = time.clock()
  try:
    driver.implicitly_wait(10)
    driver.get(url)
  except:
    print u"获取页面失败"
  #获取官网页面的链接并格式化链接
  initial_links=driver.find_elements_by_tag_name("a")
  right_links = url_filtrate(initial_links,url)
  for link in right_links:
    linkQuence.put(link)
  # 设置线程数和启动多线程
  threadSpider(number,url)
  fo = open("url.txt", "w+")
  for link in visitedLink:
    fo.writelines(link+'\n')
  fo.close()
  elapsed = (time.clock() - startTime)
  print("Time used:",elapsed)
  driver.quit()

if __name__ == '__main__':
  #创建一把同步锁
  numlock = threading.Lock() 
  listlock= threading.Lock()
  start('http://www.gzdr.gov.cn',30)


