# 声音克隆测试程序

这是一个基于字节跳动API的声音克隆测试程序，提供以下功能：
- 查询音色训练状态
- 文本转语音（TTS）合成

## 功能特点
- 支持从文件读取待合成文本
- 自动检查文本字节长度
- 可调节语速
- 输出MP3格式音频

## 目录结构
```
.
├── core/              # 核心功能模块
│   ├── __init__.py
│   ├── config.py      # 配置管理
│   ├── tts.py        # 文本转语音
│   └── voice_cloning.py  # 声音克隆
├── input.txt          # 待合成文本
├── voice_clone_test.py # 主程序
└── setup.py          # 项目配置
```

## 使用方法
1. 运行程序：
```bash
python voice_clone_test.py
```

2. 输入配置信息：
- BYTEDANCE_APPID
- BYTEDANCE_TOKEN
- 音色ID（以S_开头）

3. 使用功能：
- 选择1：查询音色训练状态
- 选择2：合成语音
- 选择0：退出程序

4. 合成语音时：
- 编辑input.txt文件输入要合成的文本
- 设置语速（0.2-3.0）
- 输入输出文件前缀
- 生成的音频文件保存在output目录