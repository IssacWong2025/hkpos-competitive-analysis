#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Website Customer Case Collection via SerpAPI
Search for customer cases/成功案例 on competitor websites
"""

import requests
import csv
import sys
import time
import io
import pandas as pd
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
import re

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

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

def search_customer_cases(domain, company_name):
    """Search for customer cases using Google site search"""
    base_url = "https://serpapi.com/search.json"

    # Search for customer cases on their website
    search_queries = [
        f'site:{domain} "客户"',  # Chinese
        f'site:{domain} "案例"',  # Chinese
        f'site:{domain} "customer"',  # English
        f'site:{domain} "case study"',  # English
        f'site:{domain} "成功案例"',  # Chinese
    ]

    results = {
        '竞品': company_name,
        '域名': domain,
        '搜索查询数': 0,
        '客户案例链接': [],
        '查询时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    total_found = 0

    for i, query in enumerate(search_queries, 1):
        params = {
            'engine': 'google',
            'q': query,
            'api_key': SERPAPI_KEY,
            'gl': 'hk',
            'num': 20  # Top 20 results per query
        }

        try:
            print(f"  → Query {i}: {query[:60]}...")
            response = requests.get(base_url, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()

                if 'error' in data:
                    error_msg = data.get('error', '')
                    print(f"    ⚠ API Error: {error_msg[:60]}")
                    continue

                # Count organic results
                organic_count = len(data.get('organic_results', []))
                total_found += organic_count
                results['搜索查询数'] += organic_count

                # Extract links from results
                organic = data.get('organic_results', [])
                for item in organic[:10]:  # First 10
                    link = item.get('link', '')
                    title = item.get('title', '')[:100]
                    snippet = item.get('snippet', '')[:200]

                    if link:
                        results['客户案例链接'].append({
                            '标题': title,
                            '链接': link,
                            '摘要': snippet
                        })

                print(f"    ✓ Found {organic_count} results")

            else:
                print(f"    ⚠ HTTP {response.status_code}")

        except Exception as e:
            print(f"    ✗ Error: {str(e)[:60]}")

        # Rate limiting
        if i < len(search_queries):
            delay = 1 + (i % 2)
            time.sleep(delay)

    # Calculate estimated customer count
    # Remove duplicate links
    unique_links = list(set([item['链接'] for item in results['客户案例链接']]))
    results['估算客户数'] = len(unique_links)

    # Estimate based on search result count (heuristic)
    # If found many results, likely has many customers
    if results['搜索查询数'] > 50:
        estimated_customers = '100+'
    elif results['搜索查询数'] > 20:
        estimated_customers = '50-100'
    elif results['搜索查询数'] > 10:
        estimated_customers = '20-50'
    elif results['搜索查询数'] > 5:
        estimated_customers = '10-20'
    elif results['搜索查询数'] > 0:
        estimated_customers = '5-10'
    else:
        estimated_customers = '0-5'

    results['估算客户等级'] = estimated_customers
    results['状态'] = 'success' if results['搜索查询数'] > 0 else 'no_results'

    return results

def collect_customer_cases(competitors):
    """Collect customer case data for all competitors"""
    results = []

    for i, comp in enumerate(competitors, 1):
        name = comp['name_en']
        domain = comp['domain']
        website = comp['website']

        print(f"\n{'='*60}")
        print(f"[{i}/{len(competitors)}] Processing: {name}")
        print(f"Domain: {domain}")
        print(f"Website: {website}")

        # Search for customer cases
        data = search_customer_cases(domain, name)

        data['官网'] = website
        results.append(data)

        # Small delay between competitors
        if i < len(competitors):
            delay = 2
            print(f"  → Waiting {delay}s...")
            time.sleep(delay)

    return results

def save_to_excel(results, filename):
    """Save results to Excel"""
    try:
        df = pd.DataFrame(results)

        # Select and reorder columns
        display_cols = ['竞品', '域名', '官网', '估算客户数', '估算客户等级',
                       '搜索查询数', '状态', '查询时间']

        # Add links summary
        df['案例链接数'] = df['客户案例链接'].apply(lambda x: len(x) if isinstance(x, list) else 0)

        # Reorder columns
        df = df[[c for c in display_cols if c in df.columns] + ['案例链接数']]

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

def main():
    """Main function"""
    print("=" * 60)
    print("Website Customer Case Collection")
    print("=" * 60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Load competitors
    print("\nLoading competitor list...")
    competitors = load_competitors()
    if not competitors:
        print("\n✗ Error: No competitors loaded")
        return

    # Collect data
    print("\nStarting customer case search via SerpAPI...")
    results = collect_customer_cases(competitors)

    # Save to Excel
    print("\n" + "=" * 60)
    print("Saving results...")

    timestamp = datetime.now().strftime('%Y%m%d')
    output_file = f"website_customer_cases_{timestamp}.xlsx"

    if save_to_excel(results, output_file):
        # Print summary
        print("\n" + "=" * 60)
        print("Summary:")
        success_count = len([r for r in results if r.get('状态') == 'success'])
        no_results_count = len([r for r in results if r.get('状态') == 'no_results'])

        print(f"  Success: {success_count}/{len(results)}")
        print(f"  No results: {no_results_count}/{len(results)}")

        if success_count > 0:
            # Find top competitors by customer count
            top_customers = sorted(results, key=lambda x: x.get('搜索查询数', 0), reverse=True)[:5]

            print(f"\nTop 5 by search visibility:")
            for i, r in enumerate(top_customers, 1):
                print(f"  {i}. {r['竞品']}: {r['搜索查询数']} searches, ~{r['估算客户等级']} customers")

            avg_searches = sum([r.get('搜索查询数', 0) for r in results]) / len(results)
            print(f"\nAverage search results: {avg_searches:.1f}/competitor")

    print(f"\nComplete time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
