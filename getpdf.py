#-*-  coding:utf-8 -*-
import sys,re,re,os
reload(sys)
sys.setdefaultencoding('utf-8')
#导入webdriver
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
#要想调用键盘按键操作需要引入keys包
from selenium.webdriver.common.keys import Keys

#设置浏览器
profile_directory="jnuycir2.default-release-1"
profile=webdriver.FirefoxProfile(profile_directory)
profile.set_preference('browser.download.folderList', 2)
profile.set_preference('browser.download.dir', os.getcwd())


#网址判断
def judgeurl(url):
    #EI
    pattern_EI=re.compile("ieee")
    #维普
    pattern_vip=re.compile("cqvip")
    #万方
    pettern_wangfang=re.compile("wanfangdata")
    #知网
    pattern_cnki=re.compile("cnki")
    if pattern_EI.search(url)!=None:
        return 2
    elif pattern_vip.search(url)!=None:
        return 1
    elif pettern_wangfang.search(url)!=None:
        return 3
    elif pattern_cnki.search(url)!=None:
        return 4
    else:
        return 5

def getpdf(url):
    driver = webdriver.Firefox(profile,executable_path="geckodriver.exe",firefox_binary="Mozilla Firefox/firefox.exe")
    
    #隐性等待
    driver.implicitly_wait(3)
    driver.get(url)
    if judgeurl(url)==1:
    #维普
        target_list=driver.find_elements_by_tag_name("a")
        for target in target_list:
            text=target.get_attribute('textContent')
            if text=='下载PDF':
                ActionChains(driver).move_to_element(target).click(target).perform()
    elif judgeurl(url)==2:
    #EI
        target=driver.find_elements(By.CLASS_NAME, "pdf")
        ActionChains(driver).move_to_element(target[0]).click(target[0]).perform()
    elif judgeurl(url)==3:
    #万方
        target=driver.find_element_by_id("ddownb")
        ActionChains(driver).move_to_element(target).click(target).perform()
    elif judgeurl(url)==4:
    #知网
        try:
            target=driver.find_element_by_id("pdfDown")
            ActionChains(driver).move_to_element(target).click(target).perform()
        except:
            target_list=driver.find_elements_by_tag_name("b")
            for target in target_list:
                text=target.get_attribute('textContent')
                if text=='PDF下载':
                    ActionChains(driver).move_to_element(target).click(target).perform()
    elif judgeurl(url)==5:
    #SCI
        target_list=driver.find_elements_by_tag_name("span")
        for target in target_list:
            text=target.get_attribute('textContent')
            if text=='Download PDF':
                ActionChains(driver).move_to_element(target).click(target).perform()
    # driver.quit()
if __name__ == "__main__":
    x=1
    while x==1:
        print u"请输入访问的链接按回车结束:\n"
        url=raw_input()
        getpdf(url)
        print u"请选择是否继续输入链接（1、继续，其他数字退出）"
        num=raw_input()
        x=int(num)