# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 17:03:16 2023

@author: Administrator

这个脚本可以用于没有界面的情况下使用。

两种模式: （1)使用微信发送信息； （2）使用邮箱发送微信。
231107： 这个版本将接收文件的也添加进来了。用了一个线程来导入，可查看run()。
        为了保证两个线程之间可以交流，分别添加了newfiles这个变量来连接两个线程。
        模式变成了：程序运行时，先检查是否有新的newfiles，随后呢，newfiles有的话，就发送。
        也是利用newfiles来进行触发，在指定的时间内可以发送文件过来。

240502： itchat已被封禁，将微信发送端改成使用wxauto库来进行。引用WechatChannel_20250205.py。并修改sendMSG函数。
"""
import sys
import schedule
import sqlite3
import time
import os
import datetime
import pandas as pd
import yaml

import io
import json
import threading
import requests
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


from common.log import logger

from WechatChannel import WechatChannel #微信登录和发送消息的
from dbOperate import dbOperate #用于记录和存储数据库的
from receiveFileServer import ReceiveFile #用于接受文件的

# =============================================================================
# # 获取当前文件所在目录的绝对路径，用于定位配置文件conf.yaml
# =============================================================================
def get_current_path():
    """自动获取当前执行路径（兼容开发模式和打包成exe模式）"""
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable) # 打包后：exe所在目录
    else:
        base_path = os.path.dirname(os.path.abspath(__file__)) # 开发模式：脚本所在目录
    return os.path.realpath(base_path) # 规范化路径（解决可能的符号链接/快捷方式问题）
currentPath = get_current_path()
# =============================================================================
# 函数：文件文本操作函数
# =============================================================================
def get_yaml_data(yaml_file):
    '''读取配置文件的信息'''
    file = open(yaml_file, 'r', encoding="utf-8")
    file_data = file.read()
    file.close()
    data = yaml.load(file_data, Loader=yaml.FullLoader)
    return data


def readLocalFiles(root_dir):
    '''
    函数：遍历本地文件，形成list
    参数： path: 指定文件夹的路径
    结果： 返回关于该文件夹下的所有文件的绝对路径的list
    代码来源：https://blog.csdn.net/in_don/article/details/82558356

    '''
    file_list = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            file_path = os.path.join(root, file)
            # file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            # file_name = file
            # file_list.append((file_path, file_time, file_name))
            file_list.append(file_path)
    return file_list


def readtxtData(fPath, soft='maxquant', filter1=True, filterCol=[]):
    '''
    读取报告文件内容，并形成相应的可发送的文本
    '''
    strings = "分析软件是： " + soft + '\n'
    data = pd.read_csv(fPath, sep='\t')
    if filter1:
        if len(filterCol) > 0:
            data = data.loc[:, filterCol]
    # for col in data.columns:
    #     strings = strings + col + ":   " + str(data[col][0]) + "\n"
    # # 判断文件列表中是否还包括Outlier信息--------------
    # # 如果有，将outlier信息编辑进发送文本中。
    # 获取outlier表格在第几行
    search_text = '#outlier#'
    startline = 0
    with open(fPath, 'r', encoding='utf-8') as file:
        for line_number, line in enumerate(file, 1):
            if search_text in line:
                startline = line_number
                # print(f"标志字符'{search_text}'在第{line_number}行")
                break

    # 如果存在outlier，就表示有这个表格
    if startline > 0:
        outlierData = pd.read_csv(fPath, skiprows=startline, sep='\t')  # 跳过前几行
        # print(outlierData) # 打印读取的数据
        for col in data.columns:
            # 获取列对应的judge_Decide信息
            try:
                # col = 'Number of Peptides'
                judge = str(outlierData.loc[outlierData['Lable'] == col, 'Judge_Decide'].tolist()[0])
                judge = "#" + judge
            except:
                judge = ''
            # 合并字符串
            # strings = f"{0}{1}:  {2}  {3}\n".format(strings,col,str(data[col][0]),judge)
            strings = strings + col + ":   " + str(data[col][0]) + "  " + judge + "\n"
    else:
        for col in data.columns:
            strings = strings + col + ":   " + str(data[col][0]) + "\n"

    strings = strings + '-------------------------' + '\n'

    # 添加warning信息。
    for Info in open(fPath, encoding='utf-8'):
        if Info.startswith('WARNING:'):
            Info = Info.strip()
            strings = strings + str(Info) + '\n'
    # strings = "Something was wrong, please contact Xiaowei to fix it."
    return strings


# # 测试
# folder = r'D:\test\wechatMessage\data\Summary\2022-07-16_QC_Report'
# file = r'20220715_213055_P0003_TOF4_20220626_DIA_RE5_187_300ng_150min_RE5_1_1088_Stat_Summary.txt'
# fPath =  os.path.join(folder, file)
# fPath = r'D:/Desktop/示例.txt'
# cfg = get_yaml_data(r"D:/test/wechatMessage2/conf/conf.yaml")
# AA = readtxtData(fPath, soft='maxQuant', filter1=True, filterCol=cfg['maxquantFilter'])
# fPath = r'D:\test\wechatMessage\data\pd\2022-08-16_QC_Report\E4804_E480_4_220815-Nano_DDA_293T_QCtest_200ng_120MIN_R1_Stat_Summary.txt'
# data = pd.read_csv(fPath, sep='\t')
# filterCol = ['RawFile', 'Protein_Num', 'Peptide_Num', 'PSM_Num', 'MSMS_Num',
#         'No_Missed_Cleavage (%)', 'Exp_Name', 'Percent75 of RT Length (s)',
#         'Median of RT Length (s)', 'Percent25 of RT Length (s)', 'PPM_75%',
#         'PPM_50%', 'PPM_25%']

# fPath = r'D:\test\wechatMessage\data\maxquant\Summary\QC_Record_20220816\TOF_1_20220811_293T_200ng_120min_column0809_QC_RF7_1_1010_Data_Summary.txt'
# data =  pd.read_csv(fPath, sep='\t')
# data.columns

def readWarnTxt(fPath):
    '''
    读取warn文件内容，并形成相应的可发送的文本
    '''
    with open(fPath, 'r', encoding='utf-8') as file:
        strings = file.read()
    return strings

class sendInfoProgram:
    def __init__(self):
        self.running = False #该参数用于暂停和运行整个程序的
        self.loginWeChat1 = False # 用于检查一下是否有没有登录微信
        self.refreshCFG()
        self.checkDB()
        self.receiver = ReceiveFile(self.specDir, self.port)#接收文件的类
        # # 检查有没有登录微信
        # if self.sendBywechat:
        #     self.loginWechat()
        pass

    def refreshCFG(self):
        '''获取参数'''
        # 加载配置文件
        cfg = get_yaml_data(os.path.join(currentPath, r"conf\conf.yaml"))
        # print('已加载参数')
        # 时间-----------------------------------------
        # 监控文件夹的间隔时间，单位：分钟
        # self.Intervals = cfg['Intervals']
        # 每天开始发送消息的时间
        self.startTime = cfg['startTime']
        # 每天结束发送消息的时间
        self.endTime = cfg['endTime']

        # 数据库----------------------------------------
        # 创建数据库来保存数据，如果数据库已经存在，不会再创建的
        self.dbName = cfg['database']
        self.dbPath = cfg['databasePath']  # 数据库存放目录
        if not os.path.isabs(self.dbPath):
            self.dbPath = os.path.join(currentPath, self.dbPath)
        self.dbFile = os.path.join(self.dbPath, self.dbName)  # 数据库路径

        # 工程师管理质谱仪列表-----------------------------
        self.msCharge = cfg['msCharge']  # 220824后开始启用

        # specDir： 指定目录（所有搜库结果的存放位置）---------
        self.specDir = cfg['specDir']

        # 文件的后缀名------------------------------------
        # 不同软件生成的报告，后缀名可能不一样，需要进行筛选相应的文件
        # # 根据后缀名来区分不同软件生成的报告
        self.MQfileSuffix = cfg['MQfileSuffix']
        self.PDfileSuffix = cfg['PDfileSuffix']
        self.SPfileSuffix = cfg['SPfileSuffix']
        self.warnFileSuffix = cfg['warnFileSuffix']

        # # 需要从文件中提取的列的内容-----------------------
        # 筛选的内容是哪些, False和True表示是否需要筛选。如果mazquantFilter、PDFileter、spectronautFilter是空的，表示要发送全部
        # filter1  是否需要对列进行筛选,表示是否要进行筛选，True表示需要筛选
        self.maxquant = cfg['maxquant']
        self.PD = cfg['PD']
        self.spectronaut = cfg['spectronaut']

        # filterCol: list,说明需要筛选的是哪些列
        self.maxquantFilter = cfg['maxquantFilter']
        self.PDFilter = cfg['PDFilter']
        self.spectronautFilter = cfg['spectronautFilter']

        # allCol: 搜库结果中包含哪些列，仅在UI界面选择中才有意义
        self.maxquantAll = cfg['maxquantAll']
        self.PDAll = cfg['PDAll']
        self.spectronautAll = cfg['spectronautAll']

        # 质谱仪名称的格式，用于从文件名中获取到相应的质谱仪名称，从而知道是谁负责的-----------
        # 每台质谱数据名称的格式：比如TOF1有三种写法：TOF1、TOF-1、TOF_1
        self.msPatterns = cfg['msPatterns']  # 质谱仪在样品名称上模式

        # 管理员----------------------------------------
        # 设置管理员，以便出现问题了，会将信息发送给管理员
        self.admin = cfg['admin']  # 该软件的管理员

        # 工程师的邮箱-----------------------------------
        # enginnersEmails - 用于发邮件的
        self.enginnersEmails = cfg['enginnersEmails']

        # 发送者邮箱信息----------------------------------
        # 发送邮件时需要的。
        self.sender_email = cfg['sender_email']  # 发件人邮箱
        self.sender_password = cfg['sender_password']  # 发件人邮箱密码或授权码
        self.smtserver = cfg['smtserver']  # SMTP服务器和端口
        self.smtserverPort = cfg['smtserverPort']

        # 是否用邮箱发送、是否用微信发送 -------------------
        self.sendBywechat = cfg['sendBywechat']
        self.sendByemail = cfg['sendByemail']
        # # 检查一下有没有登录微信
        # if self.sendBywechat:
        #     if not self.loginWeChat1:
        #         self.loginWechat()  # 登录一下微信，如果没有登录
        
        # 接受文件的端口号
        self.port = cfg['port']

    def CFGtoSave(self):
        cfg = {}
        # 时间-----------------------------------------
        # 监控文件夹的间隔时间，单位：分钟
        # cfg['Intervals'] = self.Intervals
        
        # 每天开始发送消息的时间
        cfg['startTime'] = self.startTime
        # 每天结束发送消息的时间
        cfg['endTime'] = self.endTime

        # 数据库----------------------------------------
        # 创建数据库来保存数据，如果数据库已经存在，不会再创建的
        cfg['database'] = self.dbName
        cfg['databasePath'] = self.dbPath   # 数据库存放目录

        # 工程师管理质谱仪列表-----------------------------
        cfg['msCharge'] = self.msCharge   # 220824后开始启用

        # specDir： 指定目录（所有搜库结果的存放位置）---------
        cfg['specDir'] = self.specDir

        # 文件的后缀名------------------------------------
        # 不同软件生成的报告，后缀名可能不一样，需要进行筛选相应的文件
        # # 根据后缀名来区分不同软件生成的报告
        cfg['MQfileSuffix'] = self.MQfileSuffix
        cfg['PDfileSuffix'] = self.PDfileSuffix
        cfg['SPfileSuffix'] = self.SPfileSuffix
        cfg['warnFileSuffix'] = self.warnFileSuffix

        # # 需要从文件中提取的列的内容-----------------------
        # 筛选的内容是哪些, False和True表示是否需要筛选。如果mazquantFilter、PDFileter、spectronautFilter是空的，表示要发送全部
        # filter1  是否需要对列进行筛选,表示是否要进行筛选，True表示需要筛选
        cfg['maxquant'] = self.maxquant
        cfg['PD'] = self.PD
        cfg['spectronaut'] = self.spectronaut

        # filterCol: list,说明需要筛选的是哪些列
        cfg['maxquantFilter'] = self.maxquantFilter
        cfg['PDFilter'] = self.PDFilter
        cfg['spectronautFilter'] = self.spectronautFilter

        # allCol: 搜库结果中包含哪些列，仅在UI界面选择中才有意义
        cfg['maxquantAll'] = self.maxquantAll
        cfg['PDAll'] = self.PDAll
        cfg['spectronautAll'] = self.spectronautAll

        # 质谱仪名称的格式，用于从文件名中获取到相应的质谱仪名称，从而知道是谁负责的-----------
        # 每台质谱数据名称的格式：比如TOF1有三种写法：TOF1、TOF-1、TOF_1
        cfg['msPatterns'] = self.msPatterns  # 质谱仪在样品名称上模式

        # 管理员----------------------------------------
        # 设置管理员，以便出现问题了，会将信息发送给管理员
        cfg['admin'] = self.admin   # 该软件的管理员

        # 工程师的邮箱-----------------------------------
        # enginnersEmails - 用于发邮件的
        cfg['enginnersEmails'] = self.enginnersEmails

        # 发送者邮箱信息----------------------------------
        # 发送邮件时需要的。
        cfg['sender_email']  = self.sender_email  # 发件人邮箱
        cfg['sender_password'] = self.sender_password # 发件人邮箱密码或授权码
        cfg['smtserver'] = self.smtserver   # SMTP服务器和端口
        cfg['smtserverPort'] = self.smtserverPort

        # 是否用邮箱发送、是否用微信发送 -------------------
        cfg['sendBywechat'] = self.sendBywechat
        cfg['sendByemail'] = self.sendByemail
        
        # 接受文件的端口号-----------------
        cfg['port'] = self.port
        
        # 保存文件------------
        output_file = os.path.join(currentPath, r"conf\conf.yaml")
        with open(output_file, 'w', encoding='utf-8') as yaml_file:
            yaml.dump(cfg, yaml_file, allow_unicode=True)
        print(f'Saved arguments to {output_file}')
        
        


    def checkDB(self):
        '''检查数据库和表格是否存在，如果不存在，就相应的创建数据库和表格'''
        self.dbase = dbOperate(self.dbFile)  # 创建数据库
        # 创建OLDFILES
        self.dbase.create_table(table_name='OLDFILES',
                           columns=['PATH TEXT', 'TIME DATETIME', 'NAME TEXT'])  # 创建表格
        # 创建SENTFILES
        self.dbase.create_table(table_name='SENTFILES',
                           columns=['PATH TEXT', 'TIME DATETIME', 'NAME TEXT', 'RECEIVER'])  # 创建表格
        self.dbase.close()

    def loginWechat(self):
        if not self.loginWeChat1:
            self.wcCl = WechatChannel()
            self.loginWeChat1 =self.wcCl.startup()  # 登录微信

    def towho(self, filePath):
        '''
        根据文件名确定是哪个工程师负责的仪器
        '''
        # 文件名称
        fn = os.path.basename(filePath)
        # 根据文件名筛选出是哪台质谱
        import re
        for ms in self.msPatterns.keys():
            result = bool(re.search(self.msPatterns[ms], fn))
            if result:
                # charge = list(msCharge['charge'][msCharge['ms'] == ms]) 20220824之后就弃用
                charge = self.msCharge[ms]  # 20220824之后就启用

                # 对charge进行筛选，看是否有人需要进行指定某些文件才给他发送，比如只要QC结果的
                # 20221116增加的
                charge1 = []
                for each in charge:
                    if isinstance(each, dict):
                        boolWho = bool(re.search(list(each.values())[0], fn))
                        if boolWho:
                            charge1.append(list(each.keys())[0])
                    else:
                        charge1.append(each)

                # 结束for循环
                break
            else:
                charge1 = self.admin

        # 返回结果:
        return list(set(charge1))  # 去重，返回一个list，可能有多个人，比如['admin', 'xiaowei']

    # 测试
    # filePath = r"20220715_213055_P0002_TOF5_20220626_DIA_RE5_187_300ng_150min_RE5_1_1088_Stat_Summary.txt"
    # towho(filePath)
    # filePath = r"D:\test\MSWarning\data\20220826-095518-TOF5-warn.txt"
    # towho(filePath)

    def send_email(self, receiver_email, subject, body, attachment=None):
        '''
        发送邮件,发送成功则为True，否则为False

        # 测试
        receiver_email = "h15016211223@163.com"  # 收件人邮箱
        subject = "测试邮件"  # 邮件主题
        body = "这是一封测试邮件，用于测试发送邮件功能。"  # 邮件正文
        attachment = "file.txt"  # 附件文件路径，如果不需要附件则设置为None
        attachment = None
        send_email(receiver_email, subject, body, attachment)
        '''
        try:
            # 邮件内容设置
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = receiver_email
            msg['Subject'] = subject

            # 添加邮件正文
            msg.attach(MIMEText(body, 'plain'))

            # 添加附件（可选）
            if attachment:
                with open(attachment, "rb") as f:
                    part = MIMEApplication(f.read(), Name=attachment)
                part['Content-Disposition'] = f'attachment filename="{attachment}"'
                msg.attach(part)

            # 发送邮件
            server = smtplib.SMTP(self.smtserver, self.smtserverPort)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, receiver_email, msg.as_string())
            server.quit()
            print("Email sent successfully")
            return True
        except Exception as e:
            print("Email sent failed: ",  str(e))
            return False

    def sentMSG(self, f, soft=None, filter1=None, filterCol=None, wholetext=False, sendBywechat=True,
                sendByemail=False):
        '''
        编辑发送报告文本，确定发送给谁，然后发送消息，写入日志和数据库
        搜库结果经过筛选，warn信息不需要筛选，读取全文
        发送搜库结果：所有的参数均需要
        发送warn信息：仅需要dbFiles
        '''
        try:
            # （1）利用函数，对新增文件逐一进行发送微信信息给相应的负责人
            if wholetext:
                strings = readWarnTxt(f)  # a. 发送warn文档
            else:
                strings = readtxtData(f, soft=soft, filter1=filter1, filterCol=filterCol)  # a. 发送文本

            whos = self.towho(f)  # b. 发给谁,也可能会是多个人 whos是一个list
            for who in whos:
                if self.sendBywechat:
                    if not self.loginWeChat1:
                        self.loginWechat() #登录一下微信，如果没有登录
                    re = self.wcCl.sendMSG(strings=strings,who=who) # c. 发送消息（还需要一个，如果发送不成功，怎么办）
                    sendStatus = re == "done"
                if self.sendByemail:
                    sendStatus = self.send_email(receiver_email=self.enginnersEmails[who], subject=f"搜库结果-{os.path.basename(f)}",
                                            body=strings, attachment=f)
                # 记录发送情况
                if sendStatus:
                    logger.info(f"send to {who} with {f}")
                    logging.info(f"send to {who} with {os.path.basename(f)} \n")
                    fdata = (f,  # 路径
                             datetime.datetime.now(),  # 发送时间
                             os.path.basename(f),  # name
                             who
                             )
                    self.dbase.insertData(table_name='SENTFILES', data=fdata)
                else:
                    logger.error(f"{os.path.basename(f)} didn't send!!!\n")
            #  (2) 将oldFiles写入到某个文件中，或将已发送信息的文件续写入到某个文件中
            if re == "done":
                fdata = (f,  # 路径
                         datetime.datetime.fromtimestamp(os.path.getmtime(f)),  # 修改时间
                         os.path.basename(f)  # name
                         )
                self.dbase.insertData(table_name='OLDFILES', data=fdata)

        except Exception as reason:
            print(f)
            print("This file didn't send, please check !")
            print(reason)
       
    def mainfunjob(self):
        '''仅发送文件而已'''
        try:
            # 0、连接数据库
            self.dbase.connect()
            # # 登录一下微信，如果没有登录
            if self.sendBywechat:
                if not self.loginWeChat1:
                    self.loginWechat()

            # 4、如果有新增的文件就执行
            if len(self.newfiles) > 0:
                for f in self.newfiles:
                    #  (2)筛选文件，根据文件名后缀筛选出是什么分析软件，从而确定需要获取哪些信息
                    if f.endswith(self.MQfileSuffix):
                        soft = 'maxquant'
                        filter1 = self.maxquant
                        filterCol = self.maxquantFilter
                        self.sentMSG(f, soft, filter1, filterCol)
                    elif f.endswith(self.PDfileSuffix):
                        soft = 'PD'
                        filter1 = self.PD
                        filterCol = self.PDFilter
                        self.sentMSG(f, soft, filter1, filterCol)
                    elif f.endswith(self.SPfileSuffix):
                        soft = 'spectronaut'
                        filter1 = self.spectronaut
                        filterCol = self.spectronautFilter
                        self.sentMSG(f, soft, filter1, filterCol)
                    elif f.endswith(self.warnFileSuffix):
                        self.sentMSG(f=f, wholetext=True)
                    # 对于后缀不匹配的，暂且放过吧。
                    else:
                        fdata = (f,  # 路径
                                 datetime.datetime.fromtimestamp(os.path.getmtime(f)),  # 修改时间
                                 os.path.basename(f)  # name
                                 )
                        self.dbase.insertData(table_name='OLDFILES', data=fdata)
                    
                    self.newfiles.remove(f) #移除掉这个文件

            # 5、本轮发送完毕。
            self.dbase.close() #关闭数据库连接
        except KeyboardInterrupt:
            logger.debug('退出了程序唉， exit.')
            logger.info('Bye~')
    
    def initNewfiles(self):
        '''刚开始启动时，需要检查一下是否有新文件（没有发送的文件）'''
        # 0、连接数据库
        self.dbase.connect()
        # # 登录一下微信，如果没有登录
        if self.sendBywechat:
            if not self.loginWeChat1:
                self.loginWechat()
        # 1、初始化定义oldFiles和oldFilesNumber
        oldFiles = self.dbase.getDbData(table_name='OLDFILES')
        # sentFiles = getDbData(dbFiles = dbFiles,table_name='SENTFILES')

        # 2、获取指定目录下的所有文件列表
        currentFiles = readLocalFiles(self.specDir)

        # 3、获取新增文件
        self.newfiles = list(set(currentFiles) - set(oldFiles))
        self.dbase.close() #关闭数据库连接
        
    def parse_time(self, time_str):
        '''给时间转格式的'''
        return datetime.datetime.strptime(time_str, '%H:%M:%S').time()
    
    def run_in_background(self):
        '''发送程序，指定时间内发送'''
        self.initNewfiles() #先自动获取一下self.newfiles
        startTime = self.parse_time(self.startTime)
        endTime = self.parse_time(self.endTime)
        
        while self.running:
            current_time = datetime.datetime.now().time()
            if startTime <= current_time <= endTime: #当前时间在指定的时间段内
                if self.receiver.newFiles:
                    # 将receiver.newFiles给了newfiles后，变成[],这样就可以防止在发送信息的时间里接收的文件可以作为新的文件来传入。
                    self.newfiles = self.newfiles + self.receiver.newFiles
                    self.receiver.newFiles = []
                    
                if self.newfiles:    
                    self.mainfunjob() # 发送文件
                else:
                    time.sleep(2)
            else:
                time.sleep(2) #暂停2s。#主要针对非需要运行的时间段
                # print('stop 2s, 非运行阶段')
                
    def stop(self):
        '''暂停run()运行'''
        self.running = False
        self.receiver.running = False # 用于控制接收文件的线程可以关闭
        # 首先检查run_thread是否存在，如果存在则使用join方法等待线程结束，并将run_thread设置为None。
        # 这样可以确保在停止后台运行时，线程能够正常地结束
        if self.run_thread:
            self.run_thread.join()  # 这里可以选择是否等待线程结束
            # self.run_thread.terminate() # 终止线程（不建议）
            self.run_thread = None
        
        self.receiver.stop()

        print("Stoped!")
    
    def run(self):
        '''运行程序'''
        if self.running:
            return

        # 使用线程运行 run_in_background 方法
        self.running = True
        self.run_thread = threading.Thread(target=self.run_in_background)
        self.run_thread.start()
        
        # 接收文件的线程
        self.receiver.running = True
        self.run_thread_receiver = threading.Thread(target=self.receiver.run)
        self.run_thread_receiver.start()

# # =============================================================================
# # test
# # =============================================================================
# if __name__ == "__main__":
#     sendInfoP = sendInfoProgram()
#     sendInfoP.refreshCFG()
#     sendInfoP.run()
#     time.sleep(60)
#     sendInfoP.stop()

