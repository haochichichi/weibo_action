from settings import *

import requests, json


"""
读写用户表
"""
import csv

class Table_csv:
    def __init__(self):
        self.url= TABLE_CSV
        self.Nurl = TABLE_CSV_NEW
    
    def read_table(self):
        """
         with open(self.url, 'r', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            column = [row for row in reader]

        :return:
        """
        with open(self.url, encoding="utf-8") as f:
            table=[]
            reader = csv.DictReader(f)
            for row in reader:
                if(row['username']!='username'):
                    array = {'username': '', 'password': '', 'cookies': '', 'comment': ''}
                    array['username'] = row['username']
                    array['password'] = row['password']
                    array['cookies'] = row['cookies']
                    array['comment'] = row['comment']
                    table.append(array)
        print('[table]', table)
        return table

    def write_table(self,table):
        with open( self.url, 'w+', newline='')as f:
            writer = csv.DictWriter(f, fieldnames=('username', 'password', 'cookies', 'comment'))
            writer.writeheader()  # 写入头
            for row in table:
                writer.writerow(row)

    def save_cookies(self,cookies_dict,username):
        table = Table_csv().read_table()
        try:
            for row in table:
                if row['username'] == username:
                    row['cookies'] = json.dumps(cookies_dict, ensure_ascii='False', indent=4)
                    #row['cookies'] = json.dumps(cookies_dict)
                    Table_csv().write_table(table)
                    print("[save_cookies]>成功", username)
                    return True
            print("[save_cookies]>未找到用户！", username)
            return False
        except:
            print("[save_cookies]>存储出错！", username)
            return False


    def find_cookies(self,username):
        table = Table_csv().read_table()
        try:
            for row in table:
                if row['username'] == username:
                    print("[find_cookies]>成功", username)
                    return json.loads(row['cookies'])
            print("[find_cookies]>未找到用户！", username)
            return 0
        except:
            print("[save_cookies]>查询出错！", username)
            return 1

    def check_table(self):
        wrong=0
        error=0
        success=0
        total=0
        table = Table_csv().read_table()
        try:
            for row in table:
                if row['cookies'] == json.dumps("error", ensure_ascii='False', indent=4)or row['cookies'] =='':
                    error +=1
                elif row['cookies'] == json.dumps("wrong", ensure_ascii='False', indent=4)or row['cookies'].find("Apache")==-1:
                    wrong +=1
                else:
                    success+=1
                total+=1
            check = success / total
            print("[错误]" + str(error) + "[无效]" + str(wrong) + "[成功]" + str(success) + "[成功率]" + str(check))
            print("[check_table]>成功")
        except:
            print("[check_table]>检查出错！")




if __name__ == "__main__":
    table=Table_csv().read_table()
    Table_csv().write_table(table)
    cookies={'Apache': '123.112.15.224_1599290353.371911', 'SINAGLOBAL': '123.112.15.224_1599290353.371910', 'U_TRS1': '000000b7.be449eef.5f533bef.ab7e15c3', 'ULV': '1599290352872:1:1:1:123.112.15.224_1599290353.371911:', 'bdshare_firstime': '1599290363996', 'U_TRS2': '000000b7.be4e9eef.5f533bef.a8357bb2', 'SUB': '_2A25yV0uqDeRhGeFK6FMW9C3IwjiIHXVRJTpirDV_PUNbm9AKLWvVkW9NQ2DTj1DMj6Cb7HwGZujShaZ7lIG7WoO7', 'ULOGIN_IMG': 'tc-a33cf8b630d6b2af1c0f15746ee35ac4d0d6', 'UOR': ',my.sina.com.cn,', 'SCF': 'Au7JFgwlxhUOzQP4y89uSU3_b0QTC7SP1-xvkl_uRO52y9fvZpRi5Ofp_8WSjthXcuBJjlIAytX1gh2ssCmxTrQ.', 'SUBP': '0033WrSXqPxfM725Ws9jqgMF55529P9D9W5sKRApzv35Me2A_rjhCA7E5NHD95QNShepS0B0Sh.XWs4DqcjZds8VIJLydJiDP7tt', 'ALF': '1630826362', 'sso_info': 'v02m6alo5qztayYlrmqmpaFrpimpZ-Jp5WpmYO0t42DjLGNs5CzjYOktA=='}
    Table_csv().save_cookies(cookies,'16687332479')
    table = Table_csv().read_table()
    cookies_dict=Table_csv().find_cookies('16687332479')
    response = requests.get('http://my.sina.com.cn/profile/', cookies=cookies_dict, timeout=5, allow_redirects=False)
    if response.status_code == 200:
        if 'me_name' in response.text:
            print('[cookies 登录]>成功')
        else:
            print('[cookies 登录]>登录失败！')
    else:
        print('[cookies 登录]>传输失败！')
    print(cookies)
    cookies=Table_csv().find_cookies('1')
    print(cookies)

    wrong = 0
    error = 0
    success = 0
    Table_csv().check_table()