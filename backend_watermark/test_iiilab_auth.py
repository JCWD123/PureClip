"""测试 iiilab API 凭证是否有效"""
import requests
import json

# 从配置文件读取
from config.config import settings

print("="*80)
print("iiilab API 凭证测试")
print("="*80)

print(f"\n📋 当前配置:")
print(f"   API URL: {settings.IIILAB_API_URL}")
print(f"   Client ID: {settings.IIILAB_CLIENT_ID}")
print(f"   Client Secret: {settings.IIILAB_CLIENT_SECRET}")
print(f"   Timeout: {settings.IIILAB_TIMEOUT}")

print("\n" + "="*80)
print("开始测试...")
print("="*80)

# 测试1: 使用简单的公开URL
test_url = "https://www.w3schools.com/html/mov_bbb.mp4"

headers = {
    "x-client-id": settings.IIILAB_CLIENT_ID,
    "x-client-secret": settings.IIILAB_CLIENT_SECRET,
    "Content-Type": "application/json",
    "Accept": "application/json"
}

data = {"url": test_url}

print(f"\n📤 发送请求:")
print(f"   URL: {settings.IIILAB_API_URL}")
print(f"   Method: POST")
print(f"   Headers: {json.dumps({k: v[:20]+'...' if len(v) > 20 else v for k, v in headers.items()}, indent=6)}")
print(f"   Data: {data}")

try:
    response = requests.post(
        settings.IIILAB_API_URL,
        headers=headers,
        json=data,
        timeout=30
    )
    
    print(f"\n📥 响应:")
    print(f"   状态码: {response.status_code}")
    print(f"   响应头: {dict(response.headers)}")
    
    try:
        result = response.json()
        print(f"   响应体: {json.dumps(result, indent=6, ensure_ascii=False)}")
    except:
        print(f"   响应体 (文本): {response.text[:500]}")
    
    if response.status_code == 200:
        print("\n✅ 测试成功！API凭证有效！")
        
        # 测试2: 使用百度短链
        print("\n" + "="*80)
        print("测试百度短链...")
        print("="*80)
        
        baidu_url = "https://mr.baidu.com/r/1Mf25TiaqXu?f=cp&rs=2140313395&ruk=H9L__jwD_3Mko6WfA-nOJA&u=dad868bf9d433114&sid_for_share=184272_3"
        data2 = {"url": baidu_url}
        
        response2 = requests.post(
            settings.IIILAB_API_URL,
            headers=headers,
            json=data2,
            timeout=30
        )
        
        print(f"\n📥 响应:")
        print(f"   状态码: {response2.status_code}")
        
        if response2.status_code == 200:
            result2 = response2.json()
            print(f"   响应: {json.dumps(result2, indent=6, ensure_ascii=False)}")
            print("\n✅ 百度链接解析测试成功！")
        else:
            print(f"   错误: {response2.text}")
            print("\n⚠️ 百度链接解析失败（可能不支持该平台）")
            
    elif response.status_code == 401:
        print("\n❌ 认证失败！")
        print("\n可能的原因:")
        print("1. client_id 或 client_secret 错误")
        print("2. 凭证已过期")
        print("3. 账号状态异常")
        print("\n建议:")
        print("1. 重新检查 config.yaml 中的 client_id 和 client_secret")
        print("2. 确认凭证是否完整（没有多余的空格或引号）")
        print("3. 登录 iiilab 官网确认账号状态")
        print("4. 重新生成新的凭证")
    else:
        print(f"\n❌ 请求失败！状态码: {response.status_code}")
        print(f"错误信息: {response.text}")
        
except requests.exceptions.Timeout:
    print("\n❌ 请求超时！")
    print("可能的原因:")
    print("1. 网络连接问题")
    print("2. API服务器响应慢")
    
except Exception as e:
    print(f"\n❌ 异常: {e}")
    import traceback
    print("\n详细错误:")
    traceback.print_exc()

print("\n" + "="*80)
print("测试完成")
print("="*80)

