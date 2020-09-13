#from chaojiying import Chaojiying_Client
from settings import *

from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import requests, json
import base64
import random

from lxml import etree
import time

import requests

class Browser:
    def __init__(self):

        # get直接返回，不再等待界面加载完成
        desired_capabilities = DesiredCapabilities.CHROME
        desired_capabilities["pageLoadStrategy"] = "none"

        self.browser = webdriver.Chrome(WEBDRIVER)
        #self.super_eagle = Chaojiying_Client(YINGUSER, YINGPWD, YINGCODE)
        self.__open_browser()
        #self.browser.set_page_load_timeout(3)
        #self.browser.set_script_timeout(3)  # 这两种设置都进行才有效

    def __open_browser(self):
        self.browser.get('http://my.sina.com.cn/profile/unlogin/')
        self.browser.implicitly_wait(3)
        self.browser.find_element_by_class_name("hd_login").click()
        time.sleep(1)

    def get_browser(self):
        return self.browser

    def close_browser(self):
        self.browser.close()


class Login:
    def __init__(self,browser):
        self.browser= browser
        #self.super_eagle = Chaojiying_Client(YINGUSER, YINGPWD, YINGCODE)

    def __inter_info(self,acc,pwd):
        self.browser.find_element_by_name("loginname").clear()
        self.browser.find_element_by_name("password").clear()
        self.browser.find_element_by_name("loginname").send_keys(acc)
        self.browser.find_element_by_name("password").send_keys(pwd)
        time.sleep(1)

    def __process_image(self):
        im = Image.open('aucthcode.png')
        (x, y) = im.size  # read image size

        x_s = 100  # define standard width
        y_s = y * x_s // x  # calc height based on standard width
        out = im.resize((x_s, y_s), Image.ANTIALIAS)  # resize image with high-quality
        out.save('aucthcode_pro.png')

        print ('original size: ', x, y)
        print ('adjust size: ', x_s, y_s)


    def __save_picture(self):
        self.browser.find_element_by_class_name("reload-code").click()
        self.browser.execute_script('document.body.style.zoom="0.8"') #电脑显示为125%
        self.browser.save_screenshot('code.png')
        element = self.browser.find_element_by_class_name("yzm")  # 获取验证码的div位置

        #print(element.location)  # 打印元素坐标
        #print(element.size)  # 打印元素大小

        left = element.location['x']
        top = element.location['y']

        right = left + element.size['width']
        bottom = top + element.size['height']

        img = Image.open('code.png')
        imgcod = img.crop((left, top, right, bottom))  # 根据 div的长宽截图
        imgcod.save('aucthcode.png')
        print((left, top, right, bottom))

        self.__process_image()

    def __has_verify_code(self):
        time.sleep(1)
        try:
            #img=self.browser.find_element_by_class_name("yzm")
            html = etree.HTML(self.browser.page_source)
            print(1)
            res = html.xpath('.//li[@node-type="door_box"]/@style')[0]
            print(res)
            if res == 'display: block;':
                print ('有验证码')
                return True
            else :
                print ('无验证码')
                return False
        except:
            print('判断验证码失败')
            return False


    def __deal_with_code(self):
        img = self.browser.find_element_by_class_name("yzm")
        src = img.get_attribute('src')  # 获取链接信息
        print(src)
        img_bytes = requests.get(src).content  # 获取验证码的字节流信息

        with open('baidu_tieba.png', 'ab') as f:
            f.write(img_bytes)
            f.close()

        self.__save_picture()

        img = open('aucthcode_pro.png', 'rb+')
        img_raw_data = img.read()
        img.close()
        payload = {
            # 图片的二进制用base64编码一下
            'img': base64.b64encode(img_raw_data)
        }
        response = requests.post('http://127.0.0.1:5000/sina', data=payload)
        # print(response.text)
        print('当前目录current_captcha.jpg的识别结果', response.json()['result'])

        state = json.loads(response.text).get('result')

        print('[state]', state)

        self.browser.find_element_by_name("door").send_keys(state)
        self.browser.execute_script('document.body.style.zoom="1"')

        """
         #path 拼接
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'verifycode')
        code_img_path = os.path.join(path, 'code_img.png')
        code_img_path_all = os.path.join(path, 'all_code_img.png')
        #验证码获取
        self.__get_image(code_img_path_all, code_img_path)
        self.__inter_code(self.__discern_code(code_img_path))
        """

    def process_cookies(self, cookies):
        """
        处理cookies
        :param cookies:
        :return:
        """
        cookies_dict = {}
        for item in cookies:
            cookies_dict[item.get('name')] = item.get('value')
        print('cookies_dict',cookies_dict)
        return cookies_dict

    def get_cooikes(self):
        """
        从文件中读取cookies
        :return:
        """
        with open('sina_cookies.TXT', 'r', encoding='utf-8') as f:
            cooikes_dict = json.loads(f.read())
        return cooikes_dict

    def save_cookies(self, cookies_dict):
        """
         保存cookies
        :param cookies_dict:
        :return:
        """
        with open('sina_cookies.TXT', 'w', encoding='utf-8') as f:
            f.write(json.dumps(cookies_dict, ensure_ascii='False', indent=4))

    def login_with_cookies(self, cookies_dict):
        """
        通过cookies访问主页读取信息
        :param cookies_dict:
        :return:
        """
        time.sleep(2)
        response = requests.get('http://my.sina.com.cn/profile/', cookies=cookies_dict, timeout=5, allow_redirects=False)
        print(response)
        if response.status_code == 200:
            print('用户cookies有效')
            time.sleep(1)
            if 'me_name' in response.text:
                print('通过cookies登录成功')

    def __save_cookies(self):

        print('存cookies：')
        cookies=self.browser.get_cookies()
        d = self.process_cookies(cookies)
        self.save_cookies(d)
        print('保存用户cookies成功')
        d = self.get_cooikes()
        print('读取用户cookies！！')
        self.login_with_cookies(d)
        print('通过cookies访问主页！！')

    def __is_succeed(self):
        time.sleep(2)
        try:
            print("self.browser.current_url:",self.browser.current_url)
            a=self.browser.find_element_by_class_name("me_name")
            print('me_name！')
            self.__save_cookies()
            print('登录成功！')
            return True
        except:
            print('登录失败')
            return False


    def __to_login(self, acc, pwd):
        for i in range (1,10):
            self.__inter_info(acc, pwd)
            if(self.__has_verify_code()):
                self.__deal_with_code()
            #time.sleep(5)
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

        return False


        """
                for i in range(10):
            self.__clear_info()
            self.__inter_info(acc, pwd)
            if self.__has_verify_code():
                self.__deal_with_code()
            self.__click_login()
            if self.__is_succeed():
                return True
            elif self.__has_verify_code():
                self.__deal_with_code()
                self.__click_login()
                if self.__is_succeed():
                    return True
            if self.login_abnormal.is_into_inter_phone_num():
                return False
            time.sleep(2)
        return False
        """

    def login(self, acc, pwd):
        return self.__to_login(acc, pwd)


if __name__ == '__main__':
    username = '13135350413' #18290599612
    password = "hcc479643ss"

    my_bro = Browser().get_browser()

    if Login(my_bro).login(acc=username, pwd=password):
        print("!")





    """
     if Login(my_bro).login(acc=username, pwd=password):

    acc = 'ii2bhblh9z@sina.cn'
    pwd = '2A1B8E'
    my_bro = Browser().get_browser()
    if Login(my_bro).login(acc=acc, pwd=pwd):

        Abnormal.into_verify(my_bro)

    """
