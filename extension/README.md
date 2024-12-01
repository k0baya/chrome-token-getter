## chrome-token-getter 
基于 [wozulong/ChatGPTAuthHelper](https://github.com/wozulong/ChatGPTAuthHelper/) 以及 [xyhelper/xyhelper-chrome-login](https://github.com/xyhelper/xyhelper-chrome-login) 修改的小工具，可以自定义服务端地址，增强了通用性。


### 使用步骤：

1. 下载[本仓库代码](https://github.com/k0baya/chrome-token-getter/archive/refs/heads/master.zip)并解压缩。
2. 打开 `Chrome` ，地址栏输入： `chrome://extensions` 打开 `扩展程序` 设置页面。
3. 右上角打开 `开发者模式` 。
4. 点击左上角 `加载已解压的扩展程序` 按钮，选择刚下载解压的插件文件夹内的 `extension` 目录，确定安装。

### 使用方法
首次点击插件图标，将打开设置页面，设置远端服务的地址后，再次点击插件图标，将自动打开 chatgpt 的登录页面，登录后即可获取 refreshToken。
