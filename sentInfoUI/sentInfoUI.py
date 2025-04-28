# -*- coding: utf-8 -*-
"""
Created on Mon Jul 31 14:45:30 2023

@author: Administrator
用于配套的，实现界面化，主要是将参数可用通过界面来进行设置，另外支持调用另一个程序来进行。挺有意思的，有空的话，复盘一下是怎么做到的。

230809: 实现UI的基本功能
230824：修改run_other_script()函数，添加encoding=’utf-8',保障运行其它程序时不会因为编码问题而出错。
230825: run_other_script()函数，重新修改了。将微信发送程序转成了class，利用class来推动程序的启动和关闭。
        并将UI的参数都可以互转到self.sendInfoP。
230829: （1）新增get_enginnerTableInfo(),主要是在enginner table中，数据容易报错，所以重新定义了。（如添加信息不完全，导致信息获取出问题）
        （2）添加错误提示功能。
        （3）修改get_table_widget_values()， 如果单元格是''，将不获取这个值。
230912: 添加 `self.sendInfoP.wcCl.friendsList()` 因为在添加工程师后，再运行程序，如果是刚刚添加工程师微信的话，会发现没有这个人，无法发送消息。
        在WechatChannel中新建一个函数：friendsList() 用于获取微信好友列表

231107: 大改。 将传玺的接收文件的程序也放进来了，单独用Server_231107.py来实现运行程序的。
        对于sentInfoUI中，主要是删掉了间隔时间的这个参数，并添加了port这个参数。
        在sendInfoProgram231107中，修改了更多。

250306： (1)itchat已被封禁，将微信发送端改成使用wxauto库来进行。
        (2) 给QPlainTextEditLogger添加一个flush方法，以兼容某些日志处理逻辑
        （3）需删除获取好友列表这个功能（230912添加的功能），当前wxauto库不支持

250423： (1) 将界面改成英文。
"""

# 其它文档需要的---------------------------------------------
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

# from common.expired_dict import ExpiredDict
from common.log import logger
# from lib import itchat
# from lib.itchat.content import *
# 本文档需要的--------------------------------------------------
import sys
import yaml
import os
import subprocess
import signal
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QTableWidget, QTableWidgetItem, QWidget, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtCore import QTime
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QTextCharFormat, QColor

from sendInfoProgram import sendInfoProgram, get_yaml_data

# 微信wxauto库的初始化
import comtypes # # 在 WeChat 对象的初始化之前，添加对 COM 库的初始化
import pythoncom
import win32com.client
import wxauto
import win32gui
import win32con
import win32api
import traceback  

# =============================================================================
# # 获取当前文件所在目录的绝对路径
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
# 读取参数配置
# =============================================================================
# cfg = get_yaml_data(os.path.join(currentPath, r"conf\conf.yaml"))  # 获取参数


class QPlainTextEditLogger(QObject):
    '''为print信息输出到UI上做准备的'''
    append_signal = pyqtSignal(str)

    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def write(self, text):
        self.append_signal.emit(text)

    def __del__(self):
        self.text_widget = None
    
    def flush(self):
        """提供 flush 方法，以兼容某些日志处理逻辑"""
        # 来解决'QPlainTextEditLogger' object has no attribute 'flush'
        pass  


class LogEmitter(logging.Handler, QObject):
    '''为logging Info信息输出到UI上做准备的'''
    append_info_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        QObject.__init__(self)

    def emit(self, record):
        msg = self.format(record)
        self.append_info_signal.emit(msg)

class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        loadUi('ui/sentInfo_231107-xw.ui', self)
        # self.setWindowTitle('SendInfo') #修改标题
        self.sendInfoP = sendInfoProgram()  # 关于发送消息的程序
        self.initUI()
        self.print2UI()


    def initUI(self):
        '''页面初始化'''
        self.configureToUI()
        self.buttonEvent()
        pass

    def configureToUI(self):
        '''将参数输出到UI界面上'''
        # # 获取参数
        # cfg = get_yaml_data(os.path.join(currentPath, r"conf\conf.yaml"))
        # 是否发送微信或邮件
        self.checkBox_sendBywechat.setChecked(self.sendInfoP.sendBywechat)  # 是否发送微信
        self.checkBox_sendByemail.setChecked(self.sendInfoP.sendByemail)  # 是否发送邮件
        # 每天发送的起始时间和结束时间
        self.start_timeEdit.setTime(QTime.fromString(self.sendInfoP.startTime, 'h:mm:ss'))  # 发送起始时间
        self.end_timeEdit.setTime(QTime.fromString(self.sendInfoP.endTime, 'h:mm:ss'))  # 发送结束时间
        self.port_lineEdit.setText(str(self.sendInfoP.port)) #端口号
        # 所有报告的存放位置
        self.specDir_lineEdit.setText(self.sendInfoP.specDir)  # 所有报告的存放位置
        # 文件后缀名称
        self.maxquant_fileSuffix_lineEdit.setText(self.sendInfoP.MQfileSuffix)  # MQ文件后缀
        self.PD_fileSuffix_lineEdit.setText(self.sendInfoP.PDfileSuffix)  # PD文件后缀
        self.SP_fileSuffix_lineEdit.setText(self.sendInfoP.SPfileSuffix)  # SP文件后缀
        self.warn_fileSuffix_lineEdit.setText(self.sendInfoP.warnFileSuffix)  # warn文件后缀
        # 发送邮件需要的信息
        self.senter_email_lineEdit.setText(self.sendInfoP.sender_email)  # 发件人邮箱
        self.senter_password_lineEdit.setText(self.sendInfoP.sender_password)  # 发件人邮箱密码或授权码
        self.emailServer_lineEdit.setText(self.sendInfoP.smtserver)  # SMTP服务器和端口
        self.emailServer_Port_lineEdit.setText(str(self.sendInfoP.smtserverPort))
        # 管理员
        self.admin_lineEdit.setText(self.sendInfoP.admin[0]) #管理员

        # 写入数据到MStableWidget中
        self.write_table_widget_data(self.MStableWidget,
                                     [[key, value] for key, value in self.sendInfoP.msPatterns.items()])
        # DONE 待修改 写入数据到enginnertableWidget中
        self.write_table_data_toenginnertableWidget()  # 写入数据到enginnertableWidget
        # 写入数据到软件的表格中
        self.write_table_widget_data(self.MQ_tableWidget1,
                                     [[value] for value in list(set(self.sendInfoP.maxquantAll) - set(self.sendInfoP.maxquantFilter))])
        self.write_table_widget_data(self.PD_tableWidget1,
                                     [[value] for value in list(set(self.sendInfoP.PDAll) - set(self.sendInfoP.PDFilter))])
        self.write_table_widget_data(self.SP_tableWidget1, [[value] for value in list(
            set(self.sendInfoP.spectronautAll) - set(self.sendInfoP.spectronautFilter))])
        self.write_table_widget_data(self.MQ_tableWidget2, [[value] for value in self.sendInfoP.maxquantFilter])
        self.write_table_widget_data(self.PD_tableWidget2, [[value] for value in self.sendInfoP.PDFilter])
        self.write_table_widget_data(self.SP_tableWidget2, [[value] for value in self.sendInfoP.spectronautFilter])

        pass

    def buttonEvent(self):
        '''专门用于对按钮的进行的事件'''
        # 质谱仪---
        self.addMSBtn.clicked.connect(self.add_empty_rowtoMStableWidget)  # addMSBtn
        self.delMSBtn.clicked.connect(self.delete_selected_rowtoMStableWidget)  # delMSBtn

        # 工程师----
        self.addEnginerBtn.clicked.connect(self.add_empty_rowtoenginnertableWidget)  # addEnginerBtn
        self.delEnginerBtn.clicked.connect(self.delete_selected_rowtoenginnertableWidget)  # delEnginerBtn

        # 软件----
        # maxquant
        self.MQ_addBtn.clicked.connect(self.add_MQValue)  # MQ_addBtn
        self.MQ_delBtn.clicked.connect(self.del_MQValue)  # MQ_delBtn
        # protein discover
        self.PD_addBtn.clicked.connect(self.add_PDValue)  # PD_addBtn
        self.PD_delBtn.clicked.connect(self.del_PDValue)  # PD_delBtn
        # spectronaut
        self.SP_addBtn.clicked.connect(self.add_SPValue)  # SP_addBtn
        self.SP_delBtn.clicked.connect(self.del_SPValue)  # SP_delBtn

        # 其它----
        self.brosweSaveDirBtn.clicked.connect(self.open_directory_dialog)  # brosweSaveDirBtn

        # 保存----
        self.saveBtn.clicked.connect(self.saveConfigure)  # 测试

        # 运行
        self.is_running = False
        # self.runBtn.setStyleSheet("background-color: green;") # 按钮颜色修改
        self.runBtn.clicked.connect(self.runFunction)
    def runFunction(self):
        '''TODO: 写运行程序。'''
        if not self.is_running:
            self.run_other_script()
            self.runBtn.setText("停止")
            self.runBtn.setStyleSheet("background-color: red;")
            self.is_running = True
        else:
            self.stop_other_script()
            self.runBtn.setText("运行")
            self.runBtn.setStyleSheet("background-color: green;")
            self.is_running = False
        pass

    def run_other_script(self):
        '''运行其它程序'''
        try:
            self.UI2Configure() #从UI上提取
            self.sendInfoP.run()
            QMessageBox.information(self, "Sending Info", 'The program is running.')
        except Exception as e:
            error_message = f"The information is incomplete, please check if all have been filled.\n {str(e)}"
            QMessageBox.critical(self, "ERROR", error_message, QMessageBox.Ok)

    def stop_other_script(self):
        '''暂停其它程序'''
        self.sendInfoP.stop()
        QMessageBox.information(self, "Sending Info", 'The program stopped running.')

    def saveConfigure(self):
        try:
            self.UI2Configure()
            # 最后，保存cfg到yaml文件中
            self.sendInfoP.CFGtoSave()
            QMessageBox.information(self, "Sending Info", 'All parameters have been saved and can be used directly at the next login.')
        except:
            error_message = "The information is incomplete, please check if all have been filled."
            QMessageBox.critical(self, "ERROR", error_message, QMessageBox.Ok)

    def UI2Configure(self):
        '''如果参数被改动过，将参数转入到self.sendInfoP'''

        # 是否发送微信或邮件
        self.sendInfoP.sendBywechat = self.checkBox_sendBywechat.isChecked()  # 是否发送微信
        self.sendInfoP.sendByemail = self.checkBox_sendByemail.isChecked()  # 是否发送邮件
        # 每天发送的起始时间和结束时间
        self.sendInfoP.startTime = self.get_time(self.start_timeEdit)  # 发送起始时间
        self.sendInfoP.endTime = self.get_time(self.end_timeEdit)  # 发送结束时间
        self.sendInfoP.port = int(self.port_lineEdit.text()) #端口号 

        # 所有报告的存放位置
        self.sendInfoP.specDir = self.specDir_lineEdit.text()  # 所有报告的存放位置
        # 文件后缀名称
        self.sendInfoP.MQfileSuffix = self.maxquant_fileSuffix_lineEdit.text()  # MQ文件后缀
        self.sendInfoP.PDfileSuffix = self.PD_fileSuffix_lineEdit.text()  # PD文件后缀
        self.sendInfoP.SPfileSuffix = self.SP_fileSuffix_lineEdit.text()  # SP文件后缀
        self.sendInfoP.warnFileSuffix = self.warn_fileSuffix_lineEdit.text()  # warn文件后缀
        # 发送邮件需要的信息
        self.sendInfoP.sender_email = self.senter_email_lineEdit.text()  # 发件人邮箱
        self.sendInfoP.sender_password = self.senter_password_lineEdit.text()  # 发件人邮箱密码或授权码
        self.sendInfoP.smtserver = self.emailServer_lineEdit.text()  # SMTP服务器和端口
        self.sendInfoP.smtserverPort = int(self.emailServer_Port_lineEdit.text())
        # 管理员
        self.sendInfoP.admin = [self.admin_lineEdit.text()]  # 管理员
        # 获取UI界面的MStableWidget数据
        self.sendInfoP.msPatterns = {item[0]: item[1] for item in self.get_table_widget_values(self.MStableWidget)}

        # DONE： 获取enginnertableWidget的值
        self.get_enginnerTableInfo()

        # 获取软件的表格值
        def softValues(tableWidget):
            '''获取软件的表格值'''
            data_list = self.get_table_widget_values(tableWidget)
            values = [item[0] for item in data_list]
            return values

        self.sendInfoP.maxquantFilter = softValues(self.MQ_tableWidget2)  # MQ_tableWidget2
        self.sendInfoP.PDFilter = softValues(self.PD_tableWidget2)  # PD_tableWidget2
        self.sendInfoP.spectronautFilter = softValues(self.SP_tableWidget2)  # SP_tableWidget2
        self.sendInfoP.maxquantAll = softValues(self.MQ_tableWidget1) + self.sendInfoP.maxquantFilter  # MQ_tableWidget1
        self.sendInfoP.PDAll = softValues(self.PD_tableWidget1) + self.sendInfoP.PDFilter  # PD_tableWidget1
        self.sendInfoP.spectronautAll = softValues(
            self.SP_tableWidget1) + self.sendInfoP.spectronautFilter  # SP_tableWidget1


    def get_enginnerTableInfo(self):
        # 获取enginnerTable信息------
        enginnerTable = []
        rows = self.enginnertableWidget.rowCount()
        cols = self.enginnertableWidget.columnCount()

        for row in range(rows):
            row_data = []
            for col in range(cols):
                item = self.enginnertableWidget.item(row, col)
                if item:
                    cell_value = item.text()
                else:
                    cell_value = ''
                row_data.append(cell_value)
            if row_data != ['', '', '', '']:  # 如果整行为空，就不添加了。
                enginnerTable.append(row_data)

        # 转化enginnerTable信息------
        msCharge = {ms: [] for ms in self.sendInfoP.msPatterns.keys()}
        enginnersEmails = {}
        for item in enginnerTable:  # item[0] enginner,item[1] ms,item[2] project, item[3] emails
            if item[0] != '' and item[1] in self.sendInfoP.msPatterns:
                # 填充mscharge的值
                if item[2] == '':
                    msCharge[item[1]].append(item[0])
                else:
                    msCharge[item[1]].append({item[0]: item[2]})
                # 填充工程师+email的值
                if item[3] != '':
                    enginnersEmails[item[0]] = item[3]

        self.sendInfoP.msCharge = msCharge
        self.sendInfoP.enginnersEmails = enginnersEmails



    def add_empty_rowtoMStableWidget(self):
        '''给MStableWidget添加一行'''
        self.add_empty_row(self.MStableWidget)

    def delete_selected_rowtoMStableWidget(self):
        '''删除MStableWidget指定的行'''
        self.delete_selected_row(self.MStableWidget)

    # 工程师--------------------------------------------------------------------
    def write_table_data_toenginnertableWidget(self):
        '''写入数据到enginnertableWidget中'''
        # Example data to be written to the QTableWidget
        # data = [
        #     ['xq', '480-1', 'P0019', ''],
        #     ['xq', '480-2', 'ssss', 'c'],
        #     ['xq', '480-3', 'ff', 'xy']
        # ]
        data = []
        msCharge = self.sendInfoP.msCharge
        for ms in msCharge.keys():
            for each in msCharge[ms]:
                if isinstance(each, dict):
                    who = list(each.keys())[0]
                    projects = each[who]
                else:
                    who = each
                    projects = ''
                if who in self.sendInfoP.enginnersEmails.keys():
                    email = self.sendInfoP.enginnersEmails[who]
                else:
                    email = ''
                data.append([who, ms, projects, email])
        # Call the function to write data to the QTableWidget
        self.write_table_widget_data(self.enginnertableWidget, data)

    def add_empty_rowtoenginnertableWidget(self):
        '''给enginnertableWidget添加一行'''
        self.add_empty_row(self.enginnertableWidget)

    def delete_selected_rowtoenginnertableWidget(self):
        '''删除MStableWidget指定的行'''
        self.delete_selected_row(self.enginnertableWidget)

    # 软件---------------------------------------------------------------------
    def add_MQValue(self):
        self.add_softwareValue(self.MQ_tableWidget1, self.MQ_tableWidget2)
    def del_MQValue(self):
        self.delete_softwareValue(self.MQ_tableWidget1, self.MQ_tableWidget2)

    # PD
    def add_PDValue(self):
        self.add_softwareValue(self.PD_tableWidget1, self.PD_tableWidget2)
    def del_PDValue(self):
        self.delete_softwareValue(self.PD_tableWidget1, self.PD_tableWidget2)

    # SP
    def add_SPValue(self):
        self.add_softwareValue(self.SP_tableWidget1, self.SP_tableWidget2)
    def del_SPValue(self):
        self.delete_softwareValue(self.SP_tableWidget1, self.SP_tableWidget2)

    # 其它---------------------------------------------------------------------
    def open_directory_dialog(self):
        '''specDir_lineEdit，用于浏览目录来获取参数'''
        # Open the directory dialog and get the selected directory
        selected_dir = QFileDialog.getExistingDirectory(self, 'Select Directory', './')

        if selected_dir:
            # Display the selected directory path in the QLineEdit (replace line_edit_widget with your widget name)
            self.specDir_lineEdit.setText(selected_dir)

    # 基本函数------------------------------------------------------------------
    def write_table_widget_data(self, table_widget, data):
        '''往任一table weight写入数据'''
        # Set the number of rows and columns for the QTableWidget
        table_widget.setRowCount(len(data))
        table_widget.setColumnCount(len(data[0]))

        # Write data to the QTableWidget
        for row, rowData in enumerate(data):
            for col, cellData in enumerate(rowData):
                item = QTableWidgetItem(cellData)
                table_widget.setItem(row, col, item)

    def get_table_widget_values(self, tableWidget):
        values = []
        rows = tableWidget.rowCount()
        cols = tableWidget.columnCount()

        for row in range(rows):
            row_data = []
            for col in range(cols):
                item = tableWidget.item(row, col)
                if item:
                    if item.text() != '':
                        cell_value = item.text()
                        row_data.append(cell_value)
            if row_data:  # 如果整行为空，就不添加了。
                values.append(row_data)
        return values

    def add_empty_row(self, table_widget):
        '''添加一个空的行'''
        # Get the number of rows in the QTableWidget
        row_count = table_widget.rowCount()

        # Insert an empty row at the end
        table_widget.insertRow(row_count)

    def delete_selected_row(self, table_widget):
        '''删除选择的行'''
        # Get the currently selected row index
        selected_row = table_widget.currentRow()

        if selected_row >= 0:
            # Remove the selected row
            table_widget.removeRow(selected_row)

    def get_time(self, timeEdit):
        '''获取timeEdit的值'''
        # Get the selected time from the QTimeEdit
        time = timeEdit.time()
        # # Format the time as per your requirement
        formatted_time = time.toString("hh:mm:ss")  # Format: Hour:Minute AM/PM
        return formatted_time

    def add_softwareValue(self, tableWidget1, tableWidget2):
        '''软件的值右移，移入'''
        # Get the selected row index from tableWidget1
        selected_row_index = tableWidget1.currentRow()

        if selected_row_index >= 0:
            # Get the data from the selected row in tableWidget1
            selected_row_data = []
            for col in range(tableWidget1.columnCount()):
                item = tableWidget1.item(selected_row_index, col)
                if item:
                    selected_row_data.append(item.text())

            # Insert the selected row data into tableWidget2 at the end
            row_count = tableWidget2.rowCount()
            tableWidget2.insertRow(row_count)
            for col, cellData in enumerate(selected_row_data):
                item = QTableWidgetItem(cellData)
                tableWidget2.setItem(row_count, col, item)

            # Remove the selected row from tableWidget1
            tableWidget1.removeRow(selected_row_index)

    def delete_softwareValue(self, tableWidget1, tableWidget2):
        '''软件的值左移，移出'''
        # Get the selected row index from tableWidget2
        selected_row_index = tableWidget2.currentRow()

        if selected_row_index >= 0:
            # Get the data from the selected row in tableWidget2
            selected_row_data = []
            for col in range(tableWidget2.columnCount()):
                item = tableWidget2.item(selected_row_index, col)
                if item:
                    selected_row_data.append(item.text())

            # Insert the selected row data into tableWidget1 at the end
            row_count = tableWidget1.rowCount()
            tableWidget1.insertRow(row_count)
            for col, cellData in enumerate(selected_row_data):
                item = QTableWidgetItem(cellData)
                tableWidget1.setItem(row_count, col, item)

            # Remove the selected row from tableWidget2
            tableWidget2.removeRow(selected_row_index)

    # 将print和logging info 输出到UI的文本框-----------------------------------
    def print2UI(self):
        '''后台输出的信息，输出到UI上'''
        self.redirector = QPlainTextEditLogger(self.output_text_edit)
        self.redirector.append_signal.connect(self.append_text)

        self.log_emitter = LogEmitter()
        self.log_emitter.append_info_signal.connect(self.append_info_text)
        logging.basicConfig(level=logging.INFO, handlers=[self.log_emitter])
        # logging.basicConfig(level=logging.error, handlers=[self.log_emitter])

        sys.stdout = self.redirector  # 重定向 stdout 流

    def append_text(self, text):
        '''增加print的信息'''
        cursor = self.output_text_edit.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(text)
        self.output_text_edit.setTextCursor(cursor)
        self.output_text_edit.ensureCursorVisible()

    def append_info_text(self, text):
        '''增加logging Info的信息'''
        cursor = self.output_text_edit.textCursor()
        cursor.movePosition(cursor.End)
        format_ = QTextCharFormat()
        format_.setForeground(QColor("blue"))
        cursor.insertText(text, format_)
        self.output_text_edit.setTextCursor(cursor)
        self.output_text_edit.ensureCursorVisible()

    # 关闭窗口时弹窗提醒。
    def closeEvent(self, event):
        '''
        重写了 closeEvent 方法，当关闭窗口时，如果后台任务还在运行，会弹出一个询问框来确认是否关闭窗口。如果用户选择关闭，会断开与任务的连接并停止任务。
        '''
        if self.is_running:
            reply = QMessageBox.question(self, 'Confirm Close',
                                         "Background task is still running. Do you want to close the window?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                if self.is_running:
                    self.sendInfoP.stop() #关掉正在运行的程序
                if self.redirector:
                    self.redirector.deleteLater()  # 释放 QPlainTextEditLogger 对象
            else:
                event.ignore()
        else:
            event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("SendInfo")  # Set application name here
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
