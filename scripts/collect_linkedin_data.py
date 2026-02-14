#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Company Data Collector
Extract employee count and follower data for market share estimation
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
            if row['竞品英文名'] and row['LinkedIn URL']:
                competitors.append({
                    'name_cn': row['竞品中文名'],
                    'name_en': row['竞品英文名'],
                    'linkedin': row['LinkedIn URL'],
                    'website': row['官网URL'],
                    'bundle_id': row['App Store Bundle ID']
                })

    print(f"✓ Loaded {len(competitors)} competitors with LinkedIn URLs")
    return competitors

def extract_linkedin_company_data(url):
    """Extract company data from LinkedIn page"""

    # LinkedIn is challenging to scrape, but we can try basic extraction
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    data = {
        'status': 'failed',
        'employees': None,
        'followers': None,
        'company_size': None,
        'raw_html': ''
    }

    try:
        print(f"  → Fetching {url}...")
        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Try to find employee count in meta/OG data
            # LinkedIn often puts this in meta tags or structured data
            employee_count = None

            # Method 1: Check for common employee count patterns in text
            text = soup.get_text()

            # Look for patterns like "10,000+ employees" or "10K+"
            patterns = [
                r'(\d+[,\d]*)\s*employees?',
                r'(\d+[,\d]*)\s*staff',
                r'(\d+)K\+\s*employees?',
                r'See all\s*(\d+)[,\d]*\s*employees'
            ]

            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    emp_str = match.group(1).replace(',', '')
                    try:
                        employee_count = int(emp_str)
                        break
                    except:
                        pass

            # Method 2: Check meta tags
            meta_employees = soup.find('meta', attrs={'name': 'employeeCount'})
            if meta_employees and meta_employees.get('content'):
                try:
                    employee_count = int(meta_employees['content'].replace(',', ''))
                except:
                    pass

            if employee_count:
                data['employees'] = employee_count
                # Classify company size
                if employee_count < 50:
                    data['company_size'] = 'Small (1-50)'
                elif employee_count < 200:
                    data['company_size'] = 'Medium (50-200)'
                elif employee_count < 1000:
                    data['company_size'] = 'Large (200-1K)'
                else:
                    data['company_size'] = 'Enterprise (1K+)'

                data['status'] = 'success'
                print(f"    ✓ Employees: {employee_count}")

            # Try to extract follower data (company page followers)
            # This is often in specific container
            follower_patterns = [
                r'(\d+[,\d]*)\s*followers?',
                r'(\d+[,\d]*)\s*following'
            ]

            for pattern in follower_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    follower_str = match.group(1).replace(',', '')
                    try:
                        data['followers'] = int(follower_str)
                        print(f"    ✓ Followers: {data['followers']}")
                        break
                    except:
                        pass

            # Save raw HTML length for debugging
            data['raw_html'] = f"{len(response.text)} chars"

        elif response.status_code == 999:
            # LinkedIn often returns 999 for bot detection
            data['status'] = 'blocked'
            print(f"    ⚠ Blocked (999)")
        else:
            print(f"    ⚠ Status: {response.status_code}")

    except Exception as e:
        print(f"    ✗ Error: {str(e)[:100]}")
        data['error'] = str(e)[:200]

    return data

def collect_linkedin_data(competitors):
    """Collect LinkedIn data for all competitors"""
    results = []

    for i, comp in enumerate(competitors, 1):
        name = comp['name_en']
        linkedin_url = comp['linkedin']

        print(f"\n{'='*60}")
        print(f"[{i}/{len(competitors)}] {name}")
        print(f"LinkedIn: {linkedin_url}")

        # Check if URL is valid
        if not linkedin_url or linkedin_url.lower() == 'n/a':
            print("  → No LinkedIn URL, skipping")
            results.append({
                '竞品': name,
                '竞品中文名': comp['name_cn'],
                'LinkedIn URL': linkedin_url,
                '状态': 'no_url'
            })
            continue

        # Extract data
        data = extract_linkedin_company_data(linkedin_url)

        # Add basic info
        data['竞品'] = name
        data['竞品中文名'] = comp['name_cn']
        data['LinkedIn URL'] = linkedin_url
        data['官网'] = comp['website']
        data['App Store Bundle ID'] = comp['bundle_id']
        data['查询时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        results.append(data)

        # Rate limiting
        if i < len(competitors):
            delay = 2 + (i % 3)
            print(f"  → Waiting {delay}s...")
            time.sleep(delay)

    return results

def save_to_excel(results, filename):
    """Save results to Excel"""
    try:
        df = pd.DataFrame(results)

        # Reorder columns for readability
        priority_cols = ['竞品中文名', '竞品', 'company_size', 'employees', 'followers',
                       'status', 'LinkedIn URL', '官网', '查询时间']
        other_cols = [c for c in df.columns if c not in priority_cols]
        ordered_cols = [c for c in priority_cols if c in df.columns] + other_cols

        df = df[ordered_cols]

        # Save
        output_path = Path("market_research/data") / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        df.to_excel(output_path, index=False, engine='openpyxl')

        print(f"\n✓ Data saved: {output_path}")

        # Print summary
        success_count = len(df[df['status'] == 'success'])
        blocked_count = len(df[df['status'] == 'blocked'])
        no_url_count = len(df[df['status'] == 'no_url'])

        print(f"\nSummary:")
        print(f"  Success: {success_count}/{len(results)}")
        print(f"  Blocked: {blocked_count}/{len(results)}")
        print(f"  No URL: {no_url_count}/{len(results)}")

        if success_count > 0:
            avg_employees = df[df['status'] == 'success']['employees'].mean()
            max_employees = df[df['status'] == 'success']['employees'].max()
            print(f"  Average employees: {avg_employees:.0f}")
            print(f"  Max employees: {max_employees:.0f}")

        return True

    except Exception as e:
        print(f"\n✗ Save failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("LinkedIn Company Data Collection")
    print("=" * 60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Load competitors
    print("\nLoading competitor list...")
    competitors = load_competitors()
    if not competitors:
        print("\n✗ Error: No competitors loaded")
        return

    # Collect data
    print("\nStarting data collection via LinkedIn...")
    results = collect_linkedin_data(competitors)

    # Save to Excel
    print("\n" + "=" * 60)
    print("Saving results...")

    timestamp = datetime.now().strftime('%Y%m%d')
    output_file = f"linkedin_company_data_{timestamp}.xlsx"

    if save_to_excel(results, output_file):
        print(f"\n✓ Complete: {len(results)} records collected")
        print(f"✓ Excel: market_research/data/{output_file}")

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
