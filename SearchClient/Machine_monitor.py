# -*- coding: utf-8 -*-
"""
Created on 20221109 
# 目的： 监控TOF仪器是否报错
# 原理：监控TOF的CompassHyStarErrorLogbook.log是否发生改变，如果改变了，则说明TOF的仪器出现问题,
#       会自动发送文本到指定的电脑上，由该电脑完成报警信息。

# 1、监测某个文件是否发生改变
# 2、一旦发生改变，触发某个事件（函数）发生。
"""
import os
import time
import codecs
import socket
import sys
import struct
import re

currentPath = os.getcwd()
chunkSize = 1024000

def Initial_Run(Param1,Param2,Param3,Param4,Param5,Param6,Param7):
    global msType,ms,filePath,logPattern,ErrorPattern,recordCT,recordfLNumber,recordfileSize,timeInterval,serverHost,port,Exclude_Info
    msType,ms,logPattern,ErrorPattern,filePath,timeInterval,Analyzer_Info = Param1,Param2,Param3,Param4,Param5,Param6,Param7
    info = ms + '仪器可能出问题了，请及时查看。如已查看，可以忽略此信息。'
    logPattern = logPattern[:-1]
    port,serverHost = str(Analyzer_Info).split(':')
    timeInterval = int(timeInterval)
    #print(str(currentPath) + '\t' + str(msType) + '\t' + str(ms) + '\t' + str(logPattern) + '\t' + str(ErrorPattern) + '\t' + str(filePath) + '\t' + str(timeInterval))
    Info_Exclude = os.path.join(os.getcwd(),'Config','Warn_Info_Exclude.txt')
    Exclude_Info = list()
    if os.path.exists(Info_Exclude):
        for Info in open(Info_Exclude):
            Exclude_Info.append(Info)
    
    def logwrite(words,timestr=True):
        # 日志目录
        logFolder = os.path.join(currentPath,'log')
        if not os.path.exists(logFolder):
            os.mkdir(logFolder)     
        logFiles = os.path.join(currentPath, r'log/Warnlog' + '.txt')
        # 读写模式a: 写入文件，若文件不存在则会先创建再写入，但不会覆盖原文件，而是追加在文件末尾
        with codecs.open(logFiles,"a+",'utf-8') as f:
            if timestr:
                dateTime = time.strftime('%Y%m%d %H:%M:%S', time.localtime()) #日期-时间
                contents = dateTime + "  " + words + " \n"  #添加换行符，以便更好地人为读取
                f.write(contents)  # 自带文件关闭功能，不需要再写f.close()
            else:
                f.write(words)
    def errorlogwrite(words,timestr=True):
        # 日志目录
        logFolder = os.path.join(currentPath,'log')
        if not os.path.exists(logFolder):
            os.mkdir(logFolder)    
        logFiles = os.path.join(currentPath, r'log/ErrorLog' + '.log')
        with codecs.open(logFiles,"a+",encoding="utf-8") as f:
            if timestr:
                dateTime = time.strftime('%Y%m%d %H:%M:%S', time.localtime()) #日期-时间
                contents = dateTime + "  " + str(words)  + " \n"#添加换行符，以便更好地人为读取
                f.write(contents)  # 自带文件关闭功能，不需要再写f.close()
            else:
                f.write(words)

    def logwrite2(words,timestr=True):
        # 日志目录
        logFolder = os.path.join(currentPath,'log')
        if not os.path.exists(logFolder):
            os.mkdir(logFolder)    
        logFiles = os.path.join(currentPath, r'log/sentLog' + '.txt')
        with codecs.open(logFiles,"a+",'utf-8') as f:
            if timestr:
                dateTime = time.strftime('%Y%m%d %H:%M:%S', time.localtime()) #日期-时间
                contents = dateTime + "  " + words + " \n"#添加换行符，以便更好地人为读取
                f.write(contents)  # 自带文件关闭功能，不需要再写f.close()
            else:
                f.write(words)
    
    # 单文件传输
    def socket_client(Warn_File):
        #print(str(Warn_File) + 'will be send')
        # 1.连接socket server
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((serverHost, int(port)))
            # 2.传输文件
            # 判断是否为文件
            if os.path.isfile(Warn_File):
                # 定义定义文件信息。128s表示文件名为1024sdbytes长，l表示一个int或log文件类型，在此为文件大小
                fileinfo_size = struct.calcsize('1024sd')
                # 定义文件头信息，包含文件名和文件大小
                fhead = struct.pack('1024sd', os.path.basename(Warn_File).encode('utf-8'), os.stat(Warn_File).st_size)
                # 发送文件名称与文件大小
                s.send(fhead)
                # 将传输文件以二进制的形式分多次上传至服务器
                fp = open(Warn_File, 'rb')
                while 1:
                    data = fp.read(chunkSize)
                    if not data:
                        print ('{0} file send over...'.format(os.path.basename(Warn_File)))
                        break
                    s.send(data)
                # 关闭当期的套接字对象
                s.close()
            
            # 3.记录一下
            logwrite2(Warn_File)
        
        except Exception as reason:
            errorlogwrite(reason)
    
    # 获取报错文件新增内容
    def newLines(fp,lastSize):
        textLine = []
        if msType == 'timsTOF':
            Encode = 'utf-16 LE'
        elif msType == 'SCIEX':
            Encode = 'Windows-1252'
        else:
            Encode = 'utf-8'
        with open(fp, 'r',encoding = Encode) as f:
            f.seek(lastSize) #读取文本的指针定位到上一次的文本末尾
            for each in f:
                textLine.append(each) #将新增的每一行存在textLine列表中
        return textLine
    
    # 解析文件错误内容
    def GetError(recordfilePath,filePath,recordfileSize):
        if recordfilePath != filePath:
            # 获取文件的新内容
            newText1 = newLines(fp = recordfilePath,lastSize= int(recordfileSize)) # 旧文件的内容
            # print(newText1)
            newText2 = newLines(fp = filePath,lastSize= int(0)) # 新文件的内容
            newText = newText1 + newText2
            #recordfilePath = filePath  # 新文件的话，要重头读取并重新定义recordfilePath
        else:
            newText = newLines(fp = filePath,lastSize= int(recordfileSize))
            #print(newText)
        recordfileSize = os.path.getsize(filePath)   # 重新定义recordfileSize
                        
        # 解析新增内容,获取关于error的信息
        if len(newText) > 0:
            #print("I can get the error information when the file changed!")
            errortext = parseText(textLine = newText,errorWords = ErrorPattern)
        else:
            errortext = []
        # 4、如果有ERROR，则将报错信息通知到负责人
        if len(errortext) > 0:
            mainFunc(errortext)
        else:
            print('No Error')
    
    # 监控TOF/SCIEX仪器是否报错-单个文件
    def monitorFile(recordT,filePath,fileSize):
        global recordfileSize
        # 当前文件的修改时间
        currentChangeTime = os.path.getmtime(filePath)
        #print('正在监测文件是否发生改变……')
        if recordT != currentChangeTime:
            recordT = os.path.getmtime(filePath)
            # 执行函数 获取关于error的信息
            GetError(filePath,filePath,int(fileSize))
            recordT = os.path.getmtime(filePath)
            recordfileSize = os.path.getsize(filePath)
        print('函数执行完毕，下一轮监控开始啦！！！')
        return recordT
    
    # 专门用来存放发生文件的目录
    def productFile(errorInfo):
        dataFolder = os.path.join(currentPath,'data')
        if not os.path.exists(dataFolder):
            os.mkdir(dataFolder)
        # 根据时间自动生成文件名称        
        file = time.strftime('%Y%m%d-%H%M%S', time.localtime()) + '-' + ms + '-warn.txt'
        fp = os.path.join(dataFolder,file)
        #print('NewFile ' + fp)
        with codecs.open(fp,"w+",'utf-8') as f:
            currentTime = time.strftime('%Y%m%d %H:%M:%S', time.localtime())
            contents = currentTime +' ' + info  + '\n'
            f.write(contents)
            # 逐一将错误信息存在需要发送的文档上
            for each in errorInfo:
                f.write(each)
        return fp

    # 执行Socket 传输文件
    def mainFunc(Info):
        try:
            logwrite(ms + " has error.") # 记录一下日志报错了。
            fp = productFile(Info) # 产生文件
            socket_client(fp) # 发送文件到指定的电脑
            print('已将报错信息发送到迷你主机。')
        except Exception as reason:
            errorlogwrite(reason)
    
    # 解析文件错误内容
    def parseText(textLine, errorWords):
        errortext = []
        for text in textLine:
            text = text.strip()
            error1 = bool(errorWords in str(text))
            if error1 :
                if msType == 'timsTOF':
                    contents = str(text).split(ErrorPattern)[1]
                if msType == 'SCIEX':
                    etext = str(text).split(ErrorPattern)[1].strip() # ERROR的原因
                    if etext in Exclude_Info or etext in errortext:
                        continue
                    t = re.search(r"(\d{2}-\d{2}-\d{4}\s\d{1,2}:\d{1,2}:\d{1,2})",str(text)).groups()[0]
                    contents = t + '\t' + etext + "\n" # ERROR文本精简成时间 + 原因
                else:
                    if msType == 'E480':
                        t = text.split(']')[0].split('[Time=')[1] # 发生ERROR的时间
                    elif msType == 'Eclipse':
                        t = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2})",str(text)).groups()[0] # 发生ERROR的时间
                    etext = str(text).split(ErrorPattern)[1] # ERROR的原因
                    contents = t + '\t' + etext + "\n" # ERROR文本精简成时间 + 原因
                errortext.append(contents) 
        return errortext
    
    # 监控Thermo报错目录下的文件
    def monitorFile2(recordT,recordfLNumber):
        global recordfileSize,filePath
        #print(str(recordT) + '\t' + str(recordfLNumber) + '\t' + str(filePath) + '\t' + str(recordfileSize))
        try:
            # 记录当前文件的修改时间
            print('正在监测文件是否发生改变……' + str(filePath))
            currentChangeTime = os.path.getmtime(filePath)
            # 1、监控指定目录下的MS-log
            # 间断性获取该文件的修改时间，直到文件发生改变就停止
            # 目录的文件数是否改变，如果改变了，重新获取MS-log的路径（有可能此时已经形成一个新的MS-log)
            if len(os.listdir(MSlogDir)) != recordfLNumber:
                NewfilePath = newFiles(MSlogDir,logPattern)
                recordfLNumber = len(os.listdir(MSlogDir)) # MSlogDir文件数
                GetError(filePath,NewfilePath,recordfileSize)
                recordT = os.path.getmtime(NewfilePath)
                filePath = NewfilePath
                recordfileSize = os.path.getsize(NewfilePath)
            elif recordT == currentChangeTime:
                time.sleep(timeInterval)
            else:
                GetError(filePath,filePath,recordfileSize)
                recordT = os.path.getmtime(filePath)
                recordfileSize = os.path.getsize(filePath)
            #print(recordT)
            #print('函数执行完毕，下一轮监控开始啦！！！')
        except Exception as reason:
            errorlogwrite(reason)
        return(recordT,recordfLNumber)

    # Thermo报错目录提取最新报错文件
    def newFiles(MSlogDir,logPattern):
        fileList = os.listdir(MSlogDir) # 该目录下的文件列表
        fileList = [f for f in fileList if bool(re.search(logPattern,f))] # 文件以MS-log开头
        if len(fileList) > 0:
            fileList = [os.path.join(MSlogDir, f) for f in fileList] #绝对路径
            fileList.sort(key=lambda fn:os.path.getmtime(fn))  #按时间排序
            fp = fileList[-1] #最新的文件
        else:
            File = open(os.path.join(MSlogDir,'Initial_File.txt'),'w')
            File.write('Nothing : Prevention program error')
            File.close()
            fp = os.path.join(MSlogDir,'Initial_File.txt')
        return fp
    
    # 监控指定的文件，一旦文件发生变化，将执行上面的操作，之后继续监控文件，一直如此循环
    if msType in ['timsTOF','SCIEX']:
        recordCT = os.path.getmtime(filePath)
        recordfileSize = os.path.getsize(filePath)
        #print('Initial ' + str(recordfileSize))
        while True:
            NewCT = monitorFile(recordCT,filePath,recordfileSize)
            time.sleep(timeInterval)
            recordCT = NewCT
            
    # 如果是480、7600、eclipse仪器的话：
    elif msType in ['E480','Eclipse']:
        # 监控目录下的某一类文件，一旦文件发生变化，将执行上面的操作，之后继续监控文件，一直如此循环
        MSlogDir = filePath
        filePath = newFiles(filePath,logPattern)
        recordCT = os.path.getmtime(filePath)
        recordfLNumber = len(os.listdir(MSlogDir))
        recordfileSize = os.path.getsize(filePath)
        while True:
            #print(str(recordCT) + '\t' + str(recordfLNumber) + '\t' + str(filePath))
            NewCT,NewNum = monitorFile2(recordCT,recordfLNumber)
            time.sleep(timeInterval)
            recordCT = NewCT
            recordfLNumber = NewNum
        
