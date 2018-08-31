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
        self.setWindowTitle('cnkiSpider v1.10')
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

        self.checkBtn = QPushButton('check', self)
        self.checkBtn.setGeometry(150, 110, 60, 30)
        self.checkBtn.clicked.connect(self.check)
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

        self.downlist, self.namelist = self.YearOrMonth(papername, year)

        print(self.downlist)
        print(len(self.downlist))
        print(len(self.namelist))
        self.s = requests.session()
        self.login()

        for i in range(len(self.namelist)):
            pos = i
            self.namelist[pos] = self.namelist[pos].replace('*', ' ')
            self.namelist[pos] = self.namelist[pos].replace('?', ' ')
            self.namelist[pos] = self.namelist[pos].replace('\r', ' ')
            self.namelist[pos] = self.namelist[pos].replace('\n', ' ')
            self.namelist[pos] = self.namelist[pos].replace(':', ' ')
            self.namelist[pos] = self.namelist[pos].replace('\\', ' ')
            self.namelist[pos] = self.namelist[pos].replace('<', ' ')
            self.namelist[pos] = self.namelist[pos].replace('>', ' ')
            self.namelist[pos] = self.namelist[pos].replace('|', ' ')
            self.namelist[pos] = self.namelist[pos].replace('”', ' ')
            self.namelist[pos] = self.namelist[pos].replace('“', ' ')
            self.namelist[pos] = self.namelist[pos].replace('"', ' ')
            self.namelist[pos] = self.namelist[pos].replace('/', ' ')
            self.namelist[pos] = self.namelist[pos].replace('%', ' ')
            self.namelist[pos] = self.namelist[pos].replace(' ', ' ')

        # download logic
        for downloadlink, title in zip(self.downlist, self.namelist):
            try:
                # check whether file existed
                if os.path.exists(savepath + title + '.pdf'):
                    self.DownloadCount += 1
                    self.DownloadCountindex.setText(str(self.DownloadCount))
                    self.DownloadCountindex.adjustSize()
                    continue

                # if not existed, download and save
                content = self.s.get(downloadlink).content
                with open(savepath + title + '.pdf', 'wb') as f:
                    f.write(content)
                    self.DownloadCount += 1
                    self.DownloadCountindex.setText(str(self.DownloadCount))
                    self.DownloadCountindex.adjustSize()

                # check file content
                try:
                    count = 0
                    while '错误' in content.decode('utf-8') or '登录' in content.decode('utf-8') or '504' in content.decode('utf-8'):
                        count += 1
                        self.s = requests.session()
                        self.login()
                        content = self.s.get(downloadlink).content
                        with open(savepath + title + '.pdf', 'wb') as f:
                            f.write(content)
                        time.sleep(1)
                        if count == 10:
                            self.downlist.append(downloadlink)
                            self.namelist.append(title)
                            self.GetCount += 1
                            self.TotalNum.setText(str(self.GetCount))
                            self.TotalNum.adjustSize()
                            break
                    if '频繁' in content.decode('utf-8'):
                        i = 0
                        while i < 300:
                            time.sleep(1)
                            self.s = requests.session()
                            self.login()
                            content = self.s.get(downloadlink).content
                            with open(savepath + title + '.pdf', 'wb') as f:
                                f.write(content)
                            if '频繁' not in content.decode('utf-8'):
                                break
                            i += 1

                except ValueError:
                    pass

            # file failed to down load will be added to the end of the list
            except(OSError, IOError):
                self.downlist += [downloadlink]
                self.namelist += [title]
                f1 = open(os.path.abspath('.')+'/log.txt', 'a+')
                f1.write(title+'\n \r\n')
                f1.close()
                self.loseCount += 1
                self.loseCountindex.setText(str(self.loseCount))
                self.loseCountindex.adjustSize()
                continue
    def check(self):
        t = threading.Thread(target=self.check1)
        t.setDaemon(True)
        t.start()



    def check1(self):
        self.DownloadCount =0
        savepath = os.path.abspath('.')+'/download/'
        for downloadlink, title in zip(self.downlist, self.namelist):
            try:
                if os.path.exists(savepath + title + '.pdf'):
                    self.DownloadCount += 1
                    self.DownloadCountindex.setText(str(self.DownloadCount))
                    self.DownloadCountindex.adjustSize()
                    continue
                self.s = requests.session()
                self.login()
                content = self.s.get(downloadlink).content
                with open(savepath + title + '.pdf', 'wb') as f:
                    f.write(content)
                    self.DownloadCount += 1
                    self.DownloadCountindex.setText(str(self.DownloadCount))
                    self.DownloadCountindex.adjustSize()
                try:
                    count = 0
                    while '错误' in content.decode('utf-8') or '登录' in content.decode('utf-8'):
                        count += 1
                        self.s = requests.session()
                        self.login()
                        content = self.s.get(downloadlink).content
                        time.sleep(1)
                        with open(savepath + title + '.pdf', 'wb') as f:
                            f.write(content)
                            self.DownloadCount += 1
                            self.DownloadCountindex.setText(str(self.DownloadCount))
                            self.DownloadCountindex.adjustSize()
                        if count == 10:
                            self.downlist.append(downloadlink)
                            self.namelist.append(title)
                            self.GetCount += 1
                            self.TotalNum.setText(str(self.GetCount))
                            self.TotalNum.adjustSize()
                            break
                    if '频繁' in content.decode('utf-8'):
                        i = 0
                        while i < 300:
                            time.sleep(1)
                            self.s = requests.session()
                            self.login()
                            content = self.s.get(downloadlink).content
                            with open(savepath + title + '.pdf', 'wb') as f:
                                f.write(content)
                            if '频繁' not in content.decode('utf-8'):
                                break
                            i += 1

                except ValueError:
                    pass

            except(OSError, IOError):
                f1 = open(os.path.abspath('.')+'/log.txt', 'a+')
                f1.write(self.name+'\n \r\n')
                f1.close()
                self.loseCount += 1
                self.loseCountindex.setText(str(self.loseCount))
                self.loseCountindex.adjustSize()
                continue


    # def downloadSingleFile(self, url, title):
    #     self.s = requests.session()
    #     self.login()
    #     savepath = os.path.abspath('.')+'/download/'
    #     content = self.s.get(url).content
    #     with open(savepath + title + '.pdf', 'wb') as f:
    #         f.write(content)
    #     return content

    def login(self):
        self.s = requests.session()
        data = {'username': 'blueking02', 'password': 'blueking007', 'keeppwd': 'keepPwd', 'app': ''}
        self.s.post('http://wap.cnki.net/touch/usercenter/Account/Validator', data=data)

    def YearOrMonth(self,papername, date):
        if len(date) == 6:
            final = []
            name = []
            for i in range(1,32):
                temp_final, temp_name = [], []
                # print('Getting:', i)
                self.ProcessLabel.setText('Getting:'+date[4:]+'-' +str(i))
                self.ProcessLabel.adjustSize()
                if i <=9:
                    temp_final, temp_name = self.getArticleIDs(papername, date[0:4]+'-'+date[4:]+'-0'+str(i))
                    final += temp_final
                    name += temp_name
                else:
                    temp_final, temp_name = self.getArticleIDs(papername, date[0:4]+'-'+date[4:] + '-'+str(i))
                    final += temp_final
                    name += temp_name

                self.GetCount += len(temp_final)
                self.TotalNum.setText(str(self.GetCount))
                self.TotalNum.adjustSize()
            return final, name

        if len(date) == 4:
            urllist, names = [], []
            for i in range(1,13):
                if i <= 9:
                    urllist_temp, names_temp = self.YearOrMonth(papername, date+'0'+str(i))
                    urllist += urllist_temp
                    names += names_temp
                else:
                    urllist_temp, names_temp = self.YearOrMonth(papername, date +str(i))
                    urllist += urllist_temp
                    names += names_temp

            return urllist, names


    def getArticleIDs(self, papername,date):

        PostUrl = 'http://navi.cnki.net/knavi/NPaperDetail/GetArticleDataXsltByDate'
        data = {'py':papername, 'pcode':'CCND', 'pageIndex':1, 'pageSize':200, 'date':date}
        resp = requests.post(PostUrl, data=data)
        content = resp.content.decode('utf-8')
        pattern = 'ShareUrl(.*?)ournalname'



        linkInfo = re.findall(pattern, content, re.S)

        if linkInfo == []:
            print('空', date)
            return [], []

        final = []
        for i in range(int(len(linkInfo)/6)):
            final.append(linkInfo[i*6])
        # print(len(final))

        filenameList, DBnameList = [], []

        filenamePattern = 'fileName=(.*?)\',\''
        for item in final:
            temp = re.findall(filenamePattern, item, re.S)
            filenameList.append(temp[0])
        # print(filenameList)
        # print(len(filenameList))

        DBnamePattern = r'DBName=(.*?)&amp'
        for item in final:
            temp = re.findall(DBnamePattern, item, re.S)
            DBnameList.append(temp[0])

        # print(DBnameList)
        # print(len(DBnameList))

        titlePattern = "\',\'(.*?).j"
        titles = []

        for item in final:
            temp = re.findall(titlePattern, item, re.S)
            titles.append(temp[0].split("\',\'")[1])




        ArticleUrlList = []
        for i in range(len(filenameList)):
            ArticleUrlList.append('http://kns.cnki.net/kcms/detail/detail.aspx?dbcode=CCND&filename='+filenameList[i]+'&dbname='+DBnameList[i])


        downloadlinklist = []
        for url in ArticleUrlList:
            raw = requests.get(url).content.decode('utf-8')
            soup = bs(raw)
            try:
                downurl = soup.find_all("a", attrs={'id':'pdfDown'})[0]['href']
                downloadlinklist.append(downurl.replace('\n', '').replace(' ', ''))
            except IndexError:
                pass



        return downloadlinklist, titles

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
