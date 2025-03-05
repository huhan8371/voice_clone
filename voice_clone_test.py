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
        
        # 确保输出目录存在
        os.makedirs("output", exist_ok=True)
        
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
    
    async def synthesize_speech(self):
        """合成语音"""
        print("\n=== 合成语音 ===")
        # print(f"使用音色ID: {self.speaker_id}")
            
        # 首先检查音色状态
        try:
            status = await self.voice_cloning.get_status(self.speaker_id)
            status_code = status.get('status')
            if status_code not in (2, 4):
                print("错误: 该音色尚未训练完成或不可用！")
                return
            print(f"音色状态: {self.status_map.get(status_code, '未知')}")
        except Exception as e:
            print(f"检查音色状态失败: {str(e)}")
            return
            
        while True:
            # 从input.txt文件读取文本
            try:
                if not os.path.exists('input.txt'):
                    print("错误: input.txt 文件不存在！")
                    return
                    
                with open('input.txt', 'r', encoding='utf-8') as f:
                    text = f.read().strip()
                    
                if not text:
                    print("错误: input.txt 文件为空！")
                    return
                    
                # 检查文本字节长度
                text_bytes = len(text.encode('utf-8'))
                print(f"\n待合成文本的字节长度: {text_bytes}")
                    
                if text_bytes > 1024:
                    print("错误: 文本长度超过1024字节限制，请减少input.txt中的文本内容！")
                    return
                    
                print(f"\n待合成文本内容:\n{text}")
                break
            except Exception as e:
                print(f"读取文件失败: {str(e)}")
                return
            
        while True:
            speed = input("\n请输入语速(0.2-3.0，默认1.0): ").strip() or "1.0"
            try:
                speed_ratio = float(speed)
                if not 0.2 <= speed_ratio <= 3.0:
                    print("错误: 语速必须在0.2到3.0之间！")
                    continue
                break
            except ValueError:
                print("错误: 请输入有效的数字！")
                continue

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
            
            # 生成带时间戳的文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"output/{prefix}_{timestamp}.mp3"
            
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