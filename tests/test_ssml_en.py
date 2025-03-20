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
TEST_OUTPUT_DIR = "output/ssml_tests_en"

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

class TestSSMLBreak:
    """Test SSML break functionality"""

    @pytest.mark.asyncio
    async def test_break_tag(self, tts_service, speaker_id):
        """Test break tag with different durations"""
        test_cases = [
            {
                "name": "short_break",
                "ssml": """<speak>
                    First part<break time="100ms"/>second part.
                </speak>""",
            },
            {
                "name": "medium_break",
                "ssml": """<speak>
                    First sentence.<break time="500ms"/>Second sentence.
                </speak>""",
            },
            {
                "name": "long_break",
                "ssml": """<speak>
                    Paragraph one.<break time="1000ms"/>Paragraph two.
                </speak>""",
            }
        ]
        
        for case in test_cases:
            output_path = os.path.join(TEST_OUTPUT_DIR, f"break_{case['name']}.mp3")
            
            try:
                result = await tts_service.synthesize_to_file(
                    text=case["ssml"],
                    output_path=output_path,
                    speaker_id=speaker_id,
                    text_type="ssml"
                )
                
                assert os.path.exists(output_path)
                assert os.path.getsize(output_path) > 0
                print(f"Successfully generated {case['name']} with break tag")
            except Exception as e:
                print(f"Failed to process {case['name']}: {str(e)}")
                raise

    @pytest.mark.asyncio
    async def test_break_with_punctuation(self, tts_service, speaker_id):
        """Test breaks with different punctuation marks"""
        ssml = """<speak>
            First sentence.<break time="300ms"/>
            Second sentence,<break time="100ms"/>
            with a brief pause.<break time="500ms"/>
            Final sentence.
        </speak>"""
        output_path = os.path.join(TEST_OUTPUT_DIR, "break_punctuation.mp3")
        
        try:
            result = await tts_service.synthesize_to_file(
                text=ssml,
                output_path=output_path,
                speaker_id=speaker_id,
                text_type="ssml"
            )
            
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
            print("Successfully generated audio with mixed breaks and punctuation")
        except Exception as e:
            print(f"Failed to process breaks with punctuation: {str(e)}")
            raise
