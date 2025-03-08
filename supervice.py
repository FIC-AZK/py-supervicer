#<-- coding UTF-8 -->
"""
- 直接运行该文件会直接以debug脚本形式进入监控,并在最后清空Log
- 我写这个类的时候是按照使用者阅读了注释之后理解代码之后写的，
- 希望你不会把重要的文件夹作为log文件夹之后开了clear
"""

import pygetwindow as gw
import pyautogui
import time
import threading
import os
import socket
import shutil


# 监视目前所聚焦窗口，并将其打开时间与名称记录，并对敏感项截图
# 如果要关闭，创建新线程将notStop改为False
class supervicer():
    # config
    configed = False
    # 配置信息
    hostName = socket.gethostname()
    # 开始前是否清空
    clear = False
    # debug开关
    debug = True
    # 日志保存位置<dir>
    logsSavePath = 'Log'
    # 日志名称 以及全局路径
    logsName = 'logs.txt'
    logsFilePath = os.path.join(logsSavePath,logsName)
    # 截图保存位置<dir{logsSavepath\\ScreenShot}>
    picSavePath = os.path.join(logsSavePath,'ScreenShot')
    # 截图窗口关键字
    browslist = ['chrome', 'firefox', 'edge', 'opera', '360', 'qq']
    # 白名单
    unShotList = ['新标签', '新页']
    # 轮询休眠(单位:秒)
    sleeptime = 0.5
    # 是否停止
    notStop = True


    def debugPrint(self, outputs=str):
        if self.debug:
            print("supervice.py:\t\t",outputs+'\n')


    def __init__(self, debug=bool):
        self.debugPrint("sys:\t创建class Supervicer\n")
        self.debug = debug

    # 设置监视程序的各个信息
    # logsSavePath: 日志储存位置，会在该位置的logs.txt储存聚焦窗口记录，在该目录中的ScreenShot子目录储存截图
    def config(self, logsSavePath=str, screenShotWindowNameList=list, unShotlist=list, sleepTime=float, ifclear=bool, ifdebug=bool)->bool:
        if ifdebug:
            self.debug = bool(ifdebug)
        self.clear = bool(ifclear)
        self.unShotList = list(unShotlist)  # 白名单
        # 自动储存位置分析
        if os.path.isdir(logsSavePath):
            if os.path.isabs(logsSavePath):
                self.logsSavePath = str(logsSavePath)
            else:
                self.logsSavePath = os.path.abspath(logsSavePath)
        else:
            if os.path.isfile(str(logsSavePath)):
                self.logsSavePath = os.path.dirname(os.path.abspath(str(logsSavePath)))
                self.debugPrint("warning:\tlogsSavePath日志目录是一个文件，真的没问题吗？(已自动转至文件父级目录)\n")
            else:
                os.makedirs(str(logsSavePath))
                self.logsSavePath = os.path.abspath(str(logsSavePath))
                self.debugPrint("warning:\t你输入的logsSavePath是新目录吗，已经创建\n")
        self.picSavePath = os.path.join(os.dirname(logsSavePath),"ScreenShoot")
            
        self.browslist = list(screenShotWindowNameList)
        self.sleeptime = float(sleepTime)
        if sleepTime >= 20:
            self.debugPrint("warning:\tsleepTime轮询间隔过大，是否应该检查一下？\n")
        if sleepTime <= 0.01:
            self.debugPrint("warnging:\tsleepTime轮询间隔过小，真的需要如此频繁吗？\n")
        self.configed = True

        self.debugPrint()
        return True


    '''
    # 从.txt文件导入配置
    def configWithTxts(self):
        pass
    '''

    '''
    # 从.js文件导入配置
    def configWithJS(self):
        pass
    '''

    def getLogsFileName(self):
        self.logsFilePath = os.path.join(self.logsSavePath,self.logsName)
        self.debugPrint(f"sys:\t日志储存位置为{self.logsFilePath}\n")
        return self.logsFilePath


    # 清空文件
    def trunkUse(self, newFileString):
        with open(self.logsFilePath,'w',encoding='utf-8') as trunkfile:
            trunkfile.write(newFileString)
            trunkfile.close()
        self.debugPrint("sys:\t已清空日志文件\n")
        return True


    # 检查当前窗口是否有截屏目标特征,且不为白名单
    def checkIsBrowser(self, String):
        for whiteName in self.unShotList:
            if whiteName.lower() in String.lower():
                return False
        for browsername in self.browslist:
            if browsername.lower() in String.lower():
                return True
        return False


    # 按照"YYYYmmddHHMMSS:       String\n"的格式输出
    def fwrite(self, inPutingString):
        return str(time.strftime('%Y%m%d%H%M%S',time.localtime()) + u":\t\t" + inPutingString + u"\n")


    # 将所用目录合为绝对目录
    def makeSurePathAbs(self):
        if not os.path.isabs(self.logsFilePath):
            self.logsFilePath = os.path.abspath(self.logsFilePath)
        if not os.path.isabs(self.picSavePath):
            self.picSavePath = os.path.abspath(self.picSavePath)


    # 确保日志目录存在
    def makeSurePicSaveDir(self):
        self.makeSurePathAbs()
        if not os.path.exists(self.picSavePath):
            try:
                os.makedirs(self.picSavePath)
                self.debugPrint("sys:\t创建截图保存路径:"+self.picSavePath+'\n')
            except OSError as e:
                self.debugPrint("sys:\t无法创建截图保存路径:"+e+'\n')



    # 对当前窗口截屏(包含验证)
    # 创建绝对路径全称为<{picSavePath(已经为绝对路径)}\\{YYYYmmddHHMMSS.png}>的图片并尝试保存
    def ActiveWindowScreenShot(self, activateWindowName):
        activeWindow = gw.getActiveWindow()
        time.sleep(1)
        if activeWindow and activateWindowName == activeWindow.title:
            screenshot = pyautogui.screenshot(region=(activeWindow.left, activeWindow.top, activeWindow.width, activeWindow.height))
            fileName = os.path.join(self.picSavePath, self.hostName+str(int(time.strftime('%Y%m%d%H%M%S', time.localtime())))+".png")
            try:
                screenshot.save(fileName)
                self.debugPrint("sys:\t已保存为" + fileName + '\n')
            except Exception as e:
                self.debugPrint("Error:\t截图保存失败:", e, '\n')
        else:
            self.debugPrint("sys:\t窗口在短时间内关闭或不是浏览器窗口\n")

        
    # 新线程内延时截图，防止占用轮询时间
    def creatScreenShotThread(self, windowName):
        newThred = threading.Thread(target=self.ActiveWindowScreenShot, args=(windowName,))
        newThred.start()


    # 清理日志
    def clearLogs(self):
        self.debugPrint("sys:\t开始清理日志文件夹\n")
        self.trunkUse("-*- coding utf-8 -*-\n")
        shutil.rmtree(self.picSavePath)
        os.makedirs(self.picSavePath)
        self.debugPrint("sys:\t已清除截屏\n")


    # 记录主窗口，你不应该直接使用
    def runLogs(self):
        self.debugPrint("sys:\t开始记录\n")
        with open(self.logsFilePath,'a',encoding='utf-8') as log:
            lastWindowName = gw.getActiveWindowTitle()
            log.write(self.fwrite(lastWindowName))
            while self.notStop:
                thisWindowName = gw.getActiveWindowTitle()
                # 判断当前聚焦的程序已更换，且不为空，保存到logs save path中
                if not thisWindowName == lastWindowName and not thisWindowName == "Program Manager" and not thisWindowName == "":
                    log.write(self.fwrite(thisWindowName))
                    self.debugPrint(self.hostName+' looking :'+thisWindowName+'\n')
                    lastWindowName = thisWindowName
                    # 如果当前窗口是浏览器，调用新线程保存截图
                    if self.checkIsBrowser(thisWindowName):
                        self.creatScreenShotThread(thisWindowName)
                # 适当休眠
                time.sleep(self.sleeptime)
                self.debugPrint("sys:\t休眠...\n")
            self.debugPrint("sys:\tnotStop不为True,停止运行\n")

    
    # 创建记录进程
    def creatRunLogsThread(self):
        self.debugPrint("sys:\tcreatRunLogsThread:\t创建监视线程\n")
        newthread = threading.Thread(target=self.runLogs)
        newthread.start()

        self.debugPrint("sys:\tcreatRunLogsThread:\t监视线程开始运行\n")
        return True


    # 监视函数主体
    def startSupervice(self, useDefaltConfig = False, playClear = True):
        if useDefaltConfig == False and self.config == False:
            return False
        self.makeSurePicSaveDir()
        if self.clear:
            self.clearLogs()
        self.creatRunLogsThread()
        return True
        

if __name__ == '__main__':
    #debug = True
    #clear = True
    supervice = supervicer(True)
    supervice.startSupervice(True, False)
    os.system('echo 按任意键终止')
    os.system('pause')
    supervice.notStop = False
    time.sleep(1)
    supervice.clearLogs()