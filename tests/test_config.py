import pytest
from core.config import Config

def test_config_initialization():
    config = Config(
        appid="test_appid",
        token="test_token"
    )
    assert config.appid == "test_appid"
    assert config.token == "test_token"
    assert config.host == "https://openspeech.bytedance.com"

def test_get_headers():
    config = Config(
        appid="test_appid",
        token="test_token"
    )
    headers = config.get_headers()
    assert headers["Content-Type"] == "application/json"
    assert headers["Authorization"] == "Bearer;test_token"