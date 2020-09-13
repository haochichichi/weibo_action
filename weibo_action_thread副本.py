from settings import *
from table_action import *

from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import threading
import time
from selenium import webdriver
from multiprocessing import current_process



import requests, json
import base64
import random

from lxml import etree

import requests

#--------------------------打开浏览器--------------------------
class Browser:
    def __init__(self):
        # get直接返回，不再等待界面加载完成
        desired_capabilities = DesiredCapabilities.CHROME
        desired_capabilities["pageLoadStrategy"] = "none"

        self.browser = webdriver.Chrome(WEBDRIVER)
        self.browser.maximize_window()
        self.__open_browser()

        #self.browser.set_page_load_timeout(3)
        #self.browser.set_script_timeout(3)  # 这两种设置都进行才有效

    def __open_browser(self):
        self.browser.get('http://my.sina.com.cn/profile/unlogin/')
        self.browser.implicitly_wait(3)
        time.sleep(1)

    def get_browser(self):
        return self.browser

    def close_browser(self):
        self.browser.close()

#--------------------------登录账户-------------------------
class Login:
    def __init__(self,browser):
        self.browser= browser
        self.loginname=''
        self.password = ''

    #输入 账户密码
    def __inter_info(self,acc,pwd):
        self.loginname = acc
        self.password = pwd
        time.sleep(2)
        try:
            """
             print (self.loginname + '[账号密码可填] ')
            if (self.browser.find_element_by_name("loginname").text != ''):
                self.browser.find_element_by_name("loginname").clear()
                print (self.loginname + '[self.browser.find_element_by_name("loginname").text]不为空 ')
            self.browser.find_element_by_name("loginname").send_keys(acc)

            if (self.browser.find_element_by_name("password").text != ''):
                self.browser.find_element_by_name("password").clear()
            self.browser.find_element_by_name("password").send_keys(pwd)
            
            """

            self.browser.find_element_by_name("loginname").clear()
            self.browser.find_element_by_name("password").clear()
            self.browser.find_element_by_name("loginname").send_keys(acc)
            self.browser.find_element_by_name("password").send_keys(pwd)
            time.sleep(1)
        except:
            print (self.loginname + '[账号密码不可填] ')


    # 修改 验证码 图片大小
    def __process_verify_code(self):
        im = Image.open('img/'+self.loginname+' aucthcode.png')
        (x, y) = im.size  # read image size
        x_s = 100  # define standard width
        y_s = y * x_s // x  # calc height based on standard width
        out = im.resize((x_s, y_s), Image.ANTIALIAS)  # resize image with high-quality
        out.save('img/'+self.loginname+' aucthcode_pro.png')


    # 保存 验证码 截图
    def __save_verify_code(self):
        self.browser.find_element_by_class_name("reload-code").click()#微博不识别第一次验证码，故刷新截图
        self.browser.execute_script('document.body.style.zoom="0.8"') #电脑显示为125%
        time.sleep(1)
        self.browser.save_screenshot('img/'+self.loginname+' code.png')
        element = self.browser.find_element_by_class_name("yzm")  # 获取验证码的div位置

        left = element.location['x']
        top = element.location['y']
        right = left + element.size['width']
        bottom = top + element.size['height']

        img = Image.open('img/'+self.loginname+' code.png')
        imgcod = img.crop((left, top, right, bottom))  # 根据 div的长宽截图
        imgcod.save('img/'+self.loginname+' aucthcode.png')

        self.__process_verify_code()

    # VGGNet识别 验证码
    def __read_verify_code(self):
        img = open('img/'+self.loginname+' aucthcode_pro.png', 'rb+')
        img_raw_data = img.read()
        img.close()
        payload = {
            'img': base64.b64encode(img_raw_data)# 图片的二进制用base64编码一下
        }
        response = requests.post('http://127.0.0.1:5000/sina', data=payload)
        result = json.loads(response.text).get('result')
        return result

    # 判断 验证码 是否显示
    def __has_verify_code(self):
        time.sleep(1)
        try:
            html = etree.HTML(self.browser.page_source)
            res = html.xpath('.//li[@node-type="door_box"]/@style')[0]#取style内容
            if res == 'display: block;':
                print ( self.loginname+'[__has_verify_code] 有验证码')
                return True
            else :
                print (self.loginname+'[__has_verify_code] 无验证码')
                return False
        except:
            print(self.loginname+'[__has_verify_code] 判断验证码失败')
            return False

    # 判断 验证码 是否显示
    def __input_hidden(self):
        time.sleep(1)
        try:
             html = etree.HTML(self.browser.page_source)
             res = html.xpath('.//div[@node-type="box"]/@style')[0]  # 取style内容
             print('[res]',res)
             if (res.find('display: none;') != -1 ) :
                  print (self.loginname + '[__input_hidden] 输入框隐藏')
                  return True
             else:
                  print (self.loginname + '[__input_hidden] 输入框显示')
                  return False
        except:
             print(self.loginname + '[__input_hidden] 判断输入框显示失败')
             return False

    # 输入 验证码 
    def __deal_with_code(self):
        #由于验证码链接产生其他随机验证码，直接获取url失效，改用直接截图获取验证码
        self.__save_verify_code()
        #使用轮子（VGGNet）识别验证码
        result = self.__read_verify_code()
        print(self.loginname+'[verify_code Result]',result)

        self.browser.find_element_by_name("door").send_keys(result)
        self.browser.execute_script('document.body.style.zoom="1"')

    def __process_cookies(self, cookies):
        """
        处理cookies
        :param cookies:
        :return:cookies_dict
        """
        cookies_dict = {}
        for item in cookies:
            cookies_dict[item.get('name')] = item.get('value')
        print(self.loginname+'[cookies_dict]',cookies_dict)
        return cookies_dict

    def __get_cooikes(self):
        """
        从文件中读取cookies
        :return:
        """
        with open('sina_cookies.TXT', 'r', encoding='utf-8') as f:
            cooikes_dict = json.loads(f.read())
        return cooikes_dict
    

    def __save_cookies(self, cookies_dict,account):
        """
         保存cookies
        :param cookies_dict:
        :return:
        """
        #with open('sina_cookies.TXT', 'w', encoding='utf-8') as f:
            #f.write(json.dumps(cookies_dict, ensure_ascii='False', indent=4))
        Table_csv().save_cookies(cookies_dict,account)

        print(self.loginname + '[保存cookies到sina_cookies.TXT]')

    def __login_with_cookies(self, cookies_dict):
        """
        通过cookies访问主页读取信息
        :param cookies_dict:
        :return:
        """
        time.sleep(2)
        response = requests.get('http://my.sina.com.cn/profile/', cookies=cookies_dict, timeout=5, allow_redirects=False)
        if response.status_code == 200:
            if 'me_name' in response.text:
                print(self.loginname+'[通过cookies 登录成功]')

    # --------------------保存 cookies（主方法）---------------------------
    def ____save_cookies(self):
        cookies=self.browser.get_cookies()
        d = self.__process_cookies(cookies)
        self.__save_cookies(d,self.loginname)
        d = self.__get_cooikes()
        print(self.loginname + '[读取cookies从sina_cookies.TXT]')
        self.__login_with_cookies(d)

    def __is_succeed(self):
        time.sleep(5)
        try:
            a=self.browser.find_element_by_class_name("me_name")
            print(self.loginname + '[通过点击 登录成功]')
            return True
        except:
            print(self.loginname + '[通过点击 登录失败]')
            return False

    #--------------------自动 登录（主方法）---------------------------
    def ___to_login(self, acc, pwd):
        for i in range (0,5):#尝试5次登录
            if(self.__input_hidden()):#判断是否隐藏输入
                wait = WebDriverWait(self.browser, 10)
                wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'hd_login')))
                self.browser.find_element_by_class_name("hd_login").click()

            self.__inter_info(acc, pwd)#输入 账号密码
            if(self.__has_verify_code()):#判断 验证码 是否显示
                self.__deal_with_code()#输入 验证码 是否显示

            #点击登录
            self.browser.find_element_by_class_name("login_btn").click()
            if (self.__is_succeed()):#判断是否进入主页
                try:
                    self.____save_cookies()
                    print(self.loginname + '[存储cookies 成功]')
                    return True
                except:
                    print(self.loginname + '[存储cookies 失败]')
                    return False
            else:
                #self.browser.find_element_by_class_name("layerbox_close").click()
                self.browser.refresh()
            """
            try:
                wait = WebDriverWait(self.browser, 5)
                self.browser.find_element_by_class_name("login_btn").click()
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'me_name')))
                time.sleep(1)
            except TimeoutException:
                print ('time out after 30 seconds when loading page')
                self.browser.execute_script('window.stop ? window.stop() : document.execCommand("Stop");')  # 当页面加载时间超过设定时间，通过执行Javascript来stop加载，即可执行后续动作
            finally:
                if(self.__is_succeed()):
                    return True
            """
        return False


    def login(self, acc, pwd):
        return self.___to_login(acc, pwd)


def list_of_groups(list_info, per_list_len):
    '''
           将列表分割成指定长度的子列表，每个列表长度为当前测试并发数
           :param list_info:   列表，需要进行参数化的总列表
           :param per_list_len:  每个小列表的长度
           :return:
    '''
    list_of_group = zip(*(iter(list_info),) *per_list_len)
    end_list = [list(i) for i in list_of_group] # i is a tuple
    count = len(list_info) % per_list_len
    end_list.append(list_info[-count:]) if count !=0 else end_list
    return end_list

def user_login(username, password):
    my_bro = Browser().get_browser()
    procName = current_process().name
    print("当前进程:", procName)
    try:
        if Login(my_bro).login(acc=username, pwd=password):
            print("!")
    except Exception as e:
        raise e
    finally:
        print("[finishi]")
        my_bro.close()
        my_bro.quit()

if __name__ == '__main__':
    """
    userinfo = [
        {"username": "18290599612", "password": "Bee47961jj"},
        {"username": "16687332479", "password": "feew6987"},
        {"username": "15299527293", "password": "hcc479643ss"},
        {"username": "13806772472", "password": "zcc479543mm"}
    ]
    """
    userinfo=Table_csv().read_table()
    threads = []
    split_user_list = list_of_groups(userinfo, 2)  # 这里只需要修改分割的数量即可实现循环登录和并发登录的数量
    print(split_user_list)
    for user_list in split_user_list:
        threads = [threading.Thread(target=user_login, args=(i["username"], i["password"])) for i in user_list]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

