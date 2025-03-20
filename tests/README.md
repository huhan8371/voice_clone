# SSML测试说明

## 环境准备

1. 创建环境配置文件
```bash
# 在项目根目录下，复制环境变量模板
cp .env.example .env

# 编辑项目根目录下的.env文件，填入实际的配置值：
BYTEDANCE_APPID=你的APPID
BYTEDANCE_TOKEN=你的TOKEN
SPEAKER_ID=你的音色ID  # 例如：S_0
```

2. 安装依赖
```bash
# 安装项目及其依赖
pip install -e .

# 安装测试依赖
pip install pytest pytest-asyncio python-dotenv
```

## 运行测试

1. 运行所有SSML测试
```bash
# 在项目根目录下运行
pytest tests/test_ssml.py -v
```

2. 运行特定测试
```bash
# 运行基础speak标签测试
pytest tests/test_ssml.py::TestSSML::test_basic_speak -v

# 运行phoneme标签测试
pytest tests/test_ssml.py::TestSSML::test_phoneme_tags -v

# 运行say-as标签测试
pytest tests/test_ssml.py::TestSSML::test_say_as_tags -v
```

## 测试输出

1. 音频文件位置
- 所有生成的音频文件都保存在 `output/ssml_tests/` 目录下
- 文件命名规则：`{测试类型}_{测试名称}.mp3`

2. 测试结果说明
- 每个测试都会验证：
  - 音频文件是否成功生成
  - 文件大小是否大于0
- 对于边界测试：
  - 最大长度测试可能会抛出字符超限错误
  - 特殊字符测试验证系统处理特殊字符的能力

## 注意事项

1. 运行测试前请确保：
- 项目根目录下的.env文件配置正确
- 项目已经通过pip install -e .安装
- 有足够的磁盘空间存储生成的音频文件

2. 音频验证
- 建议手动检查生成的音频文件，验证SSML标记是否正确影响了语音输出
- 特别关注多音字控制和文本替换的效果

3. 清理建议
- 测试完成后可以清理 `output/ssml_tests/` 目录
- 保留特定测试案例的音频文件用于后续比对

## 测试用例说明

1. 基础测试 (test_basic_speak)
- 验证最基本的speak标签包装功能
- 输出文件：basic_speak.mp3

2. 多音字控制测试 (test_phoneme_tags)
- 验证拼音标记对多音字的控制
- 测试案例：
  - 茜茜公主(xi1 xi1)
  - 吃饭(chi1)
- 输出文件：phoneme_*.mp3

3. 语义类型测试 (test_say_as_tags)
- 验证不同类型文本的特定读法
- 测试数字、日期、电话号码等
- 输出文件：say_as_*.mp3

4. 文本替换测试 (test_sub_tags)
- 验证alias替换功能
- 输出文件：sub_basic.mp3

5. 组合标签测试 (test_combined_tags)
- 验证多个SSML标签的组合使用
- 输出文件：combined_tags.mp3

6. 边界测试 (test_edge_cases)
- 验证字符长度限制
- 验证特殊字符处理
- 输出文件：edge_*.mp3

## 配置文件说明

项目使用.env文件管理配置信息，该文件应位于项目根目录下：

```ini
# .env文件配置项说明
BYTEDANCE_APPID=字节跳动应用ID
BYTEDANCE_TOKEN=访问令牌
SPEAKER_ID=音色ID（例如：S_0）
```

注意：
- 不要将.env文件提交到版本控制系统
- 可以参考项目根目录下的.env.example创建自己的.env文件
- 确保所有必需的配置项都已设置

## 关于pytest.ini配置

项目根目录下的pytest.ini文件用于配置pytest的行为：
- 设置测试发现规则
- 配置警告处理
- 设置异步测试行为

确保该文件存在并包含正确的配置。
