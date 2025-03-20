import os
import pytest
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from core.config import Config
from core.tts import TTSService

# 加载环境变量
project_root = Path(__file__).parent.parent
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

# 测试配置
TEST_OUTPUT_DIR = "output/ssml_tests"

@pytest.fixture
def get_env_var():
    """获取环境变量的帮助函数"""
    def _get_env_var(var_name: str) -> str:
        value = os.getenv(var_name)
        if not value:
            raise ValueError(f"环境变量 {var_name} 未设置，请检查.env文件")
        return value
    return _get_env_var

@pytest.fixture
def speaker_id(get_env_var):
    """获取话者ID"""
    return get_env_var("SPEAKER_ID")

@pytest.fixture
def tts_service(get_env_var):
    """创建TTS服务实例"""
    config = Config(
        appid=get_env_var("BYTEDANCE_APPID"),
        token=get_env_var("BYTEDANCE_TOKEN")
    )
    return TTSService(config)

@pytest.fixture(autouse=True)
def setup_test_env():
    """设置测试环境"""
    os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)
    yield
    # 测试后清理可以在这里添加

class TestSSML:
    """SSML功能测试类"""

    @pytest.mark.asyncio
    async def test_basic_speak(self, tts_service, speaker_id):
        """测试基本的speak标签"""
        ssml = "<speak>你好世界</speak>"
        output_path = os.path.join(TEST_OUTPUT_DIR, "basic_speak.mp3")
        
        result = await tts_service.synthesize_to_file(
            text=ssml,
            output_path=output_path,
            speaker_id=speaker_id,
            text_type="ssml"
        )
        
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0

    @pytest.mark.asyncio
    async def test_phoneme_tags(self, tts_service, speaker_id):
        """测试phoneme标签（多音字控制）"""
        test_cases = [
            {
                "name": "chinese_pinyin",
                "ssml": "<speak>《<phoneme alphabet=\"py\" ph=\"xi1 xi1\">茜茜</phoneme>公主》</speak>",
            },
            {
                "name": "multi_pronunciation",
                "ssml": "<speak>今天要去<phoneme alphabet=\"py\" ph=\"chi1\">吃</phoneme>饭</speak>",
            }
        ]
        
        for case in test_cases:
            output_path = os.path.join(TEST_OUTPUT_DIR, f"phoneme_{case['name']}.mp3")
            
            result = await tts_service.synthesize_to_file(
                text=case["ssml"],
                output_path=output_path,
                speaker_id=speaker_id,
                text_type="ssml"
            )
            
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0

    @pytest.mark.asyncio
    async def test_say_as_tags(self, tts_service, speaker_id):
        """测试say-as标签（语义类型）"""
        test_cases = [
            {
                "name": "number",
                "ssml": "<speak>数字<say-as interpret-as=\"cardinal\">123</say-as></speak>",
            },
            {
                "name": "date",
                "ssml": "<speak>日期<say-as interpret-as=\"date\">2024-03-19</say-as></speak>",
            },
            {
                "name": "telephone",
                "ssml": "<speak>电话<say-as interpret-as=\"telephone\">13812345678</say-as></speak>",
            }
        ]
        
        for case in test_cases:
            output_path = os.path.join(TEST_OUTPUT_DIR, f"say_as_{case['name']}.mp3")
            
            result = await tts_service.synthesize_to_file(
                text=case["ssml"],
                output_path=output_path,
                speaker_id=speaker_id,
                text_type="ssml"
            )
            
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0

    @pytest.mark.asyncio
    async def test_sub_tags(self, tts_service, speaker_id):
        """测试sub标签替换"""
        ssml = "<speak><sub alias=\"语音合成标记语言\">SSML</sub>测试</speak>"
        output_path = os.path.join(TEST_OUTPUT_DIR, "sub_basic.mp3")
        
        result = await tts_service.synthesize_to_file(
            text=ssml,
            output_path=output_path,
            speaker_id=speaker_id,
            text_type="ssml"
        )
        
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0

    @pytest.mark.asyncio
    async def test_combined_tags(self, tts_service, speaker_id):
        """测试组合标签"""
        ssml = "<speak>这是<phoneme alphabet=\"py\" ph=\"xi1 xi1\">茜茜</phoneme>公主的<say-as interpret-as=\"date\">2024-03-19</say-as>故事</speak>"
        output_path = os.path.join(TEST_OUTPUT_DIR, "combined_tags.mp3")
        
        result = await tts_service.synthesize_to_file(
            text=ssml,
            output_path=output_path,
            speaker_id=speaker_id,
            text_type="ssml"
        )
        
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0

    @pytest.mark.asyncio
    async def test_edge_cases(self, tts_service, speaker_id):
        """测试边界情况"""
        test_cases = [
            {
                "name": "max_length",
                "ssml": "<speak>" + "测试" * 75 + "</speak>",  # 150字符限制
            },
            {
                "name": "special_chars",
                "ssml": "<speak>测试!@#$%^&*()特殊字符</speak>",
            }
        ]
        
        for case in test_cases:
            output_path = os.path.join(TEST_OUTPUT_DIR, f"edge_{case['name']}.mp3")
            
            try:
                result = await tts_service.synthesize_to_file(
                    text=case["ssml"],
                    output_path=output_path,
                    speaker_id=speaker_id,
                    text_type="ssml"
                )
                
                assert os.path.exists(output_path)
                assert os.path.getsize(output_path) > 0
            except Exception as e:
                if case["name"] == "max_length":
                    # 如果是最大长度测试，预期可能会失败
                    assert str(e).__contains__("字符超限") or str(e).__contains__("too long")
                else:
                    raise
