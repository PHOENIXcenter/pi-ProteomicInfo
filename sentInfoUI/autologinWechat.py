"""
20250306：
    代码实现原理详细解释
    1、is_wechat_running()：检查微信是否在运行

    2、使用 win32gui.FindWindow(None, "微信") 查找窗口句柄。
        如果返回值不是 0，说明微信窗口存在，也就说明微信正在运行；否则，微信没有运行。
        find_and_open_wechat()：查找并启动微信

        定义了多个可能的微信安装路径，分别是 32 位、64 位和用户本地目录下的路径。
        使用 subprocess.Popen(path) 启动微信进程。
        如果找不到微信的路径，提示用户手动启动。
    
    3、focus_wechat_and_login()：聚焦微信窗口并进行登录

        通过 win32gui.FindWindow(None, "微信") 查找微信窗口句柄。
        如果找到窗口，使用 win32gui.ShowWindow(hwnd, win32con.SW_RESTORE) 恢复窗口（如果窗口被最小化）。
        使用 win32gui.SetForegroundWindow(hwnd) 将窗口置于前台，确保微信获得焦点。
        模拟按下 Enter 键，使用 win32api.keybd_event() 实现键盘事件，模拟用户按下登录按钮。
    
    4、WechatLogin()：主程序控制

        检查微信是否已经在运行，如果运行了就跳过启动步骤，直接尝试自动登录。
        如果微信没有运行，则通过 find_and_open_wechat() 启动微信，并通过 focus_wechat_and_login() 进行登录。

"""
import os
import subprocess
import time
import win32gui
import win32con
import win32api

def is_wechat_running():
    """
    检查微信是否正在运行。
    
    通过查找微信窗口句柄来判断微信是否已经启动。
    - 如果找到了微信窗口的句柄，则说明微信正在运行。
    - 如果未找到微信窗口句柄，则说明微信未启动。
    """
    hwnd = win32gui.FindWindow(None, "微信")  # 获取微信窗口句柄，窗口名称是 "微信"
    return hwnd != 0  # 如果找到窗口句柄，返回 True，否则返回 False

def find_and_open_wechat():
    """
    查找并启动微信。
    
    - 尝试从多个路径中找到微信的可执行文件（WeChat.exe）。
    - 如果找到了微信的路径，则通过 subprocess 启动微信。
    - 如果没有找到微信，则提示用户手动启动微信。
    """
    possible_paths = [
        r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe",  # 默认安装路径（32位）
        r"C:\Program Files\Tencent\WeChat\WeChat.exe",        # 默认安装路径（64位）
        os.path.expandvars(r"%USERPROFILE%\AppData\Local\Tencent\WeChat\WeChat.exe")  # 用户目录中的路径
    ]
    
    for path in possible_paths:
        if os.path.exists(path):  # 如果找到了路径
            subprocess.Popen(path)  # 启动微信
            print(f"微信已启动: {path}")
            return True  # 返回 True，表示微信已启动
    
    print("未找到微信，请手动启动")
    return False  # 如果没有找到微信，返回 False

def focus_wechat_and_login():
    """
    让微信窗口获得焦点，并按下 Enter 键进行登录。
    
    1. 等待微信打开并稳定显示（用 sleep 来保证时间足够）。
    2. 查找微信的窗口句柄。
    3. 如果微信窗口存在，则将其恢复并置于前台。
    4. 模拟按下 Enter 键，尝试自动登录微信。
    """
    time.sleep(5)  # 等待 5 秒，确保微信已经完全打开
    hwnd = win32gui.FindWindow(None, "微信")  # 获取微信窗口句柄
    if hwnd:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)  # 如果微信窗口最小化，恢复窗口
        win32gui.SetForegroundWindow(hwnd)  # 将微信窗口置于最前面，获得焦点
        time.sleep(2)  # 等待 2 秒，确保窗口完全激活
        # 模拟按下 Enter 键，进行登录操作
        win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)  # 按下 Enter 键
        win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放 Enter 键
        print("已按下 Enter，尝试自动登录")
    else:
        print("未找到微信窗口，请手动扫码登录")

def WechatLogin():
    """
    主程序逻辑。
    
    1. 首先检查微信是否正在运行。
    2. 如果微信已运行，尝试将微信窗口聚焦并进行自动登录。
    3. 如果微信未运行，尝试启动微信并进行自动登录。
    """
    if is_wechat_running():  # 检查微信是否正在运行
        print("微信已在运行，无需重新启动")
    else:
        if find_and_open_wechat():  # 如果微信未运行，启动微信
            focus_wechat_and_login()  # 启动微信后，尝试自动登录

# if __name__ == "__main__":
#     WechatLogin()
