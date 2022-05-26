2022-05-01

## 环境  
1、python==3.10.4  
2、pycharm运行时版本: 11.0.14.1+1-b2043.45 amd64  
3、windows10  
4、anaconda3 2022.05  
相关软件安装配置和破解教程可baidu  
可选工具Navicat版本15.0.26和MySQL版本8.0.29

## 步骤
一、下载源码。从官网git仓库下载vnpy的python源码 vnpy_master.zip，解压到一具体文件夹，eg: E:\projects\vnpy300  这个时间我下载的是vnpy3.1.0版本。

二、配置python解释器。打开pycharm，打开源码所在项目文件夹，最好新建一个虚拟环境 eg：命令行输入 conda create -n vnpy300 python==3.10，然后pycharm选择这个环境的python解释器。

三、配置vnpy运行所需环境。vnpy_3_1_0所需的python模块包，存放在vnpy300下的requirements.txt文件内。两种处理方式，第一在这个文件的目录下，命令行运行install.bat的windows批处理程序，第二按照requmirements文件里的所需模块名和版本，依次安装。eg:在激活环境vnpy300情况下输入 pip install numpy==1.21.5。推荐第一种方法，这步是关键，如果报错，老手调试，新手建议重来，哈哈~

四、运行。在vnpy300项目文件下，创建一个新的run.py文件，代码写上本介绍文档下的run.py

五、实际运行还需要安装vnpy的封装模块，本价绍文档下的vnpy模块文件。
