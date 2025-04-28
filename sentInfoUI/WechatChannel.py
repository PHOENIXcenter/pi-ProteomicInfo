# -*- coding: utf-8 -*-
"""
此脚本用于登录微信和微信发送消息的。
"""
import time
import random
import traceback  # 用于获取详细的错误堆栈信息

"""
# 20250305：
# Windows 的 UI 自动化组件（如 UIAutomationCore.dll）要求线程运行在 单线程套间 (STA) 模式下。
# 在 Python 中，默认新线程是 多线程套间 (MTA)，需通过 pythoncom 强制指定为 STA
# 不然会出现 Can not load UIAutomationCore.dll.

"""
import comtypes # # 在 WeChat 对象的初始化之前，添加对 COM 库的初始化
import pythoncom
from wxauto import WeChat # 最重要的包，就是用它来发送微信消息的啦啦啦啦啦
from autologinWechat import WechatLogin  # 用于自动登录微信的

class WechatChannel():
    def __init__(self):
        self.wx = None

    def startup(self):
        '''
        确定用户是否已经登录微信，如果没有，尝试自动登录，如果用户设置了自动登录的功能，否则需要提醒。
        '''
        # comtypes.CoInitialize() # 初始化 COM 库（当前线程）
        pythoncom.CoInitialize()  # STA 初始化
        try:
            self.wx = WeChat()
            res = True
        except Exception as e:
            # print(f"检测微信运行状态出错: {e}")
            print("微信未登录，请先登录微信，并确保微信处于登录状态。")
            try:
                WechatLogin() #尝试自动登录
                time.sleep(20) #等待微信登录成功
                self.wx = WeChat()
                res = True
            except Exception as e:
                print(f"登录微信出错: {traceback.format_exc()}")  # 输出详细的堆栈信息
                print("请先登录微信，并确保微信处于登录状态。")
                res = False
        finally:
            # comtypes.CoUninitialize() # 释放 COM 库资源
            pythoncom.CoUninitialize()
            return res

    def sendMSG(self, strings, who):
        '''给某人发送消息，此处who表示的是备注名'''
        # comtypes.CoInitialize() # 初始化 COM 库（当前线程）
        pythoncom.CoInitialize()  # STA 初始化
        try:
            if self.wx == None:
                print("请先登录微信，并确保微信处于登录状态。")
                time.sleep(60)
                self.startup()
            
            # 登录后的话，发送微信消息        
            self.wx.SendMsg(msg=strings, who=who)
            time.sleep(random.randint(15, 30)) #20250113:将原先是停留3s的，改成增加发送时间延迟。避免微信官方识别到。随机停留15s-30s
            # time.sleep(random.randint(cfg['sendmsg2_mintime'], cfg['sendmsg2_maxtime']))
            res = "done"
        except Exception as e:
            print(f"发送微信消息出错: {e}")
            res = "error"
        finally:
            # comtypes.CoUninitialize() # 释放 COM 库资源
            pythoncom.CoUninitialize()
            return res

#========================================================================================
# test
#========================================================================================

# wcCl = WechatChannel()
# wcCl.startup() # 登录微信
# re = wcCl.sendMSG(strings='爷，你回来了吗？1', who='文件传输助手')
# wcCl.sendMSG(strings='爷，我又来麻烦您了。2', who='文件传输助手')
# wcCl.sendMSG(strings='传玺宝子，注意啦！时间的小沙漏已经快见底啦，下班的钟声马上就要敲响咯。我是自动推送的', who='黄传玺')