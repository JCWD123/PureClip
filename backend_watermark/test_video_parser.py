"""视频解析器测试脚本"""
import sys
import logging
from services.video_parser import get_video_parser

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_parser():
    """测试视频解析器"""
    
    test_urls = [
        # 百度链接
        "https://mr.baidu.com/r/1Mf25TiaqXu?f=cp&rs=2140313395&ruk=H9L__jwD_3Mko6WfA-nOJA&u=dad868bf9d433114&sid_for_share=184272_3",
        
        # 抖音链接
        "https://v.douyin.com/6YWKa6_haf8/",
        
        # 小红书链接
        "http://xhslink.com/o/uMnICz6mL2",
        
        # 直接视频链接
        "https://www.w3schools.com/html/mov_bbb.mp4",
        
        # B站短链
        "https://b23.tv/abc123",
    ]
    
    parser = get_video_parser()
    
    print("="*80)
    print("视频解析器测试")
    print("="*80)
    print()
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n测试 {i}/{len(test_urls)}")
        print(f"原始URL: {url}")
        print("-"*80)
        
        try:
            result = parser.parse(url)
            
            if result['success']:
                print("✅ 解析成功!")
                print(f"   真实URL: {result['video_url']}")
                print(f"   标题: {result.get('title', 'N/A')}")
                print(f"   作者: {result.get('author', 'N/A')}")
                print(f"   平台: {result.get('platform', 'N/A')}")
            else:
                print("⚠️ 解析失败")
                print(f"   错误: {result.get('error', 'Unknown')}")
                print(f"   将使用原始URL: {result['video_url']}")
                
        except Exception as e:
            print(f"❌ 异常: {e}")
    
    print("\n" + "="*80)
    print("测试完成")
    print("="*80)

if __name__ == "__main__":
    test_parser()



