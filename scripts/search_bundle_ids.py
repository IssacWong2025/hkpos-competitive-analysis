#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动搜索 Bundle ID 的辅助脚本
"""
import requests
import csv
import sys
import io

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 竞品列表及可能的关键词
competitors = [
    {'name_cn': 'Tappo', 'keywords': ['Gotappo', 'Tappo', 'gotappo']},
    {'name_cn': 'Eats365', 'keywords': ['Eats365', 'Eats365 POS']},
    {'name_cn': 'OmniWe', 'keywords': ['OmniWe', 'OmniWe POS']},
    {'name_cn': 'ROKA', 'keywords': ['eMenu', 'ROKA', 'roka']},
    {'name_cn': 'ezPOS', 'keywords': ['ezPOS', 'Catch Gold']},
    {'name_cn': 'iCHEF', 'keywords': ['iCHEF', 'i-chef']},
    {'name_cn': 'DimPOS', 'keywords': ['DimPOS', 'Dimorder']},
    {'name_cn': 'HCTC', 'keywords': ['HCTC', 'posapp']},
    {'name_cn': 'Caterlord', 'keywords': ['Caterlord', 'Caterlord POS']},
    {'name_cn': 'DoLA', 'keywords': ['DoLA', 'Dola']},
    {'name_cn': 'Gingersoft', 'keywords': ['CLG', 'Gingersoft']},
    {'name_cn': 'Loyverse', 'keywords': ['Loyverse']}
]

def search_app_store(keyword, country='HK'):
    """搜索 App Store"""
    url = f'https://itunes.apple.com/search?term={keyword}&country={country}&entity=software&limit=10'
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return data.get('results', [])
    except Exception as e:
        print(f"  Error: {e}")
    return []

def main():
    for comp in competitors:
        print(f"\n{'='*60}")
        print(f"搜索: {comp['name_cn']}")
        print(f"关键词: {comp['keywords']}")

        found = []
        for keyword in comp['keywords'][:2]:  # 只搜索前2个关键词
            print(f"\n  搜索 '{keyword}'...")
            results = search_app_store(keyword)

            for app in results[:3]:  # 只显示前3个结果
                track_name = app.get('trackName', '')
                bundle_id = app.get('bundleId', '')
                artist = app.get('artistName', '')
                genre = app.get('genres', [''])[0] if app.get('genres') else ''

                # 过滤：只看相关度高的
                if keyword.lower() in track_name.lower() or keyword.lower() in bundle_id.lower():
                    print(f"    ✓ {track_name}")
                    print(f"      Bundle ID: {bundle_id}")
                    print(f"      开发商: {artist}")
                    print(f"      分类: {genre}")

                    if bundle_id not in [f['bundle_id'] for f in found]:
                        found.append({
                            'keyword': keyword,
                            'track_name': track_name,
                            'bundle_id': bundle_id,
                            'artist': artist,
                            'genre': genre
                        })
                        break  # 找到一个就停止

        if found:
            print(f"\n  → 推荐 Bundle ID: {found[0]['bundle_id']}")
        else:
            print(f"\n  ✗ 未找到相关应用")

if __name__ == '__main__':
    main()
