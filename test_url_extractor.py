"""测试 URL 提取器的新平台识别功能"""
from backend_watermark.utils.url_extractor import extract_url, detect_platform

# 测试用例
test_cases = [
    {
        'name': '即梦AI - 完整分享文本',
        'text': '看我在即梦发现了什么！棠樱柠发布了一篇AI作品，快来看吧！😆 https://jimeng.jianying.com/s/KloSTWIHQ1Y/?t=210 AA6209，点击链接或复制本条信息，打开【即梦】App查看精彩内容！',
        'expected_platform': 'jimeng'
    },
    {
        'name': 'QQ浏览器 - 视频分享链接',
        'text': 'https://newsa.html5.qq.com/v1/share-video?classify=0&from_app=qb_10&rowkey=42069082915498ah&sGuid=054bbabbd7fc1d03b39a19ca6cd988cb&sUserId=&vid=3786719167628940651&transferInfo=iPraiseIconType%3D0%26shareDesc%3D2%26shareImgUrl%3Dhttp%253A%252F%252Fqqpublic.qpic.cn%252Fqq_public%252F0%252F31-894382974-934CA2FD6C106AF2023250483D188EF6%252F0%253Ffmt%253Djpg%2526size%253D301%2526h%253D1080%2526w%253D1620%2526ppv%253D1%26videoBgColorV2%3D%2523191c24%26videoColorFlag%3D0%26videoHeight%3D1080%26videoNewSubjectPrefix%3D102%26videoTitleColorV2%3D%25239fb4e5%26videoWidth%3D1620&videoBusiType=1',
        'expected_platform': 'qq'
    },
    {
        'name': '抖音 - 短链接',
        'text': '复制这条信息，打开抖音搜索，直接观看视频！https://v.douyin.com/ieFa3DpW/',
        'expected_platform': 'douyin'
    },
    {
        'name': '快手 - 视频链接',
        'text': 'https://www.kuaishou.com/short-video/3x6gzr2nqe4m9aa',
        'expected_platform': 'kuaishou'
    }
]

print("=" * 80)
print("🧪 测试 URL 提取器 - 新平台识别功能")
print("=" * 80)
print()

success_count = 0
fail_count = 0

for i, test_case in enumerate(test_cases, 1):
    print(f"测试 {i}: {test_case['name']}")
    print("-" * 80)
    
    # 提取URL
    extracted_url = extract_url(test_case['text'])
    print(f"📝 输入文本: {test_case['text'][:80]}{'...' if len(test_case['text']) > 80 else ''}")
    print(f"🔗 提取的URL: {extracted_url}")
    
    # 检测平台
    if extracted_url:
        detected_platform = detect_platform(extracted_url)
        print(f"🎯 检测到的平台: {detected_platform}")
        print(f"✅ 预期平台: {test_case['expected_platform']}")
        
        # 验证结果
        if detected_platform == test_case['expected_platform']:
            print("✅ 测试通过！")
            success_count += 1
        else:
            print(f"❌ 测试失败！预期 {test_case['expected_platform']}，实际 {detected_platform}")
            fail_count += 1
    else:
        print("❌ 测试失败！未能提取到URL")
        fail_count += 1
    
    print()

print("=" * 80)
print(f"📊 测试结果汇总")
print("=" * 80)
print(f"✅ 成功: {success_count} 个")
print(f"❌ 失败: {fail_count} 个")
print(f"📈 通过率: {success_count / len(test_cases) * 100:.1f}%")
print()

if fail_count == 0:
    print("🎉 所有测试通过！URL识别功能正常！")
else:
    print(f"⚠️ 有 {fail_count} 个测试失败，请检查配置！")

