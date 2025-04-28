！！！为避免报错，应使用管理员权限来运行该程序。

文件说明：
0、my_icon.ico 界面的头像
1、ui/sentInfo_231107-xw.ui  设置UI界面
2、requirements.txt， 配置虚拟环境时，所用的各种python library. 使用python=3.7
3、autologinWechat.py  检测微信是否登录并尝试自动登录微信（设定自动登录方可）的脚本函数。
4、dbOperate.py   数据操作的所有相关函数，数据库主要是记录哪些文件已被发送、发送时间，发送给谁等信息
5、receiveFileServer.py  用于接收文件的函数，利用监控指定的端口号进行。多线程控制。
6、WechatChannel.py   利用autologinWechat.py检测并尝试自动登录微信，wxauto库进行发送微信的函数。缺点是一分钟发送信息2-4条，避免被封控。
7、sendInfoProgram.py  结合receiveFileServer.py和WechatChannel.py，实现在指定时间内，接收文件后即发送。非指定时间，仅接收文件，等到了指定的时间点，则立即推送信息。
8、sentInfoUI.py UI界面和sendInfoProgram.py结合，实现参数界面化设置，程序界面化运行，每一个按钮都是单独启动一个进程或线程。
9、sentInfoUI.spec  打包成exe的配置文件。使用脚本
```
pyinstaller -F .\sentInfoUI.py -i .\my_icon.ico --hidden-import "comtypes.stream"  --hidden-import "comtypes.client._generate"  --hidden-import "comtypes.gen.Excel"   --hidden-import "comtypes.gen.UIAutomationClient"
```
