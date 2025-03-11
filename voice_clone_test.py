import asyncio
import os
import logging
from datetime import datetime
from core import Config, VoiceCloningService, TTSService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VoiceCloneTest:
    # 状态码映射
    status_map = {
        0: "未找到",
        1: "训练中",
        2: "训练成功",
        3: "训练失败",
        4: "已激活"
    }

    def __init__(self):
        # 获取用户输入的配置
        print("\n=== 配置字节跳动API ===")
        appid = input("请输入BYTEDANCE_APPID: ").strip()
        if not appid:
            raise ValueError("BYTEDANCE_APPID 不能为空")
            
        token = input("请输入BYTEDANCE_TOKEN: ").strip()
        if not token:
            raise ValueError("BYTEDANCE_TOKEN 不能为空")
            
        speaker_id = input("请输入音色ID: ").strip()
        if not speaker_id:
            raise ValueError("音色ID 不能为空")
        if not speaker_id.startswith("S_"):
            raise ValueError("音色ID必须以'S_'开头")
            
        # 保存配置
        self.speaker_id = speaker_id
        
        # 创建配置
        self.config = Config(
            appid=appid,
            token=token
        )
        
        # 初始化服务
        self.voice_cloning = VoiceCloningService(self.config)
        self.tts = TTSService(self.config)
        
        print("\n配置完成！")
    
    async def check_status(self):
        """查询训练状态"""
        print("\n=== 查询训练状态 ===")
        print(f"查询音色ID: {self.speaker_id}")
        
        try:
            status = await self.voice_cloning.get_status(self.speaker_id)
            print("\n训练状态:")
            print(f"音色ID: {status.get('speaker_id')}")
            
            status_code = status.get('status')
            print(f"状态: {self.status_map.get(status_code, '未知')}")
            
            if status.get('demo_audio'):
                print(f"示例音频: {status.get('demo_audio')}")
                
        except Exception as e:
            print(f"\n查询状态失败: {str(e)}")
    
    def get_text_content(self) -> str:
        """获取要转换的文本内容"""
        print("\n请选择文本输入方式：")
        print("1. 直接输入文本")
        print("2. 从文件读取")
        
        choice = input("请选择 (1/2): ").strip()
        
        if choice == "1":
            return input("\n请输入要转换的文本: ").strip()
        elif choice == "2":
            file_path = input("\n请输入文本文件路径: ").strip()
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            except Exception as e:
                print(f"\n读取文件失败: {str(e)}")
                return ""
        else:
            print("\n无效的选择！")
            return ""

    async def synthesize_speech(self):
        """合成语音"""
        print("\n=== 合成语音 ===")
        
        # 添加是否显示报文的选项
        show_request = input("\n是否显示请求和响应报文 (y/n): ").strip().lower() == 'y'
    
        # 获取文本内容
        text = self.get_text_content()
        if not text:
            return
    
        # 获取输出信息
        prefix = input("\n请输入音频文件名前缀: ").strip()
        output_dir = input("请输入保存目录路径: ").strip()
        
        # 固定语速为 1.0
        speed_ratio = 1.0
        print("\n使用默认语速: 1.0")
    
        while True:
            prefix = input("\n请输入音频文件名前缀: ").strip()
            if not prefix:
                print("错误: 请提供文件名前缀！")
                continue
            if len(prefix) > 50:  # 添加前缀长度限制
                print("错误: 文件名前缀太长，请限制在50个字符以内！")
                continue
            break
            
        try:
            
            while True:
                # 获取用户输入的保存路径
                save_dir = input("\n请输入保存目录路径: ").strip()
                if not save_dir:
                    print("错误: 保存目录路径不能为空！")
                    continue
                
                try:
                    # 确保目录存在
                    os.makedirs(save_dir, exist_ok=True)
                    
                    # 检查目录是否可写
                    if not os.access(save_dir, os.W_OK):
                        print(f"错误: 没有权限写入目录 {save_dir}")
                        continue
                        
                    # 生成带时间戳的文件名
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_path = os.path.join(save_dir, f"{prefix}_{timestamp}.mp3")
                    break
                except Exception as e:
                    print(f"错误: 创建保存目录失败: {str(e)}")
                    continue
            
            print("\n正在合成语音...")
            await self.tts.synthesize_to_file(
                text=text,
                output_path=output_path,
                speaker_id=self.speaker_id,
                speed_ratio=speed_ratio
            )
            print(f"语音已保存到: {output_path}")
            
        except ValueError:
            print("错误: 语速必须是有效的数字！")
        except Exception as e:
            print(f"\n合成语音失败: {str(e)}")

async def main():
    demo = VoiceCloneTest()
    
    while True:
        print("\n============= 声音复刻测试程序 =============")
        print("1. 查询训练状态")
        print("2. 合成语音（文本转语音）")
        print("0. 退出程序")
        print("===========================================")
        
        try:
            choice = input("\n请选择功能 (0-2): ").strip()
            
            if choice == "1":
                await demo.check_status()
            elif choice == "2":
                await demo.synthesize_speech()
            elif choice == "0":
                print("\n感谢使用！再见！")
                return  # 直接返回退出程序
            else:
                print("\n无效的选择，请输入0-2之间的数字。")
            
            if choice in ["1", "2"]:  # 只在执行功能后等待
                input("\n按Enter键继续...")
        except KeyboardInterrupt:
            print("\n\n程序已被用户中断")
            return

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序已被用户中断")
    except Exception as e:
        print(f"\n程序执行出错: {str(e)}")
        logger.exception("程序异常")