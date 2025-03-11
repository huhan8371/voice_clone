import base64
import json
import uuid
from typing import Dict, Any, Optional
import aiohttp
import logging
from .config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self, config: Config):
        self.config = config
        
    async def synthesize(
        self,
        text: str,
        speaker_id: str,
        encoding: str = "mp3",
        speed_ratio: float = 1.0,
    ) -> bytes:
        """
        合成语音
        
        Args:
            text: 要转换的文本
            speaker_id: 声音ID（S_开头）
            encoding: 音频编码格式 (wav/pcm/ogg_opus/mp3)
            speed_ratio: 语速 [0.2-3.0]
            
        Returns:
            bytes: 音频数据
        """
        url = f"{self.config.host}/api/v1/tts"
        
        request_data = {
            "app": {
                "appid": self.config.appid,
                "token": self.config.token,
                "cluster": self.config.tts_cluster
            },
            "user": {
                "uid": str(uuid.uuid4())
            },
            "audio": {
                "voice_type": speaker_id,
                "encoding": encoding,
                "speed_ratio": speed_ratio
            },
            "request": {
                "reqid": str(uuid.uuid4()),
                "text": text,
                "text_type": "plain",
                "operation": "query"
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=request_data, headers=self.config.get_headers()) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"语音合成失败: {error_text}")
                
                result = await response.json()
                
                if result.get("code") != 3000:
                    raise Exception(f"语音合成错误: {result.get('message')}")
                
                if "data" not in result:
                    raise Exception("响应中没有音频数据")
                
                return base64.b64decode(result["data"])
    
    async def synthesize_to_file(
        self,
        text: str,
        output_path: str,
        speaker_id: str,
        encoding: str = "mp3",
        speed_ratio: float = 1.0,
        _return_response: bool = False
    ) -> Optional[Dict]:
        """
        将文本合成为语音并保存到文件
        """
        try:
            audio_data = await self.synthesize(
                text=text, 
                speaker_id=speaker_id, 
                encoding=encoding,
                speed_ratio=speed_ratio
            )
            
            import os
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(audio_data)
            
            logger.info(f"语音已保存到: {output_path}")
            
            if _return_response:
                return {"code": 0, "message": "success", "data": {"audio": audio_data}}
                
        except Exception as e:
            logger.error(f"合成失败: {str(e)}")
            raise