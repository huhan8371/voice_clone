import base64
import json
import uuid
from typing import Dict, Any, Optional
import aiohttp
import logging
import ssl
from .config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self, config: Config):
        self.config = config
        # 创建自定义 SSL 上下文
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        
    async def synthesize(
        self,
        text: str,
        speaker_id: str,
        text_type: str = "plain",
        encoding: str = "mp3",
        speed_ratio: float = 1.0,
    ) -> bytes:
        """
        合成语音
        
        Args:
            text: 要转换的文本
            speaker_id: 声音ID（S_开头）
            text_type: 文本类型 (plain/ssml)
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
                "text_type": text_type,
                "operation": "query"
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, 
                                  json=request_data, 
                                  headers=self.config.get_headers(),
                                  ssl=self.ssl_context) as response:
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
        text_type: str = "plain",
        encoding: str = "mp3",
        speed_ratio: float = 1.0,
        _return_response: bool = False
    ) -> Optional[Dict]:
        """
        将文本合成为语音并保存到文件
        
        Args:
            text: 要转换的文本
            output_path: 输出文件路径
            speaker_id: 声音ID
            text_type: 文本类型 (plain/ssml)
            encoding: 音频编码格式
            speed_ratio: 语速
            _return_response: 是否返回响应数据
        """
        try:
            audio_data = await self.synthesize(
                text=text, 
                speaker_id=speaker_id, 
                text_type=text_type,
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
