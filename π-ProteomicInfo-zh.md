





## 目录

[TOC]

## 1. π-ProteomicInfo

π-ProteomicInfo是一套自动化的工作处理流程，主要为SearchServer、SearchClient、sendInfo三个部分，包含从质谱采集电脑到搜库电脑的数据传输，基于搜库结果的文件信息提取及质谱文件的质控、质控结果信息发送等步骤。



## 2. SearchServer

SearchServer模块在专用数据处理工作站或数据处理服务器上运行，从SearchClient模块接收数据和参数，以执行预定义的数据处理工作流。数据搜索完成后，根据综合搜索结果触发质控信息提取程序，提取出来的质控信息转发给sentInfoUI模块。

![Main](I:\HuiYan_Project\Article\Auto_Platform\Software\Picture\Server\Main.PNG)

​                                                                                                                         SearchServer主界面

### 2.1 菜单栏 

SearchServer菜单栏包含三个子模块，不同子模块执行不同功能：

1. SearchServer子模块执行软件的自动搜库功能；
2. CohortData子模块执行软件对于队列搜库结果的预处理功能；
3. SingleData子模块执行软件对于单针自动搜库结果整理功能；

软件支持不同子功能或多个相同子功能同步运行。

![2](I:\HuiYan_Project\Article\Auto_Platform\Software\Picture\Server\2.png)





### 2.2 RunServer

软件通过不同的端口（Port）号绑定不同的运行参数，质谱电脑对应端口处理的数据将执行搜库电脑相同端口的参数进行搜库，需要留意，当界面成功运行后，参数的修改对应当前界面不再起作用。

#### 2.2.1 MaxQuant界面

##### 参数文件生成

参数文件可通过MaxQuant软件UI界面设置，设置后保存mqpar.xml文件即可进行后续使用。

##### 利用网络端口进行数据传输

设置下列参数后，用户可以在接收数据路径发现新生成的参数文件（mqpar.xml），该参数文件需拷贝至文件采集电脑并进行使用，使用方式见对应客户端描述。

![3](I:\HuiYan_Project\Article\Auto_Platform\Software\Picture\Server\3.PNG)

1. MaxQuant自动搜库运行程序设定的端口，用于数据接收；
2. 参数记录按钮，点击按钮后，已设定的端口 参数将被记录，配合3使用；
3. 参数查询按钮，点击按钮后，自动显示端口号对应的参数，配合2使用；
4. MaxQuantCMD.exe文件路径，按钮可进行路径寻找；
5. 接收数据存放地址，按钮可进行路径寻找；
6. MaxQuant参数文档即mqpar.xml文件；
7. 根据mqpar.xml文件自动显示；
8. 根据mqpar.xml文件自动显示;


#### 2.2.2 Proteome Discoverer（PD）

##### 参数文件生成

PD自动搜库所需的参数文件与对应study文件相同，即Consensus与Processing文件，用户可在软件内部设定所需的修饰与序列信息更换等步骤，其中Consensus步骤需确保添加“Result Exporter”节点来保证后续文件的产生，设置完成后导出对应文件，使用方式见对应客户端描述。

![8](I:\HuiYan_Project\Article\Auto_Platform\Software\Picture\Server\8.png)

![9](I:\HuiYan_Project\Article\Auto_Platform\Software\Picture\Server\9.png)

​                                                                                                              Result Exporter节点的添加

在Daemon中导入对应的Consensus与Processing文件，设定文件传输使用的项目名，导出参数文件并拷贝到文件采集电脑使用。

![10](I:\HuiYan_Project\Article\Auto_Platform\Software\Picture\Server\10.PNG)

##### 利用网络端口进行数据传输

利用已生成的参数文件设置如下参数，即可进行预设参数的数据处理。

![5](I:\HuiYan_Project\Article\Auto_Platform\Software\Picture\Server\5.PNG)

1. Proteome Discoverer自动搜库运行程序设定的端口，用于数据接收；
2. 参数记录按钮，点击按钮后，已设定的端口 参数将被记录，配合3使用；
3. 参数查询按钮，点击按钮后，自动显示端口号对应的参数，配合2使用；
4. Daemon.exe文件路径，按钮可进行路径寻找；
5. 接收数据存放地址，按钮可进行路径寻找；
6. Proteome Discoverer软件可执行的参数文件；
7. 搜库电脑用户名；
8. 搜库电脑主机名;

##### 利用Daemon进行数据传输

当文件采集电脑与搜库电脑可以通过Daemon软件进行访问时，用户可跳过上述设置，进入Proteome Discoverer设置界面，完成Daemon程序的设定，如下图所示，PD中点击administration，左下方Configuration中点选Discoverer Daemon，在右方的界面选择数据接收的存储路径，完成后，点选Apply，再点Yes保存，重启PD。

![6](I:\HuiYan_Project\Article\Auto_Platform\Software\Picture\Server\6.png)

![7](I:\HuiYan_Project\Article\Auto_Platform\Software\Picture\Server\7.png)



#### 2.2.3 Spectronaut

##### 参数文件生成

spectronaut搜库参数文件中，需要在对应模式对directDIA设置中添加名为"huiyan.rs"的参数设置文件，并在报告导出选项中设定导出对应报告内容，保存后的报告模板即*.prop文件将在端口设置中使用，，使用方式见对应客户端描述。设置界面如下图所示：

![11](I:\HuiYan_Project\Article\Auto_Platform\Software\Picture\Server\11.PNG)

##### 利用网络端口进行数据传输

利用已生成的参数文件设置如下参数，即可进行预设参数的数据处理。

![4](I:\HuiYan_Project\Article\Auto_Platform\Software\Picture\Server\4.PNG)

1. Spectronaut自动搜库运行程序设定的端口，用于数据接收；
2. 参数记录按钮，点击按钮后，已设定的端口 参数将被记录，配合3使用；
3. 参数查询按钮，点击按钮后，自动显示端口号对应的参数，配合2使用；
4. Spectronaut.exe文件路径，按钮可进行路径寻找；
5. 接收数据存放地址，按钮可进行路径寻找；
6. 单针搜库结果存放路径；
7. Spectronaut搜库使用的bgsfasta文件；
8. 可选，是否存在使用的库文件;
9. Spectronaut使用的工作流文件；



#### 2.2.4 DIA-NN

DIA-NN被设置在Linux服务器运行，脚本可以在采集期间完成大多数文件的单针搜库，基于DIA-NN可以利用单针quant文件的特点，大队列数据的搜库将显著减少时间消耗。**对于raw文件,"ThermoRawFileParser"软件需要提前安装以完成格式转换功能**。



### 2.3 RunDaily

模块支持并行运行，点击主界面"Daily_Monitor"按钮或在菜单栏按钮中执行，功能主要包含两部分：

1. 配合自动搜库程序，实现对应单针数据的搜库结果的信息提取，用户可自定义结果扫描软件与结果扫描频率；
2. 基于预设的参考模板，对符合规则的文件进行比对，通过提取的结果信息，评判质谱状态是否异常；

![12](I:\HuiYan_Project\Article\Auto_Platform\Software\Picture\Server\12.PNG)



当"Ignore Abnormal"选项被选择时，功能仅执行单针结果信息提取功能。"Report Abnormal"选项选择时，用户可通过参考数据的添加、更新等步骤实现新质谱文件基于参考数据的评判。



### 2.4 RunStat

数据统计模块，可用于单针与队列数据原始结果统计，适配RunDaily与StatCohort模块。



### 2.5 ResultSummary

子模块执行单针结果合并统计功能，配合RunDaily结果使用，方便用户统计。Regular选项支持多个匹配规则同时执行，满足所有规则的数据将被统计，不同规则以分号";"分开，如"TOF2;QC;DIA"，Regular选项未输入内容时，监控目录下的所有文件将执行合并程序。

![13](I:\HuiYan_Project\Article\Auto_Platform\Software\Picture\Server\13.PNG)





### 2.6 StatCohort

子模块执行软件原始搜库结果的统计。

1. 对于MaxQuant，Monitor_Dir选择combine文件夹中的txt文件夹；
2. 对于MSFragger，Monitor_Dir选择MSFragger结果文件夹；
3. 对于Spectronaut，Monitor_Dir选择软件导出文件（导出模块参考RunServer设置的"huiyan_protein.rs"模版）；

![14](I:\HuiYan_Project\Article\Auto_Platform\Software\Picture\Server\14.PNG)



### 2.7 RunCohort



子模块对各种输入执行数据预处理功能，包括：

1. 定量矩阵来自Spectronaut（报告模版，‘huiyan_ProteinQuant’）；
2. MaxQuant的原始数据库搜索结果；
3. MSFragger的原始数据库搜索结果；
4. 普通定量矩阵（ID列+强度值表达列）；

预处理任务包括几个关键步骤：**质量控制**/**标准化**/**填补缺失值**/**结果的基本显示**：提供处理数据的直观可视化。下图显示了MaxQuant、MSFragger和Spectronaut软件原始导出结果的设置界面，以及通用定量矩阵（Maxtrix）。



![MaxQuant](I:\HuiYan_Project\Article\Auto_Platform\Software\Picture\Server\MaxQuant.PNG)

​																													MaxQuant设置示例界面

![MSFragger](I:\HuiYan_Project\Article\Auto_Platform\Software\Picture\Server\MSFragger.PNG)

​																													MSFragger设置示例界面

![Spectronaut](I:\HuiYan_Project\Article\Auto_Platform\Software\Picture\Server\Spectronaut.PNG)

​																													Spectronaut设置示例界面

![Matrix](I:\HuiYan_Project\Article\Auto_Platform\Software\Picture\Server\Matrix.PNG)

​																													一般定量矩阵（Matrix）设置示例界面

Name_Maping选项为原始文件改名文件，**文件强制要求为csv格式，推荐通过excel另存为选项保存csv文件**，用户可以在该文件中调整后续图表中的命名及指定样本对应分组信息，如下方表格所示：

| #RawName             | ChangeName | Group | Other |
| -------------------- | ---------- | ----- | ----- |
| xxxx_A_xxxx_XXX_XX_1 | A_1        | A     | XX    |
| xxxx_A_xxxx_XXX_XX_2 | A_2        | A     | XX    |
| xxxx_B_xxxx_XXX_XX_1 | B_1        | B     | XX    |
| xxxx_B_xxxx_XXX_XX_2 | B_2        | B     | XX    |
| xxxx_C_xxxx_XXX_XX_1 | C_1        | C     | XX    |
| xxxx_C_xxxx_XXX_XX_2 | C_2        | C     | XX    |

**#RawName: 定量文件中对应的列名，MaxQuant中为设置的Experiment列名，首列列名固定不建议修改**；

ChangeName: 样本改名后的内容，不允许重复值；

Group: 样本分组信息，部分图片中将展示分组情况；

Other: 其他临床信息文件，不被使用；



## 3. SearchClient

SearchClient模块在质谱数据采集计算机上运行，在间隔时间内评估采集文件的完整性，确定是否应将其提交给Server模块进行数据处理，模块还支持使用不同参数模板并行执行。数据传输使用Socket工具或Daemon工具。在设置界面的下拉菜单栏中，单击可显示预设样例。

![image-20250427115200657](C:\Users\huang\AppData\Roaming\Typora\typora-user-images\image-20250427115200657.png)







### 3.1 MaxQuant  & Spectronaut & DIA-NN

界面包含以下6个部分，参数设置完成后，针对特定文件夹及其子文件夹的数据监控将开始运行，旧文件默认不处理，新文件采集完成时，将开始运行数据传输并在搜库电脑端自动搜库，

**DIA-NN无需特定客户端，借助MaxQuant或Spectronaut任意客户端即可完成数据传输，参数文件可以选择任意文件**：

![2](I:\HuiYan_Project\Article\Auto_Platform\Software\Picture\Client\2.PNG)

1. 数据传输目的电脑；
2. 数据传输电脑配置，用户可根据IP地址进行更新；
3. 数据传输端口，该端口与RunServer端设定端口一致，才能执行Server端设定的参数文档；
4. 数据临时存放位置，数据传输成功后，传输文件将清除，**强烈建议与采集文件存放位置区分**；
5. 数据采集文件夹，通过监控采集文件新文件状态判断是否启动数据传输；
6. 参数文件，由RunServer客户端生成；



### 3.2 Proteome Discoverer

Ptoteome Discoverer（PD）界面有所区分，当借助Daemon软件可以在客户端访问搜库电脑PD程序时，借助质谱电脑端**Daemon**程序可以进行数据传输，Daemon_Exe为对应的Daemon.exe程序所在路径。当无法通过Daemon访问时，基于Socker端口的数据传输需要被执行，此时需**点击Socker按钮**，对应参数可参考上述MaxQuant & Spectronaut设置。

![3](I:\HuiYan_Project\Article\Auto_Platform\Software\Picture\Client\3.PNG)



## 4. sentInfoUI

### 4.1 功能概述

本程序主要用于：

1. 实时接收质谱结果文件（Search Result）与仪器报警文件（Warning）
2. 将接收到的文件摘要或报警信息，通过微信（WeChat）或电子邮件（Email）推送给对应工程师

适用场景：质谱平台日常运行监控，及时获知数据处理结果与仪器状态。

------



### 4.2 安装与启动

1. **免安装**：下载 ZIP 包后，解压到任意本地文件夹。
2. 双击运行 `sentInfoUI_en.exe`（或 `sentInfoUI.exe`）即可打开程序主界面，无需额外依赖。

------



### 4.3 界面与参数说明

程序主界面分为两大模块：**Parameter Settings**（参数设置） 和 **Run Control**（程序运行）。

#### 4.3.1 Parameter Settings（参数设置）

- **Send Method（发送方式）**
  选择用于消息推送的方式：
  - **WeChat**：通过模拟鼠标键盘操作，利用本机登录的微信客户端发送消息。
  - **Email**：通过配置 SMTP 服务器发送电子邮件。
- **Daily Sending Time Period（每天发送时间段）**
  设置每天允许程序发送消息的时间范围。包括：
  - **Start Time**：起始时间（例如 08:00）
  - **End Time**：结束时间（例如 18:00）
    超出该时间段，程序将暂不推送消息。
- **Port Number（端口号）**
  设置程序监听的本地端口，用于接收外部传来的结果文件。需确保该端口未被占用。
- **Administrator（管理员）**
  输入管理员微信的备注名，用于接收系统运行状态或错误通知。必须与微信中备注一致。
- **Storage Location for Search Results（搜库结果存放位置）**
  选择一个本地文件夹，程序会将接收到的搜库文件或报警信息保存到该目录下。
- **File Extension（文件后缀名）**
  用于区分不同软件输出的文件类型。例如：
  - `MQ_Stat_Summary.txt` 表示 MaxQuant 结果
  - `PD_Stat_Summary.txt` 表示 Proteome Discoverer 结果
  - `SP_Stat_Summary.txt` 表示 Spectronaut 结果
  - `warn.txt` 表示报警文件
- **Email Information（邮箱信息）**
  如选择 Email 模式，需填写以下字段：
  - 发件人邮箱地址
  - 邮箱授权码或登录密码
  - SMTP 服务器地址（如 smtp.qq.com）
  - SMTP 端口号（常见如 465 或 587）
- **Mass Spectrometer（质谱仪信息）**
  添加每台质谱仪的名称及其在文件名中对应的简写。简写支持多个，用 `|` 分隔。程序将通过文件名自动判断文件来源。
  - Name：全称
  - Abbreviation：文件名中简写，多值用 `|`隔开
- **Engineer（工程师设置）**
  设置每位工程师负责的质谱仪及项目内容，并指定微信备注名或邮箱地址。程序将根据这些信息推送相应的内容。
  - Engineer：微信备注名
  - Mass Spectrometer：对应仪器名称
  - Project：项目标识（可选）
  - Email：仅 Email 模式必填
- **Software（软件字段设置）**
  选择要提取的搜库结果字段内容。界面左侧展示可用字段（Options），右侧为将要推送的字段（Content to Send），可通过按钮 `>>>`/`<<<` 添加或移除字段。
- **Save（保存）**
  点击此按钮可将当前所有设置保存至本地配置文件，下次启动程序时自动加载。

#### 4.3.2 Run Control

- **Run（运行）**

  启动接收与推送服务，进入“监听”状态，并在设定时间段内自动发送消息。

- 功能：

  - 启动后程序会在指定端口监听文件到来，并根据扩展名与表格配置，自动匹配对应质谱仪及工程师。
  - 在`Send Method`对应时间段内，将生成的摘要或报警信息推送给相应人员。

------



### 4.4 典型操作流程

1. 解压并双击 `sentInfoUI_en.exe`。
2. 在 **Parameter Settings** 中：
   - 选择 **Send Method** → “Email”。
   - 填写 **Email Information**（Sender Email、Password/Token、SMTP Server、Port）。
   - 设置 **Daily Sending Time Period**（如 09:00–17:00）。
   - 指定 **Port Number**（如 5000）与 **Storage Location**（如 `D:\Results`）。
   - 配置 **Mass Spectrometer** 与 **Engineer** 对照表，确保项目标识正确。
   - 在 **Software** 中选取需推送的结果字段，点击 **Save**。
3. 切换到 **Run Control**，点击 **Run**。
4. 当文件到达时，程序将自动分类、摘要并发送通知。

------

### 4.5 注意事项

- 微信方式需保证本机已登录微信网页版或客户端，且备注名与“Engineer”表中一致。
- Email 模式请使用授权码／SMTP Token，避免使用登录密码。
- 如需修改配置，先点击 **Stop**（程序停止），调整后再次 **Save** 并 **Run**。
- 请确保防火墙打开监听端口，或将程序添加为例外。



## 5. 常见问题

### 5.1 SearchServer

1. **如何确认自动搜库程序是否正常运行？**

- 检查数据接收文件夹是否有接收文件；
- 检查搜库结果文件夹是否有结果文件生成，MaxQuant结果文件夹与数据存放位置相同，Spectronaut结果文件位于设置的路径（搜库完成时生成），PD可在对应的界面程序查看；

2. **程序正常运行后，间隔多长时间可以看到搜库结果？**

- 正常运行状态下，默认设置约1-2h后数据将自动发送至搜库电脑开始搜库，搜库时间取决于搜库电脑的配置及搜库软件（搜库时间与人工操作耗时相同）；
- 文件扫描间隔时间由SearchClient端设置，路径为SearchClient安装文件所在的Config目录中的"Monitor_Time.txt"文件决定；

3. **搜库结果如何查看？**

- 结果文件存放于对应与软件结果文件夹，PD&Spectronaut由用户设定，MaxQuant结果文件与存放地址相同；
- 当sendInfoUI模块运行后，RunDaily提取到的结果将经由sendInfoUI模块发送给指定工程师；

4. **RunCohort模块运行报错？**

- NameMaping文件即样本列名改名文件，通过该文件修改后续处理文件的列名，确认选择文件是否异常，文件保存格式为csv格式，必要时重新生成文件；
- Input选项是否符合要求；MaxQuant&MSFragger输入为结果文件夹，Spectronaut&Matrix输入为单个文件；



### 5.2 SearchClient

1. **如何添加搜库电脑？**

- 确保搜库电脑与质谱电脑是否处于相同网络中，通过主界面PC_Setting选项添加新电脑，直接修改Config目录中"IP_Config.txt"文件也是支持的；

2. **界面自动关闭原因？**

- 检查与搜库电脑网络是否连通；
- 检查是否存在多个程序同时监控同一个文件夹或另一个程序监控当前文件夹子目录；

3. **程序异常关闭后，如何重启？**

- 一般短期异常关闭，用户重复之前的操作即可完成中断期间样本的续传；
- 长期关闭情况下，建议删除监控目录下"Complete_FileName_List.txt"，重新运行程序，程序将对新产生的文件进行搜库处理；

4. **如何对已采集完成的文件进行自动搜库？**

- 通过修改目标文件夹"Complete_FileName_List.txt"文件，文件已记录的文件不会被传输至搜库电脑，当删除对应的文件名，软件将认为该文件是新文件，自动搜库流程将被执行；
- 同时删除多个文件时，文件的传输顺序随机，仅当前批次文件均执行流程成功后，相应的文件名将记录在"Complete_FileName_List.txt"文件中，中途失败时，请调整"Complete_FileName_List.txt"文件内容，以免反复传递已搜库的文件；



### 5.3 sendInfoUI

1. **为什么没收到微信消息？**
   - 确认微信已登录且程序有操作权限；备注名精确匹配。
   - 检查“Daily Sending Time Period”是否包含当前时间。
2. **邮箱发送失败，提示认证错误？**
   - 请到邮箱设置获取 SMTP 授权码，并更新 **Email Password or Authorization Code**。
3. **文件未被识别？**
   - 检查 **File Extension** 配置是否与实际文件名后缀一致。
   - 确保 **Mass Spectrometer Abbreviation** 与文件名简写匹配。