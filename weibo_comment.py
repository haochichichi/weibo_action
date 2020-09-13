from settings import *
from table_action import *

from weibo_login_thread import *

from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ChromeOptions


from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import threading
import time
from time import time as check_time
from selenium import webdriver
from multiprocessing import current_process



import requests, json
import base64
import random

from lxml import etree

import requests
class Comment():
    def __init__(self,browser):
        self.browser= browser
        self.loginname=''
        self.password = ''
        self.cookies={}
        self.comment = ''
        #self.comURL=

    def __init_info(self, acc, pwd,cookies,comment):
        self.loginname = acc
        self.password =  pwd
        self.cookies = cookies
        self.comment = comment

    def __process_cookies(self, cookiesList):
        """
        处理cookies
        :param cookies:
        :return:cookies_dict
        """
        cookie = [item["name"] + "=" + item["value"] for item in cookiesList]
        cookiestr = '; '.join(item for item in cookie)
        return cookiestr

    def __login(self):
        """
                通过cookies访问主页读取信息
                :param cookies_dict:
                :return:
                """
        time.sleep(2)
        cookies_dict=self.__process_cookies(json.loads(self.cookies))
        response = requests.get('http://my.sina.com.cn/profile/', cookies=cookies_dict, timeout=5,
                                allow_redirects=False)
        if response.status_code == 200:
            if 'me_name' in response.text:
                print(self.loginname + '[cookies 登录]>成功')

            else:
                print(self.loginname + '[cookies 登录]>登录失败！')
        else:
            print(self.loginname + '[cookies 登录]>传输失败！')


    # 发文字微博
    def __post_weibo(self,content):
        # 跳转到用户的首页
        self.browser.get('http://my.sina.com.cn/profile')
        self.browser.find_element_by_xpath('//li[@class="l_pdt l_pdt0"]/a').click()

        self.browser.implicitly_wait(5)

        # 在弹出的文本框中输入内容
        content_textarea = self.browser.find_element_by_class_name("W_input").send_keys(content)
        time.sleep(2)

        # 点击发布按钮
        post_button = self.browser.find_element_by_css_selector("[node-type='submit']").click()
        time.sleep(1)

        # 点击右上角的发布按钮
        #post_button =  self.browser.find_element_by_css_selector("[node-type='publish']").click()





    def ___to_comment (self, acc, pwd,cook,com):
        self.__init_info(acc, pwd,cook,com)
        # 删除cookie，再打开首页可以看到是未登录状态
        self.browser.delete_all_cookies()
        # 设置cookie再打开首页可以看到是已登录状态
        cookies=json.loads(self.cookies)
        for item in cookies:
            self.browser.add_cookie(item)
        self.browser.get('http://my.sina.com.cn/profile')
        print("进入")
        self.browser.find_element_by_xpath('//li[@class="l_pdt l_pdt0"]/a').click()
        time.sleep(100)
        #self.__login()
        #self.__post_weibo('test')
        return True


    def to_comment(self, acc, pwd,cook,com):
        return self.___to_comment(acc, pwd,cook,com)

def user_comment(username, password,cookies,comment):
    my_bro = Browser().get_browser()
    print("[____________________" + username + "start____________________]")
    try:
        if Comment(my_bro).to_comment(acc=username, pwd=password,cook=cookies,com=comment):
            print("[____________________"+username+"finishi 成功____________________]")
        else:
            print("[____________________" + username + "finishi 失败____________________]")
    except Exception as e:
        raise e
    #finally:
        #my_bro.close()
        #my_bro.quit()


if __name__ == '__main__':
    start = check_time()
    userinfo = Table_csv().read_table()
    i=0
    for user_list in userinfo:
        i+=1
        user_comment(user_list["username"], user_list["password"],user_list["cookies"],user_list["comment"])
    """
     userinfo = Table_csv().read_table()
    threads = []
    split_user_list = list_of_groups(userinfo, 1)  # 这里只需要修改分割的数量即可实现循环登录和并发登录的数量
    print('[split_user_list]', split_user_list)
    for user_list in split_user_list:
        threads = [threading.Thread(target=user_comment, args=(i["username"], i["password"],i["cookies"],i["comment"])) for i in user_list]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    """



    stop = check_time()
    print("[运行时间]" + str(stop - start) + "秒")
    Table_csv().check_table()
