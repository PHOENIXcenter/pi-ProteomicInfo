from PyQt5.QtWidgets import *
from socket import *
import re

# 校正信息比对
def CheckStatus(Window,Class):
    if Class == 'Server':
        if str(Window.checkBox.isChecked()) == 'True':
            try :
                TestPort = Window.Input_Port.text()
                sock = socket()
                #print(TestPort)
                sock.connect(('localhost',int(TestPort)))
                msg_box = QMessageBox(QMessageBox.Warning,'Error','Port：' + TestPort + ' is Using')
                msg_box.exec_()
            except :
                print(str(TestPort) + 'OK')
                Window.RunServer.setEnabled(True)
            else:
                sock.close()
        else:
            Window.RunServer.setEnabled(False)

# 文件夹选择
def ChoosePath(Window,Info_Acq):
    Exist_Dir = QFileDialog.getExistingDirectory().replace('/','\\')
    if ' ' in str(Exist_Dir):
        msg_box = QMessageBox(QMessageBox.Warning,'Error','Please remove spaces in path')
        msg_box.exec_()
    else:
        if Info_Acq == 'Received':
            Window.Show_Received.setText(str(Exist_Dir))
        if Info_Acq == 'Output':
            Window.OutputDir.setText(str(Exist_Dir))

# 文件选择
def ChooseParam(Window,Info_Param):
    Param_File,Type = QFileDialog.getOpenFileName()
    Param_File = Param_File.replace('/','\\')
    if ' ' in str(Param_File):
        msg_box = QMessageBox(QMessageBox.Warning,'Error','Please remove spaces in path')
        msg_box.exec_()
    else:
        if Info_Param == 'Exe':
            Window.Show_Exe.setText(str(Param_File))
        if Info_Param == 'Fasta':
            Window.Show_Fasta.setText(str(Param_File))
        if Info_Param == 'WorkFlow':
            Window.Show_WorkFlow.setText(str(Param_File))
        if Info_Param == 'Library':
            Window.Show_Library.setText(str(Param_File))
        if Info_Param == 'MQ_Param':
            Mqpar = open(Param_File,'r',encoding = 'utf-8')
            Mqpar_Text = Mqpar.read()
            Mqpar.close()
            Exp_Name_Rule = '   <experiments>\n      <string>.*.</string>\n   </experiments>\n'
            Exp_Name = re.search(Exp_Name_Rule,Mqpar_Text)
            Exp_Name = Exp_Name[0].split('<string>')[1].split('</string>')[0]
            RawFile_Rule = '   <filePaths>\n      <string>.*.</string>\n   </filePaths>\n'
            RawFile = re.search(RawFile_Rule,Mqpar_Text)
            RawFile = RawFile[0].split('<string>')[1].split('</string>')[0]
            del Mqpar_Text
            Window.Show_Param.setText(str(Param_File))
            Window.Show_RawFile.setText(str(RawFile))
            Window.Show_Experiment.setText(str(Exp_Name))
        if Info_Param == 'PD_Param':
            PDpar = open(Param_File,'r',encoding = 'utf-8')
            PDpar_Text = PDpar.read()
            PDpar.close()
            UserName_Rule = '  <UserName>.*.</UserName>\n'
            UserName = re.search(UserName_Rule,PDpar_Text)
            UserName = UserName[0].split('<UserName>')[1].split('</UserName>')[0]
            HostName_Rule = '  <HostName>.*.</HostName>\n'
            HostName = re.search(HostName_Rule,PDpar_Text)
            HostName = HostName[0].split('<HostName>')[1].split('</HostName>')[0]
            del PDpar_Text
            Window.Show_Param.setText(str(Param_File))
            Window.Show_UserName.setText(str(UserName))
            Window.Show_HostName.setText(str(HostName))
