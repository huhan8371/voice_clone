import asyncio
import base64
import os
import ssl
from typing import Dict, Any
import aiohttp
import logging
from .config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceCloningService:
    def __init__(self, config: Config):
        self.config = config
        
    async def encode_audio_file(self, file_path: str) -> tuple[str, str]:
        """将音频文件编码为base64格式"""
        with open(file_path, 'rb') as audio_file:
            audio_data = audio_file.read()
            encoded_data = base64.b64encode(audio_data).decode('utf-8')
            audio_format = os.path.splitext(file_path)[1][1:]  # 获取文件扩展名
            return encoded_data, audio_format
    
    async def train(self, audio_path: str, speaker_id: str) -> Dict[str, Any]:
        """
        上传音频并开始训练
        
        Args:
            audio_path: 音频文件路径
            speaker_id: 声音ID
        """
        url = f"{self.config.host}/api/v1/mega_tts/audio/upload"
        
        # 准备请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer;{self.config.token}",
            "Resource-Id": "volc.megatts.voiceclone"
        }
        
        # 编码音频文件
        encoded_data, audio_format = await self.encode_audio_file(audio_path)
        
        # 准备请求数据
        data = {
            "appid": self.config.appid,
            "speaker_id": speaker_id,
            "audios": [{
                "audio_bytes": encoded_data,
                "audio_format": audio_format
            }],
            "source": 2,
            "language": 0,  # 默认中文
            "model_type": 1  # 使用2.0效果
        }
        
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(url, json=data, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"训练请求错误: {error_text}")
                
                return await response.json()
    
    async def get_status(self, speaker_id: str) -> Dict[str, Any]:
        """获取训练状态"""
        url = f"{self.config.host}/api/v1/mega_tts/status"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer;{self.config.token}",
            "Resource-Id": "volc.megatts.voiceclone"
        }
        
        data = {
            "appid": self.config.appid,
            "speaker_id": speaker_id
        }
        
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(url, json=data, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"状态查询失败: {error_text}")
                
                return await response.json()
    
    async def wait_for_completion(self, speaker_id: str, timeout: int = 3600) -> Dict[str, Any]:
        """
        等待训练完成
        
        Args:
            speaker_id: 声音ID
            timeout: 超时时间（秒）
        """
        start_time = asyncio.get_event_loop().time()
        
        while True:
            status = await self.get_status(speaker_id)
            
            # 状态：0=未找到, 1=训练中, 2=成功, 3=失败, 4=激活
            if status["status"] in (2, 4):  # Success or Active
                return status
            elif status["status"] == 3:  # Failed
                raise Exception(f"训练失败: {status}")
            
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise TimeoutError("训练超时")
            
            await asyncio.sleep(10)  # 每10秒检查一次

    async def train_and_wait(self, audio_path: str, speaker_id: str) -> Dict[str, Any]:
        """上传音频、开始训练并等待完成"""
        await self.train(audio_path, speaker_id)
        return await self.wait_for_completion(speaker_id)