import requests
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import re
import time

class example(object):
    def __init__(self):
        self.headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'}
        self.main()

    def main(self, papername=input('please input papername')):
        # for auto test
        if papername == '':
            papername = 'QHBR'

        # input year
        year = '2015'


        urllist = []

        for i in range(1,13):
            if i <=9 :
                i = '0' + str(i)
            else:
                i = str(i)
            for day in range(0,32):
                date_str = year + '-' + i + '-' + str(day)
                urllist += self.getArticleIDs(papername, date_str)
                print('Getting:', i, '_', day)
        # urllist = self.getArticleIDs('QHBR', '2015-09-30')

        options = webdriver.ChromeOptions()
        prefs = {'download.default_directory': '/Users/JeffB1ue/Downloads/ChromeDownloads/'}
        options.add_experimental_option('prefs', prefs)
        driver = webdriver.Chrome('./chromedriver', chrome_options=options)

        driver.get('http://login.cnki.net/login/?platform=kns&ReturnURL=http://www.cnki.net/')
        handle1 = driver.current_window_handle
        username = driver.find_element_by_id('TextBoxUserName')
        username.send_keys('blueking02')
        password = driver.find_element_by_id('TextBoxPwd')
        password.send_keys('blueking007')

        btn1 = driver.find_element_by_id('Button1')
        btn1.click()
        time.sleep(1)
        print(len(urllist))
        downloadcount = 0
        for url in urllist:
            driver.get(url)
            time.sleep(1)
            pdfdownbtn = driver.find_element_by_id('pdfDown')
            pdfdownbtn.click()
            time.sleep(1)
            while len(driver.window_handles) != 1:
                handles = driver.window_handles
                for handle in handles:
                    if handle != handle1:
                        handle2 = handle
                driver.switch_to.window(handle2)
                driver.close()
                driver.switch_to.window(handle1)
                pdfdownbtn.click()
                time.sleep(1.5)
            downloadcount+=1
            print('已下载:', downloadcount)



    def getArticleIDs(self, papername,date):
        PostUrl = 'http://navi.cnki.net/knavi/NPaperDetail/GetArticleDataXsltByDate'
        data = {'py':papername, 'pcode':'CCND', 'pageIndex':1, 'pageSize':100, 'date':date}
        resp = requests.post(PostUrl, data=data, headers=self.headers)
        content = resp.content.decode('utf-8')
        pattern = 'ShareUrl(.*?)journalname'

        linkInfo = re.findall(pattern, content, re.S)
        # print(linkInfo)
        # print(len(linkInfo))
        final = []
        for i in range(int(len(linkInfo)/6)):
            final.append(linkInfo[i*6])
        # print(final)
        # print(len(final))

        filenameList, DBnameList = [], []

        filenamePattern = 'fileName=(.*?)\',\''
        for item in final:
            temp = re.findall(filenamePattern, item, re.S)
            filenameList.append(temp)
        for i in range(0,len(filenameList)):
            filenameList[i] = filenameList[i][0]
        # print(filenameList)
        # print(len(filenameList))

        DBnamePattern = r'DBName=(.*?)&amp'
        for item in final:
            temp = re.findall(DBnamePattern, item, re.S)
            DBnameList.append(temp)
        for i in range(0, len(DBnameList)):
            DBnameList[i] = DBnameList[i][0]
        # print(DBnameList)
        # print(len(DBnameList))

        ArticleUrlList = []
        for i in range(len(filenameList)):
            ArticleUrlList.append('http://kns.cnki.net/kcms/detail/detail.aspx?dbcode=CCND&filename='+filenameList[i]+'&dbname='+DBnameList[i])

        print(ArticleUrlList)

        return ArticleUrlList








if __name__ == '__main__':
    e = example()
