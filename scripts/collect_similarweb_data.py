#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SimilarWeb Batch Data Collection Script (Full Cookie JSON Format)
Collects market data for Hong Kong restaurant POS competitors
"""

import requests
import json
import csv
import sys
import time
import pandas as pd
from pathlib import Path
from datetime import datetime
import io

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ================
SIMILARWEB_BASE = "https://similarweb.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9"
}

# ===============
COOKIE_FILE = "cookies.json"
COMPETITOR_CSV = "market_research/data/competitor_apps.csv"

# ===============
def load_cookies(cookie_file):
    """加载完整的 Cookie JSON 文件"""
    try:
        with open(cookie_file, 'r', encoding='utf-8') as f:
            cookies_data = json.load(f)
        print(f"✓ 成功读取 {len(cookies_data)} 个 Cookie")
        return cookies_data
    except FileNotFoundError:
        print(f"✗ 错误：找不到文件 {cookie_file}")
        return {}
    except json.JSONDecodeError as e:
        print(f"✗ JSON 解析错误: {str(e)}")
        return {}

def load_competitors():
    """从 CSV 加载竞品列表"""
    csv_path = Path(COMPETITOR_CSV)

    if not csv_path.exists():
        print("✗ 警告：找不到 {COMPETITOR_CSV}")
        return []

    competitors = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['竞品中文名']:
                website = row['官网URL']
                domain = extract_domain(website)
                competitors.append({
                    'name_cn': row['竞品中文名'],
                    'name_en': row['竞品英文名'],
                    'app_store': row['App Store名称'],
                    'bundle_id': row['App Store Bundle ID'],
                    'website': website,
                    'linkedin': row['LinkedIn URL'],
                    'facebook': row['Facebook Page URL'],
                    'domain': domain,
                    'similarweb_url': f"{SIMILARWEB_BASE}/website/{domain}"
                })

    print(f"✓ 成功加载 {len(competitors)} 家竞品")
    return competitors

def extract_domain(url):
    """从 URL 中提取域名"""
    if not url or url == 'N/A':
        return ''

    # 移除协议和www
    url = url.replace('https://', '').replace('http://', '').replace('www.', '')

    # 移除路径和端口号
    domain = url.split('/')[0]

    return domain

def get_headers(cookies_dict):
    """从 Cookie 字典设置请求头"""
    headers = HEADERS.copy()

    # 只处理 domain=.similarweb.com 的 cookies
    cookie_pairs = []
    for cookie in cookies_dict:
        if cookie.get('domain') in ['.similarweb.com', 'similarweb.com']:
            # 收集所有 SimilarWeb cookies
            cookie_pairs.append(f"{cookie['name']}={cookie['value']}")

    # 组装 Cookie header
    if cookie_pairs:
        headers['Cookie'] = '; '.join(cookie_pairs)

    return headers

def fetch_similarweb_data(domain, cookies_dict, competitors):
    """获取 SimilarWeb 数据"""
    results = []

    for comp in competitors:
        name = comp['name_en']
        similarweb_url = comp['similarweb_url']
        comp_domain = comp['domain']

        print(f"\n{'='*60}")
        print(f"正在查询: {name}")
        print(f"域名: {comp_domain}")
        print(f"URL: {similarweb_url}")

        # 设置请求头
        headers = get_headers(cookies_dict)

        try:
            # Desktop Traffic
            response = requests.get(f"{similarweb_url}?tab=overview/overview/desktop",
                                  headers=headers, timeout=30)

            if response.status_code == 200:
                print(f"✓ 请求成功 (状态码: {response.status_code})")

                # 解析 HTML 提取数据
                # 这里后续需要解析 HTML 提取：
                # - 总访问量
                # - 排名
                # - 关键词

                # 临时保存 HTML 用于调试
                data = {
                    '竞品': name,
                    '竞品英文名': name,
                    '域名': comp_domain,
                    '官网': comp['website'],
                    'SimilarWeb URL': similarweb_url,
                    '状态码': response.status_code,
                    '查询时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

                # 保存 HTML
                save_html(response, similarweb_url, name)

            else:
                print(f"✗ 请求失败 (状态码: {response.status_code})")
                data = {
                    '竞品': name,
                    '竞品英文名': name,
                    '域名': comp_domain,
                    '官网': comp['website'],
                    'SimilarWeb URL': similarweb_url,
                    '状态码': response.status_code,
                    '错误信息': f"HTTP {response.status_code}",
                    '查询时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

        except Exception as e:
            print(f"✗ 请求异常: {str(e)}")
            data = {
                '竞品': name,
                '竞品英文名': name,
                '域名': comp_domain,
                '官网': comp['website'],
                'SimilarWeb URL': similarweb_url,
                '状态码': 'ERROR',
                '错误信息': str(e),
                '查询时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

        # 延迟避免被限制
        time.sleep(2)

        results.append(data)

    return results

def save_html(response, url, name):
    """保存 HTML 用于调试"""
    safe_name = name.replace('/', '_').replace(' ', '_')
    filename = Path(f"market_research/charts/html_{safe_name}.html")

    # 确保目录存在
    filename.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"✓ HTML 已保存: {filename}")
    except Exception as e:
        print(f"✗ 保存失败: {str(e)}")

def save_to_excel(results, filename):
    """保存结果到 Excel"""
    try:
        df = pd.DataFrame(results)

        # 确保 data 目录存在
        output_path = Path("market_research/data")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 保存
        filepath = output_path / filename
        df.to_excel(filepath, index=False, engine='openpyxl')

        print(f"✓ 数据已保存到: {filepath}")
        print(f"  共 {len(results)} 条记录")
        return True

    except Exception as e:
        print(f"✗ 保存失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("SimilarWeb 批量数据收集工具")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 检查命令行参数
    if len(sys.argv) > 1:
        cookie_file = sys.argv[1]
    else:
        print("\n✗ 错误: 缺少 cookies 文件参数")
        print("\n用法: python collect_similarweb_data.py cookies.json")
        return

    # 加载 Cookies
    print(f"\n正在读取 Cookies: {cookie_file}")
    cookies = load_cookies(cookie_file)

    if not cookies:
        print("\n✗ 错误: 读取失败或格式错误")
        return

    # 统计 SimilarWeb cookies
    similarweb_cookies = [c for c in cookies if c.get('domain') == '.similarweb.com']
    print(f"✓ 找到 {len(similarweb_cookies)} 个 SimilarWeb Cookie")

    # 加载竞品列表
    print("\n正在加载竞品列表...")
    competitors = load_competitors()

    if not competitors:
        print("\n✗ 错误: 竞品列表为空")
        return

    print(f"✓ 成功加载 {len(competitors)} 家竞品")

    # 开始收集数据
    print("\n开始收集 SimilarWeb 数据...")
    results = fetch_similarweb_data(extract_domain(competitors[0]['website']), cookies, competitors)

    # 保存结果
    timestamp = datetime.now().strftime('%Y%m%d')
    output_file = f"similarweb_data_{timestamp}.xlsx"
    success = save_to_excel(results, output_file)

    print("=" * 60)
    print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if success:
        print(f"\n✓ 输出文件: market_research/data/{output_file}")
        print(f"\n 共收集 {len(results)} 条记录")
    else:
        print("\n部分数据可能未保存")

    print("\n提示: 请检查 market_research/data/ 目录查看生成的文件")
    print("\n下次运行使用: python collect_similarweb_data.py cookies.json")

if __name__ == "__main__":
    main()
