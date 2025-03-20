# 英文SSML测试计划

## 概述
本测试计划专注于验证英文SSML功能，确保各种SSML标签在英文场景下的正确处理和组合使用。

## 测试范围
1. 基础SSML结构验证
2. 音标发音控制
3. 特殊文本类型处理
4. 文本替换功能
5. 组合使用场景
6. 地址和电子格式处理
7. 停顿控制

## 测试用例设计

### 1. 音标测试（Phoneme Tests）

#### CMU音标格式
```xml
<speak>
    The name is <phoneme alphabet="cmu" ph="p iy1 t er0">Peter</phoneme>, 
    and this is <phoneme alphabet="cmu" ph="m ay1 k ah0 l">Michael</phoneme>.
</speak>
```

#### IPA音标格式
```xml
<speak>
    Welcome to <phoneme alphabet="ipa" ph="ˈlʌndən">London</phoneme>, 
    the capital of <phoneme alphabet="ipa" ph="ˈɪŋglənd">England</phoneme>.
</speak>
```

[... 之前的其他测试用例 ...]

### 7. 停顿控制测试（Break Tests）

#### 基本停顿
```xml
<speak>
    First part<break time="100ms"/>second part.
</speak>
```

#### 不同时长的停顿
```xml
<speak>
    First sentence.<break time="300ms"/>
    Second sentence,<break time="500ms"/>
    Third sentence.<break time="1000ms"/>
    Final sentence.
</speak>
```

#### 停顿与标点组合
```xml
<speak>
    First sentence.<break time="300ms"/>
    Second sentence,<break time="100ms"/>
    with a brief pause.<break time="500ms"/>
    Final sentence.
</speak>
```

## 实现方案

### 测试文件组织
- 位置：`tests/test_ssml_en.py`
- 测试类：
  - `TestSSMLEnglish`：基本SSML功能测试
  - `TestSSMLBreak`：停顿控制测试

### 验证方法
1. 基本检查：
   - 音频文件生成
   - 文件大小验证
2. 人工验证：
   - 发音准确性
   - 停顿时长是否符合预期
   - 标点和停顿组合效果

## 注意事项
- 所有测试使用英文语音模型
- break标签支持毫秒级控制（ms单位）
- break标签可以和标点符号结合使用
- 建议通过人工试听验证停顿效果

## 测试输出
1. 音频文件存储在 `output/ssml_tests_en/` 目录
2. 文件命名规则：
   - 基本测试：`{测试类型}_{测试名称}.mp3`
   - 停顿测试：`break_{测试名称}.mp3`
