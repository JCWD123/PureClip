"""天气爬虫工具"""
import requests
from bs4 import BeautifulSoup
import logging
import pandas as pd
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class WeatherCrawler:
    """天气爬虫类"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # 加载城市代码映射
        self.city_codes = self._load_city_codes()
    
    def _load_city_codes(self) -> dict:
        """从CSV文件加载城市代码映射"""
        try:
            # CSV文件路径
            csv_path = Path(__file__).parent.parent.parent.parent / "中国天气城市地区编号代码 最新地级市(358).csv"
            
            # 尝试不同的编码读取CSV
            for encoding in ['gbk', 'gb18030', 'utf-8']:
                try:
                    df = pd.read_csv(csv_path, encoding=encoding)
                    # 假设列名为: 站点编号,区县,地区/县,市,省,是否省会城市
                    # 创建城市名到代码的映射
                    city_codes = {}
                    for _, row in df.iterrows():
                        try:
                            city_code = str(row.iloc[0])  # 第一列是代码
                            city_name = str(row.iloc[3])  # 第四列是市名
                            if city_name and city_code:
                                city_codes[city_name] = city_code
                        except:
                            continue
                    
                    if city_codes:
                        logger.info(f"成功加载 {len(city_codes)} 个城市代码")
                        return city_codes
                except UnicodeDecodeError:
                    continue
            
            logger.warning("无法读取城市代码CSV文件，使用默认代码")
        except Exception as e:
            logger.error(f"加载城市代码文件失败: {e}")
        
        # 返回默认的城市代码映射
        return {
        }
    
    def get_city_code(self, city: str) -> str:
        """获取城市代码"""
        return self.city_codes.get(city, None)
    
    def crawl_weather(self, province: str, city: str) -> dict:
        """
        爬取指定城市的天气信息
        
        Args:
            province: 省份
            city: 城市
            
        Returns:
            天气信息字典
        """
        try:
            city_code = self.get_city_code(city)
            if not city_code:
                logger.error(f"未找到城市 {city} 的代码")
                return {
                    "city": city,
                    "error": f"未找到城市 {city} 的天气代码，请修改城市名称。支持的城市请参考配置。"
                }
            
            # 使用中国天气网
            url = f"http://www.weather.com.cn/weather/{city_code}.shtml"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                logger.error(f"天气爬取失败，状态码：{response.status_code}")
                return {
                    "city": city,
                    "error": f"无法获取 {city} 的天气信息，请稍后重试。"
                }
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找天气列表
            weather_ul = soup.find('ul', class_='t clearfix')
            if not weather_ul:
                logger.error(f"未找到天气数据: {city}")
                return {
                    "city": city,
                    "error": f"未能爬取到 {city} 的天气信息，网页结构可能已变化。"
                }
            
            # 获取今天的天气（第一个li）
            today_weather = weather_ul.find('li')
            if not today_weather:
                return {
                    "city": city,
                    "error": f"未能解析 {city} 的天气数据。"
                }
            
            # 解析天气信息
            try:
                date = today_weather.find('h1').text.strip()
                weather = today_weather.find('p', class_='wea').text.strip()
                
                # 解析温度
                tem_tag = today_weather.find('p', class_='tem')
                if tem_tag.find('span'):
                    temp_high = tem_tag.find('span').text.strip()
                    temp_low = tem_tag.find('i').text.strip()
                    temperature = f"{temp_low}~{temp_high}"
                else:
                    temperature = tem_tag.find('i').text.strip()
                
                # 解析风向
                wind_spans = today_weather.find('p', class_='win').find('em').find_all('span')
                wind_dir = '/'.join([span.get('title', '') for span in wind_spans])
                
                # 解析风力
                wind_force = today_weather.find('p', class_='win').find('i').text.strip()
                wind = f"{wind_dir} {wind_force}"
                
                weather_info = {
                    "city": city,
                    "date": date,
                    "temperature": temperature,
                    "weather": weather,
                    "wind": wind,
                }
                
                logger.info(f"成功爬取 {city} 天气信息: {weather} {temperature}")
                return weather_info
                
            except Exception as parse_error:
                logger.error(f"解析天气数据失败: {parse_error}")
                return {
                    "city": city,
                    "error": f"解析 {city} 天气数据时出错。"
                }
            
        except Exception as e:
            logger.error(f"爬取天气信息失败: {e}")
            return {
                "city": city,
                "error": f"获取 {city} 天气信息失败: {str(e)}"
            }
    


# 全局天气爬虫实例
weather_crawler = WeatherCrawler()


