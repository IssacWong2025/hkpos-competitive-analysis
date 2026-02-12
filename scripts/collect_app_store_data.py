#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
App Store & Google Play 基础数据收集脚本
收集香港餐饮 POS 竞品的应用商店基础信息
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
COMPETITOR_CSV = "market_research/data/competitor_apps.csv"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
}

# ===============
def load_competitors():
    """从 CSV 加载竞品列表"""
    csv_path = Path(COMPETITOR_CSV)

    if not csv_path.exists():
        print(f"✗ 警告：找不到 {COMPETITOR_CSV}")
        return []

    competitors = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['竞品中文名']:
                competitors.append({
                    'name_cn': row['竞品中文名'],
                    'name_en': row['竞品英文名'],
                    'app_store_name': row['App Store名称'],
                    'bundle_id': row['App Store Bundle ID'],
                    'google_play_pkg': row['Google Play包名']
                })

    print(f"✓ 成功加载 {len(competitors)} 家竞品")
    return competitors

def fetch_app_store_info(bundle_id):
    """获取 App Store 信息（使用 iTunes Search API）"""
    if not bundle_id:
        return None

    try:
        # iTunes Search API
        url = f"https://itunes.apple.com/hk/lookup?bundleId={bundle_id}"
        response = requests.get(url, headers=HEADERS, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get('resultCount', 0) > 0:
                app_data = data['results'][0]
                return {
                    'platform': 'App Store',
                    'bundle_id': bundle_id,
                    'app_name': app_data.get('trackName', ''),
                    'developer': app_data.get('artistName', ''),
                    'version': app_data.get('version', ''),
                    'current_version_release_date': app_data.get('currentVersionReleaseDate', ''),
                    'rating': app_data.get('averageUserRating', 0),
                    'rating_count': app_data.get('userRatingCount', 0),
                    'price': app_data.get('price', 0),
                    'genre': app_data.get('genres', [''])[0] if app_data.get('genres') else '',
                    'description': app_data.get('description', '')[:500],  # 前500字符
                    'supported_devices': app_data.get('supportedDevices', []),
                    'release_date': app_data.get('releaseDate', ''),
                    'screenshot_urls': ', '.join(app_data.get('screenshotUrls', [])),
                    'icon_url': app_data.get('artworkUrl100', ''),
                    'track_view_url': app_data.get('trackViewUrl', ''),
                    'status': 'success'
                }
            else:
                return {
                    'platform': 'App Store',
                    'bundle_id': bundle_id,
                    'status': 'not_found',
                    'error': 'App not found in App Store'
                }
        else:
            return {
                'platform': 'App Store',
                'bundle_id': bundle_id,
                'status': 'http_error',
                'error': f'HTTP {response.status_code}'
            }
    except Exception as e:
        return {
            'platform': 'App Store',
            'bundle_id': bundle_id,
            'status': 'error',
            'error': str(e)
        }

def fetch_google_play_info(package_name):
    """获取 Google Play 信息（使用第三方API或爬虫）"""
    if not package_name:
        return None

    # 注意：Google Play没有官方公开API，需要使用第三方服务或爬虫
    # 这里先返回待处理标记，后续可以用 google-play-scraper 库
    return {
        'platform': 'Google Play',
        'package_name': package_name,
        'status': 'pending',
        'error': 'Google Play scraping not implemented - need manual collection or third-party API'
    }

def collect_store_data(competitors):
    """收集所有竞品的应用商店数据"""
    results = []

    for comp in competitors:
        name_cn = comp['name_cn']
        name_en = comp['name_en']
        bundle_id = comp['bundle_id']
        google_play_pkg = comp['google_play_pkg']
        app_store_name = comp['app_store_name']

        print(f"\n{'='*60}")
        print(f"正在查询: {name_cn} ({name_en})")
        print(f"  Bundle ID: {bundle_id if bundle_id else 'N/A'}")
        print(f"  Google Play: {google_play_pkg if google_play_pkg else 'N/A'}")

        # 收集 App Store 数据
        if bundle_id:
            print(f"  → 查询 App Store...")
            app_store_data = fetch_app_store_info(bundle_id)

            # 合并数据
            result = {
                '竞品中文名': name_cn,
                '竞品英文名': name_en,
                'App Store显示名称': app_store_name,
                **app_store_data
            }

            # 添加 Google Play 数据
            if google_play_pkg:
                print(f"  → 查询 Google Play...")
                gp_data = fetch_google_play_info(google_play_pkg)
                result['gp_status'] = gp_data.get('status')
                result['gp_error'] = gp_data.get('error')
            else:
                result['gp_status'] = 'N/A'
                result['gp_error'] = ''

            results.append(result)
            print(f"  ✓ App Store: {app_store_data.get('status', 'unknown')}")
        else:
            print(f"  ✗ 跳过：无 Bundle ID")
            results.append({
                '竞品中文名': name_cn,
                '竞品英文名': name_en,
                'App Store显示名称': app_store_name,
                'platform': 'App Store',
                'status': 'skipped',
                'error': 'No Bundle ID'
            })

        # 延迟避免被限制
        time.sleep(1)

    return results

def save_to_excel(results, filename):
    """保存结果到 Excel"""
    try:
        df = pd.DataFrame(results)

        # 确保 data 目录存在
        output_path = Path("market_research/data")
        output_path.mkdir(parents=True, exist_ok=True)

        # 保存
        filepath = output_path / filename
        df.to_excel(filepath, index=False, engine='openpyxl')

        print(f"\n✓ 数据已保存到: {filepath}")
        print(f"  共 {len(results)} 条记录")
        return True

    except Exception as e:
        print(f"\n✗ 保存失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("App Store & Google Play 基础数据收集工具")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 加载竞品列表
    print("\n正在加载竞品列表...")
    competitors = load_competitors()

    if not competitors:
        print("\n✗ 错误: 竞品列表为空")
        return

    # 开始收集数据
    print("\n开始收集应用商店数据...")
    results = collect_store_data(competitors)

    # 保存结果
    timestamp = datetime.now().strftime('%Y%m%d')
    output_file = f"app_store_basic_data_{timestamp}.xlsx"
    success = save_to_excel(results, output_file)

    print("\n" + "=" * 60)
    print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if success:
        print(f"\n✓ 输出文件: market_research/data/{output_file}")
        print(f"  共收集 {len(results)} 条记录")

        # 统计成功数量
        success_count = sum(1 for r in results if r.get('status') == 'success')
        print(f"  App Store 成功: {success_count}/{len(results)}")
    else:
        print("\n部分数据可能未保存")

    print("\n提示: 请检查 market_research/data/ 目录查看生成的文件")

if __name__ == "__main__":
    main()
