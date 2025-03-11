import os
import pytest
from core import Config, VoiceCloningService, TTSService

@pytest.fixture
def config():
    appid = os.environ.get('BYTEDANCE_APPID')
    token = os.environ.get('BYTEDANCE_TOKEN')
    if not appid or not token:
        pytest.skip("需要设置 BYTEDANCE_APPID 和 BYTEDANCE_TOKEN 环境变量")
    return Config(appid=appid, token=token)

@pytest.fixture
def speaker_id():
    speaker_id = os.environ.get('TEST_SPEAKER_ID')
    if not speaker_id:
        pytest.skip("需要设置 TEST_SPEAKER_ID 环境变量")
    return speaker_id

@pytest.mark.asyncio
async def test_get_voice_status(config, speaker_id):
    service = VoiceCloningService(config)
    status = await service.get_status(speaker_id)
    assert 'status' in status
    assert status['speaker_id'] == speaker_id

@pytest.mark.asyncio
async def test_text_to_speech(config, speaker_id, tmp_path):
    service = TTSService(config)
    text = "这是一个测试。"
    output_path = tmp_path / "test_output.mp3"
    
    await service.synthesize_to_file(
        text=text,
        output_path=str(output_path),
        speaker_id=speaker_id
    )
    
    assert output_path.exists()
    assert output_path.stat().st_size > 0