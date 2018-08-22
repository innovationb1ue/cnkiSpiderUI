from PyQt5.QtWidgets import *
import threading
import sys
import os
import requests
import time
import re
import ctypes
import inspect
from bs4 import BeautifulSoup as bs

data = {
    'username': '',
    'password': '',
    'keeppwd': 'keepPwd',
    'app': ''}


class SpiderUI(QWidget):
    def __init__(self):
        self.s = requests.session()
        self.GetCount = 0
        self.ThreadPool = []
        self.DownloadCount = 0
        self.loseCount = 0
        self.name = 'None'
        self.stop = False
        super().__init__()
        # self.ValidateUser()
        self.setWindowTitle('cnkiSpider v1.02')
        self.initUI()
        self.setFixedSize(300, 300)
        self.center()
        self.show()

    def initUI(self):
        reviewsPositionY = 200
        self.PaperNameLabel = QLabel('请输入英文报纸简称:', self)
        self.PaperNameLabel.move(10, 10)
        # self.PaperNameLabel.show()

        self.PaperName = QLineEdit(self)
        self.PaperName.move(10, 30)
        self.PaperName.setText('SXJJ')
        # self.PaperName.show()

        self.dateLabel = QLabel('输入年份或月份', self)
        self.dateLabel.move(10, 60)
        # self.dateLabel.show()

        self.startdate = QLineEdit(self)
        self.startdate.move(10, 80)
        # self.startdate.show()


        self.intervalLabel = QLabel('下载间隔(s):', self)
        self.intervalLabel.move(160, 10)

        self.interval = QLineEdit(self)
        self.interval.move(160, 30)
        self.interval.setText('0')

        self.DownloadCountLabel = QLabel('已下载数：', self)
        self.DownloadCountLabel.move(10, reviewsPositionY)

        self.DownloadCountindex = QLabel('0', self)
        self.DownloadCountindex.move(70, reviewsPositionY)

        self.loseCountlabel = QLabel('失败数:', self)
        self.loseCountlabel.move(10, reviewsPositionY+60)

        self.loseCountindex = QLabel('0', self)
        self.loseCountindex.move(70, reviewsPositionY+60)


        self.TotalNumLabel = QLabel('获取到的文件数:', self)
        self.TotalNumLabel.move(10, reviewsPositionY+20)

        self.TotalNum = QLabel('0', self)
        self.TotalNum.move(110, reviewsPositionY+20)

        self.DownloadButton = QPushButton('开始下载', self)
        self.DownloadButton.setGeometry(20, 150, 100, 50)
        self.DownloadButton.clicked.connect(self.Start)

        self.StopDownloadButton = QPushButton('停止下载', self)
        self.StopDownloadButton.setGeometry(150, 150, 100, 50)
        self.StopDownloadButton.clicked.connect(self.KillAllThread)
        # self.DownloadButton.show()

        self.ProcessLabel = QLabel('下载进度', self)
        self.ProcessLabel.move(10, reviewsPositionY+40)
        # self.ProcessLabel.show()

    def ValidateUser(self):
        try:
            Validate_resp = requests.session()
            raw = Validate_resp.get('https://innovationb1ue.github.io/Validate.txt').content.decode('utf-8')
            print(raw, type(raw))
            if 'Certificate01' in raw:
                return
            else:
                self.close()
                sys.exit()
        except:
            self.close()
            sys.exit()

    def Start(self):
        t = threading.Thread(target=self.main, args=(self.PaperName.text(), self.startdate.text()))


        self.ThreadPool.append(t)
        t.setDaemon(True)
        t.start()




    def center(self):
        # form a geometry equal to the main window(rectangle here)
        qr = self.frameGeometry()
        # get the middle point of screen
        cp = QDesktopWidget().availableGeometry().center()
        # move the rectangle to center of the screen
        qr.moveCenter(cp)
        # move the top-left point to the top-left point of the rectangle above(centering the window on our screen)
        self.move(qr.topLeft())




#######################################################################################################

    def main(self, papername, year):
        savepath = os.path.abspath('.')+'/download/'
        if not os.path.exists(savepath):
            os.mkdir(savepath)

        self.downlist = self.YearOrMonth(papername, year)

        self.s = requests.session()
        self.login()

        count = 0
        for item in self.downlist:
            content = self.s.get(item).content
            with open(savepath, 'wb') as f:
                f.write(content)
                self.downloadco
            count += 1
            if count == 200:
                self.s = requests.session()
                self.login()
                count = 0


    def login(self):
        data = {'username': 'blueking02', 'password': 'blueking007', 'keeppwd': 'keepPwd', 'app': ''}
        self.s.post('http://wap.cnki.net/touch/usercenter/Account/Validator', data=data)

    def YearOrMonth(self,papername, date):
        if len(date) == 6:
            final = []
            for i in range(1,32):
                if i <=9:
                    final += self.getArticleIDs(papername, date[0:4]+'-'+date[4:]+'-0'+str(i))
                else:
                    final += self.getArticleIDs(papername, date[0:4]+'-'+date[4:]+'-'+str(i))
            return final

        if len(date) ==4:
            urllist = []
            for i in range(1,13):
                if i <=9 :
                    i = '0' + str(i)
                else:
                    i = str(i)
                for day in range(1,32):
                    date_str = date + '-' + i + '-' + str(day)
                    print('Getting:', i, '_', day)
                    urllist += self.getArticleIDs(papername, date_str)
                    print('num:',len(urllist) )
            return urllist
    def getArticleIDs(self, papername,date):

        PostUrl = 'http://navi.cnki.net/knavi/NPaperDetail/GetArticleDataXsltByDate'
        data = {'py':papername, 'pcode':'CCND', 'pageIndex':1, 'pageSize':200, 'date':date}
        resp = requests.post(PostUrl, data=data)
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


        downloadlinklist = []
        for url in ArticleUrlList:
            raw = requests.get(url).content.decode('utf-8')
            soup = bs(raw)
            downurl = soup.find_all("a", attrs={'id':'pdfDown'})[0]['href']
            downloadlinklist.append(downurl.replace('\n', '').replace(' ', ''))

        return downloadlinklist

    def _async_raise(self, tid, exctype):
        """raises the exception, performs cleanup if needed"""
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def stop_thread(self, thread):
        self._async_raise(thread.ident, SystemExit)

    def KillAllThread(self):
        for babies in self.ThreadPool:
            self.stop_thread(babies)
            time.sleep(0.2)
            print(self.ThreadPool)
        self.ThreadPool = []


if __name__ == '__main__':
    a = QApplication(sys.argv)
    e = SpiderUI()
    sys.exit(a.exec_())