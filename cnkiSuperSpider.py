import requests
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import re
import time
from requests.cookies import RequestsCookieJar
import os

class example(object):
    def __init__(self):
        self.headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'}
        self.main()

    def main(self, papername=input('please input papername:')):
        # for auto test
        if papername == '':
            papername = 'GMRB'

        # input year
        year = input('Please input year:')


        urllist = []
        #
        # for i in range(1,13):
        #     if i <=9 :
        #         i = '0' + str(i)
        #     else:
        #         i = str(i)
        #     for day in range(0,32):
        #         date_str = year + '-' + i + '-' + str(day)
        #         urllist += self.getArticleIDs(papername, date_str)
        #         print('Getting:', i, '_', day)

        # options = webdriver.ChromeOptions()
        # prefs = {'download.default_directory': '/Users/JeffB1ue/Downloads/ChromeDownloads/'}
        # options.add_experimental_option('prefs', prefs)
        # driver = webdriver.Chrome('d:/chrome/chromedriver', chrome_options=options)
        #
        # driver.get('http://login.cnki.net/login/?platform=kns&ReturnURL=http://www.cnki.net/')
        # handle1 = driver.current_window_handle
        # username = driver.find_element_by_id('TextBoxUserName')
        # username.send_keys('blueking02')
        # password = driver.find_element_by_id('TextBoxPwd')
        # password.send_keys('blueking007')
        #
        # btn1 = driver.find_element_by_id('Button1')
        # btn1.click()
        # time.sleep(2)

        s = requests.session()
        data = {'username':'blueking02', 'password':'blueking007', 'keeppwd':'keepPwd', 'app':''}
        s.post('http://wap.cnki.net/touch/usercenter/Account/Validator', data=data)

        content = s.get('http://wap.cnki.net/touch/usercenter/Zone/Index').content.decode('utf-8')
        print(content)

        content = s.get('http://kns.cnki.net/kns/download.aspx?filename=zZGlWa3MkS1hUaMFnMthmU4dkapF2Z1cmWz4UQnFGehlXNkFGZW9mZHxkeFdnYhRGOzsicwN0cMZGVWFWVQR1b=0TPnBzUFlkeBtGbpRXRXZ0Q38GRk9SM1dFM4QVcvBFS2Z0QYRTSmNWeUF0RYd1dalVcm1UVvlEeqJTaU1mW2I&tablename=CCNDCOMMIT_DAY&dflag=pdfdown').content

        f = open(os.path.abspath('.')+'/1.pdf', 'wb')
        f.write(content)
        f.close()


        print(len(urllist))



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

        downloadlinklist = []
        for url in ArticleUrlList:
            raw = requests.get(url).content.decode('utf-8')
            soup = bs(raw)
            downurl = soup.find_all("a", attrs={'id':'pdfDown'})[0]['href']
            downloadlinklist.append(downurl.replace('\n', '').replace(' ', ''))

        return downloadlinklist








if __name__ == '__main__':
    e = example()
