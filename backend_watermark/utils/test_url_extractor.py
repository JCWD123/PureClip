"""URL提取功能测试"""
from url_extractor import extract_url, extract_all_urls, is_valid_url, detect_platform


def test_extract_url():
    """测试URL提取功能"""
    
    test_cases = [
        # 格式: (输入, 期望输出, 描述)
        (
            "https://example.com/video.mp4",
            "https://example.com/video.mp4",
            "纯URL"
        ),
        (
            "观看这个视频 https://example.com/video.mp4 很精彩！",
            "https://example.com/video.mp4",
            "带中文的文本"
        ),
        # 真实测试案例1: 抖音
        (
            "1.71 复制打开抖音，看看【小丫头的作品】# # 全民猜歌达人 # 王家驹经典歌曲 # 前奏... https://v.douyin.com/6YWKa6_haf8/ K@j.pd 05/09 Atr:/",
            "https://v.douyin.com/6YWKa6_haf8/",
            "真实抖音分享链接"
        ),
        # 真实测试案例2: 百度
        (
            "【大大阮迪慧的一生之敌】https://mr.baidu.com/r/1Mf25TiaqXu?f=cp&rs=2140313395&ruk=H9L__jwD_3Mko6WfA-nOJA&u=dad868bf9d433114&sid_for_share=184272_3",
            "https://mr.baidu.com/r/1Mf25TiaqXu?f=cp&rs=2140313395&ruk=H9L__jwD_3Mko6WfA-nOJA&u=dad868bf9d433114&sid_for_share=184272_3",
            "真实百度分享链接"
        ),
        # 真实测试案例3: 小红书
        (
            "湖光山色两相宜 http://xhslink.com/o/uMnICz6mL2 \n\n复制后打开【小红书】查看笔记！",
            "http://xhslink.com/o/uMnICz6mL2",
            "真实小红书分享链接"
        ),
        (
            "【抖音】复制此链接 https://v.douyin.com/iRNBho6/ 打开抖音",
            "https://v.douyin.com/iRNBho6/",
            "抖音分享链接"
        ),
        (
            "视频地址：https://example.com/video.mp4，请查收。",
            "https://example.com/video.mp4",
            "带标点符号"
        ),
        (
            "http://www.w3schools.com/html/mov_bbb.mp4",
            "http://www.w3schools.com/html/mov_bbb.mp4",
            "HTTP协议"
        ),
        (
            "链接1 https://url1.com 链接2 https://url2.com",
            "https://url1.com",
            "多个URL（提取第一个）"
        ),
        (
            "这是B站视频 https://www.bilibili.com/video/BV1xx411c7mD 快来看",
            "https://www.bilibili.com/video/BV1xx411c7mD",
            "B站链接"
        ),
        (
            "微信文章 https://mp.weixin.qq.com/s/xxxxxx 分享",
            "https://mp.weixin.qq.com/s/xxxxxx",
            "微信链接"
        ),
        (
            "没有链接的文本",
            None,
            "无URL"
        ),
        (
            "",
            None,
            "空字符串"
        ),
    ]
    
    print("=" * 80)
    print("URL提取功能测试")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for input_text, expected, description in test_cases:
        result = extract_url(input_text)
        success = result == expected
        
        status = "✅ PASS" if success else "❌ FAIL"
        
        print(f"\n{status} - {description}")
        print(f"  输入: {input_text[:60]}{'...' if len(input_text) > 60 else ''}")
        print(f"  期望: {expected}")
        print(f"  结果: {result}")
        
        if success:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 80)


def test_extract_all_urls():
    """测试提取所有URL"""
    
    print("\n\n" + "=" * 80)
    print("提取所有URL测试")
    print("=" * 80)
    
    test_cases = [
        (
            "视频1 https://url1.com 视频2 https://url2.com 图片 https://url3.jpg",
            ["https://url1.com", "https://url2.com", "https://url3.jpg"],
            "多个URL"
        ),
        (
            "https://example.com/video.mp4",
            ["https://example.com/video.mp4"],
            "单个URL"
        ),
        (
            "没有任何链接",
            [],
            "无URL"
        ),
    ]
    
    for input_text, expected, description in test_cases:
        result = extract_all_urls(input_text)
        success = result == expected
        
        status = "✅ PASS" if success else "❌ FAIL"
        
        print(f"\n{status} - {description}")
        print(f"  输入: {input_text}")
        print(f"  期望: {expected}")
        print(f"  结果: {result}")


def test_is_valid_url():
    """测试URL验证"""
    
    print("\n\n" + "=" * 80)
    print("URL验证测试")
    print("=" * 80)
    
    test_cases = [
        ("https://example.com/video.mp4", True, "有效的HTTPS URL"),
        ("http://example.com", True, "有效的HTTP URL"),
        ("ftp://example.com", False, "非HTTP协议"),
        ("example.com", False, "缺少协议"),
        ("https://", False, "不完整的URL"),
        ("", False, "空字符串"),
        (None, False, "None值"),
    ]
    
    for url, expected, description in test_cases:
        result = is_valid_url(url)
        success = result == expected
        
        status = "✅ PASS" if success else "❌ FAIL"
        
        print(f"\n{status} - {description}")
        print(f"  URL: {url}")
        print(f"  期望: {expected}")
        print(f"  结果: {result}")


def test_detect_platform():
    """测试平台检测"""
    
    print("\n\n" + "=" * 80)
    print("平台检测测试")
    print("=" * 80)
    
    test_cases = [
        ("https://v.douyin.com/6YWKa6_haf8/", "douyin", "抖音真实链接"),
        ("https://www.douyin.com/video/xxxx", "douyin", "抖音网页版"),
        ("https://v.kuaishou.com/xxxx", "kuaishou", "快手"),
        ("https://www.bilibili.com/video/BVxxxx", "bilibili", "B站"),
        ("https://b23.tv/xxxx", "bilibili", "B站短链接"),
        ("https://mp.weixin.qq.com/s/xxxx", "weixin", "微信"),
        ("https://www.youtube.com/watch?v=xxxx", "youtube", "YouTube"),
        ("https://youtu.be/xxxx", "youtube", "YouTube短链接"),
        ("https://www.tiktok.com/@user/video/xxxx", "tiktok", "TikTok"),
        ("http://xhslink.com/o/uMnICz6mL2", "xiaohongshu", "小红书真实链接"),
        ("https://mr.baidu.com/r/1Mf25TiaqXu", "baidu", "百度真实链接"),
        ("https://example.com/video.mp4", None, "未知平台"),
    ]
    
    for url, expected, description in test_cases:
        result = detect_platform(url)
        success = result == expected
        
        status = "✅ PASS" if success else "❌ FAIL"
        
        print(f"\n{status} - {description}")
        print(f"  URL: {url}")
        print(f"  期望: {expected}")
        print(f"  结果: {result}")


if __name__ == "__main__":
    # 运行所有测试
    test_extract_url()
    test_extract_all_urls()
    test_is_valid_url()
    test_detect_platform()
    
    print("\n\n" + "=" * 80)
    print("所有测试完成！")
    print("=" * 80)

