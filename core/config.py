from dataclasses import dataclass

@dataclass
class Config:
    appid: str
    token: str
    host: str = "https://openspeech.bytedance.com"
    tts_cluster: str = "volcano_icl"  # 或 volcano_icl_concurr
    resource_id: str = "volc.megatts.voiceclone"

    def get_headers(self, use_resource_id: bool = False) -> dict:
        """获取API请求头"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer;{self.token}"
        }
        
        if use_resource_id:
            headers["Resource-Id"] = self.resource_id
            
        return headers