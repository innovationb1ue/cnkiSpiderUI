import requests
from selenium import webdriver
import re
from bs4 import BeautifulSoup as bs
import xlrd
import csv
import codecs
import time

# 名单
NamesPath = './Names.xls'

# Chromedriver path
ChromedriverPath = 'D:/Chrome/chromedriver'

# 保存的CSV
csvPath = './YearsCount.csv'

class YearsCount(object):
    def __init__(self):
        self.driver = webdriver.Chrome(ChromedriverPath)


        self.main()

    def main(self):
        # get names from xls
        Names = self.GetNames()
        # init search page
        self.initPage()

        # do search and save result
        self.research(Names)


    def initPage(self):
        self.driver.get('http://kns.cnki.net/kns/brief/result.aspx?dbprefix=CCND')
        time.sleep(10)


    def GetNames(self):
        workbook = xlrd.open_workbook(NamesPath)
        booksheet = workbook.sheet_by_index(0)
        Names = booksheet.col_values(0)
        return Names

    def research(self, Names):
        countPattern = r'color:#999;">((.*?))</span>'
        textinput = self.driver.find_element_by_id('magazine_value1')
        btnsearch = self.driver.find_element_by_id('btnSearch')
        for name in Names:
            textinput.send_keys(name)
            btnsearch.click()
            textinput.clear()
            time.sleep(3)
            pageSource = self.driver.page_source
            count = re.findall(countPattern, pageSource, re.S)
            if count == []:
                count = 0
            else:
                count = str(count[0][0])
            print('name =', name)
            print('count = ',count)
            with codecs.open (csvPath, 'a+', 'gbk') as f:
                writer = csv.writer(f)
                writer.writerow([name,count])

            time.sleep(3)


if __name__ == '__main__':
    e = YearsCount()
