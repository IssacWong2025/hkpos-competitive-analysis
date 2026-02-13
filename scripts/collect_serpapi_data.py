#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SerpAPI Competitor Data Collection
Alternative to SimilarWeb for traffic and ranking insights
"""

import requests
import csv
import sys
import json
import time
import io
import pandas as pd
from pathlib import Path
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ================
SERPAPI_KEY = "f6227a873d1bc7105a174273b567bf38e537920eb35c68123efb1848bd5f3dab"
COMPETITOR_CSV = "market_research/data/competitor_apps.csv"

def load_competitors():
    """Load competitor list from CSV"""
    csv_path = Path(COMPETITOR_CSV)
    if not csv_path.exists():
        print(f"✗ Warning: {COMPETITOR_CSV} not found")
        return []

    competitors = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['竞品中文名'] and row['官网URL']:
                competitors.append({
                    'name_cn': row['竞品中文名'],
                    'name_en': row['竞品英文名'],
                    'website': row['官网URL'],
                    'domain': extract_domain(row['官网URL'])
                })

    print(f"✓ Loaded {len(competitors)} competitors")
    return competitors

def extract_domain(url):
    """Extract domain from URL"""
    if not url or url == 'N/A':
        return ''
    url = url.replace('https://', '').replace('http://', '').replace('www.', '')
    return url.split('/')[0]

def search_domain_info(domain, company_name):
    """Search for domain information using SerpAPI"""
    base_url = "https://serpapi.com/search.json"

    # Search for the company/brand name
    params = {
        'engine': 'google',
        'q': company_name,  # Search by company name
        'api_key': SERPAPI_KEY,
        'gl': 'hk',       # Hong Kong location
        'num': 10
    }

    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"  ⚠ API Error: {str(e)[:80]}")
        return None

def extract_organic_results(data):
    """Extract organic search results information"""
    if not data or 'organic_results' not in data:
        return {}

    results = data.get('organic_results', [])

    return {
        'organic_results_count': len(results),
        'top_rank_title': results[0].get('title', '') if results else '',
        'top_rank_link': results[0].get('link', '') if results else '',
        'top_rank_snippet': results[0].get('snippet', '')[:200] if results else '',
    }

def extract_related_searches(data):
    """Extract related search terms"""
    if not data or 'related_searches' not in data:
        return {}

    related = data.get('related_searches', [])[:10]  # Top 10

    return {
        'related_searches_count': len(related),
        'related_searches': ', '.join([r.get('query', '') for r in related if r.get('query')])
    }

def extract_knowledge_graph(data):
    """Extract knowledge graph information if available"""
    if not data or 'knowledge_graph' not in data:
        return {}

    kg = data.get('knowledge_graph', {})

    return {
        'kg_type': kg.get('type', ''),
        'kg_title': kg.get('title', ''),
        'kg_description': kg.get('description', '')[:300] if kg.get('description') else '',
        'kg_website': kg.get('website', '') if kg.get('website') else '',
        'kg_images_count': len(kg.get('images', [])),
    }

def calculate_search_visibility_score(data):
    """Calculate a simple search visibility score"""
    score = 0

    # Has organic results
    if data and 'organic_results' in data:
        organic = data.get('organic_results', [])
        score += min(len(organic) * 5, 50)  # Max 50 points

    # Has knowledge graph (brand authority)
    if data and 'knowledge_graph' in data:
        score += 30

    # Has related searches (brand relevance)
    if data and 'related_searches' in data:
        related_count = len(data.get('related_searches', []))
        score += min(related_count * 2, 20)  # Max 20 points

    return min(score, 100)  # Max 100

def collect_competitor_data(competitors):
    """Collect data for all competitors"""
    results = []

    for i, comp in enumerate(competitors, 1):
        name = comp['name_en']
        domain = comp['domain']
        website = comp['website']

        print(f"\n{'='*60}")
        print(f"[{i}/{len(competitors)}] Processing: {name}")
        print(f"Domain: {domain}")
        print(f"Website: {website}")

        data = {
            '竞品': name,
            '竞品中文名': comp['name_cn'],
            '域名': domain,
            '官网': website,
            '查询时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Search for domain info
        print("  → Searching via SerpAPI...")
        api_data = search_domain_info(domain, name)

        if api_data:
            # Check for API errors
            if 'error' in api_data:
                error_msg = api_data.get('error', '')
                print(f"  ⚠ API Error: {error_msg}")
                data['状态'] = 'API Error'
                data['错误信息'] = str(error_msg)[:200]
                results.append(data)
                continue

            # Extract information
            print("  → Extracting data...")

            # Organic results
            organic = extract_organic_results(api_data)
            data.update(organic)
            print(f"    ✓ Organic results: {organic.get('organic_results_count', 0)}")

            # Related searches
            related = extract_related_searches(api_data)
            data.update(related)
            print(f"    ✓ Related searches: {related.get('related_searches_count', 0)}")

            # Knowledge graph
            kg = extract_knowledge_graph(api_data)
            data.update(kg)
            if kg.get('kg_type'):
                print(f"    ✓ Knowledge Graph: {kg.get('kg_type', '')}")

            # Calculate visibility score
            visibility_score = calculate_search_visibility_score(api_data)
            data['搜索可见度评分'] = visibility_score
            print(f"    ✓ Visibility score: {visibility_score}/100")

            # Save raw API response for reference
            data['api_response_json'] = json.dumps(api_data, ensure_ascii=False)[:500]

            # Determine status
            data['状态'] = '成功'
            data['状态码'] = 'SUCCESS'

        else:
            data['状态'] = '请求失败'
            data['状态码'] = 'REQUEST_FAILED'

        results.append(data)

        # Rate limiting - wait between requests
        if i < len(competitors):
            delay = 1 + (i % 2)  # 1-2 seconds
            print(f"  → Waiting {delay}s before next request...")
            time.sleep(delay)

    return results

def save_to_excel(results, filename):
    """Save results to Excel"""
    try:
        df = pd.DataFrame(results)

        # Reorder columns for readability
        priority_cols = ['竞品', '竞品中文名', '域名', '搜索可见度评分', '状态', 'organic_results_count',
                       'related_searches_count', 'kg_type']
        other_cols = [c for c in df.columns if c not in priority_cols]

        # Reorder
        ordered_cols = priority_cols + [c for c in other_cols if c not in priority_cols]
        df = df[ordered_cols]

        # Save
        output_path = Path("market_research/data") / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        df.to_excel(output_path, index=False, engine='openpyxl')

        print(f"\n✓ Data saved: {output_path}")
        return True

    except Exception as e:
        print(f"\n✗ Save failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def generate_html_summary(results):
    """Generate HTML summary report"""
    # Sort by visibility score
    sorted_results = sorted(results, key=lambda x: x.get('搜索可见度评分', 0), reverse=True)

    html_items = ""
    for r in sorted_results:
        score = r.get('搜索可见度评分', 0)
        color = '#22c55e' if score >= 70 else '#3b82f6' if score >= 40 else '#f59e0b' if score > 0 else '#9ca3af'

        html_items += f"""    <tr>
      <td><strong>{r['竞品']}</strong></td>
      <td><div style="background:{color};width:{max(score, 2)}%;height:20px;border-radius:4px;"></div></td>
      <td>{score}</td>
      <td>{r.get('organic_results_count', '-')}</td>
      <td>{r.get('related_searches_count', '-')}</td>
      <td>{r.get('kg_type', '-')}</td>
    </tr>
"""

    html = f"""<!DOCTYPE html>
<html lang="zh-HK">
<head>
<meta charset="UTF-8">
<title>竞品搜索可见度分析 - SerpAPI</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; padding: 24px; }}
h1 {{ font-size: 24px; margin-bottom: 8px; color: #f8fafc; }}
.subtitle {{ color: #94a3b8; margin-bottom: 24px; font-size: 14px; }}
.card {{ background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; }}
table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
th {{ text-align: left; padding: 12px; border-bottom: 2px solid #334155; color: #94a3b8; font-weight: 500; }}
td {{ padding: 12px; border-bottom: 1px solid #1e293b; }}
tr:hover td {{ background: #1e293b; }}
.metric {{ display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600; }}
.metric-high {{ background: #22c55e20; color: #22c55e; }}
.metric-mid {{ background: #3b82f620; color: #3b82f6; }}
.metric-low {{ background: #f59e0b20; color: #f59e0b; }}
.footer {{ margin-top: 24px; text-align: center; font-size: 12px; color: #475569; }}
</style>
</head>
<body>
<h1>竞品搜索可见度分析</h1>
<p class="subtitle">数据来源: Google Search (SerpAPI) &middot; 更新: {datetime.now().strftime('%Y-%m-%d')}</p>

<div class="card">
  <table>
    <thead>
      <tr>
        <th>竞品</th>
        <th>搜索可见度</th>
        <th>评分</th>
        <th>搜索结果数</th>
        <th>相关搜索数</th>
        <th>知识图谱</th>
      </tr>
    </thead>
    <tbody>
{html_items}
    </tbody>
  </table>
</div>

<div class="footer">
  <p>评分说明：基于自然搜索结果数、知识图谱存在性、相关搜索数量综合计算</p>
  <p>数据来源: SerpAPI (Google Search) | 仅供内部分析参考</p>
</div>
</body>
</html>"""

    # Save
    charts_dir = Path("market_research/charts")
    charts_dir.mkdir(parents=True, exist_ok=True)

    output_path = charts_dir / 'serpapi_visibility_comparison.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✓ HTML report: {output_path}")
    return output_path

def main():
    """Main function"""
    print("=" * 60)
    print("SerpAPI Competitor Data Collection")
    print("=" * 60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Load competitors
    print("\nLoading competitor list...")
    competitors = load_competitors()
    if not competitors:
        print("\n✗ Error: No competitors loaded")
        return

    # Collect data
    print("\nStarting data collection via SerpAPI...")
    results = collect_competitor_data(competitors)

    # Save to Excel
    print("\n" + "=" * 60)
    print("Saving results...")

    timestamp = datetime.now().strftime('%Y%m%d')
    output_file = f"serpapi_data_{timestamp}.xlsx"

    if save_to_excel(results, output_file):
        # Generate HTML summary
        print("\nGenerating HTML summary...")
        generate_html_summary(results)

        print(f"\n✓ Complete: {len(results)} records collected")
        print(f"✓ Excel: market_research/data/{output_file}")
        print(f"✓ HTML: market_research/charts/serpapi_visibility_comparison.html")

    # Print summary
    print("\n" + "=" * 60)
    print("Summary:")
    successful = len([r for r in results if r.get('状态码') == 'SUCCESS'])
    failed = len(results) - successful
    print(f"  Success: {successful}")
    print(f"  Failed: {failed}")

    if successful > 0:
        avg_score = sum([r.get('搜索可见度评分', 0) for r in results if r.get('搜索可见度评分', 0) > 0]) / max(successful, 1)
        print(f"  Avg Visibility Score: {avg_score:.1f}/100")

if __name__ == "__main__":
    main()
