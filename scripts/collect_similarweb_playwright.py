#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SimilarWeb Data Collection with Playwright
Solves 403 Forbidden by using real browser automation
"""

import asyncio
import csv
import sys
import json
import time
import io
import pandas as pd
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ================
SIMILARWEB_BASE = "https://similarweb.com"
COMPETITOR_CSV = "market_research/data/competitor_apps.csv"
COOKIE_FILE = "cookies.json"

def load_cookies(cookie_file):
    """Load cookies from JSON file"""
    try:
        with open(cookie_file, 'r', encoding='utf-8') as f:
            cookies_data = json.load(f)
        print(f"✓ Loaded {len(cookies_data)} cookies from {cookie_file}")
        return cookies_data
    except FileNotFoundError:
        print(f"✗ Error: File not found {cookie_file}")
        return []
    except json.JSONDecodeError as e:
        print(f"✗ JSON decode error: {str(e)}")
        return []

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
                website = row['官网URL']
                domain = extract_domain(website)
                competitors.append({
                    'name_cn': row['竞品中文名'],
                    'name_en': row['竞品英文名'],
                    'website': website,
                    'domain': domain,
                    'similarweb_url': f"{SIMILARWEB_BASE}/website/{domain}"
                })

    print(f"✓ Loaded {len(competitors)} competitors")
    return competitors

def extract_domain(url):
    """Extract domain from URL"""
    if not url or url == 'N/A':
        return ''
    url = url.replace('https://', '').replace('http://', '').replace('www.', '')
    return url.split('/')[0]

async def scrape_similarweb_page(page, competitor):
    """Scrape SimilarWeb data for a single competitor"""
    name = competitor['name_en']
    domain = competitor['domain']
    url = competitor['similarweb_url']

    print(f"\n{'='*60}")
    print(f"Scraping: {name}")
    print(f"Domain: {domain}")
    print(f"URL: {url}")

    data = {
        '竞品': name,
        '竞品英文名': name,
        '域名': domain,
        '官网': competitor['website'],
        'SimilarWeb URL': url,
        '查询时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    try:
        # Navigate to SimilarWeb page
        print("  → Navigating to page...")
        await page.goto(url, wait_until='networkidle', timeout=30000)

        # Wait for page to load
        await asyncio.sleep(3)

        # Check if we hit a login/gate page
        title = await page.title()
        print(f"  → Page title: {title}")

        if 'login' in title.lower() or 'sign in' in title.lower():
            print(f"  ⚠ Redirected to login page")
            data['状态'] = '需要登录'
            data['状态码'] = 'LOGIN_REQUIRED'
            return data

        # Check for 403/Access Denied
        body_text = await page.evaluate("() => document.body.innerText")
        if 'access denied' in body_text.lower() or '403' in body_text:
            print(f"  ⚠ Access denied")
            data['状态'] = '访问被拒绝'
            data['状态码'] = 'ACCESS_DENIED'
            return data

        # Try to extract traffic data
        print("  → Extracting traffic data...")

        # Method 1: Look for traffic overview elements
        try:
            # Total visits selector (may vary)
            total_visits = await page.evaluate("""() => {
                const selectors = [
                    '[data-testid="total-visits"]',
                    '.total-visits',
                    '.engagement-overview__metric-value',
                    '.website-traffic__summary-number'
                ];
                for (const sel of selectors) {
                    const el = document.querySelector(sel);
                    if (el) return el.textContent?.trim();
                }
                return null;
            }""")

            if total_visits:
                print(f"  ✓ Total visits: {total_visits}")
                data['总访问量'] = total_visits
        except Exception as e:
            print(f"  ⚠ Could not extract total visits: {str(e)[:50]}")

        # Method 2: Look for rank data
        try:
            rank = await page.evaluate("""() => {
                const selectors = [
                    '[data-testid="global-rank"]',
                    '.global-rank',
                    '.rank-value',
                    '.website-rank__number'
                ];
                for (const sel of selectors) {
                    const el = document.querySelector(sel);
                    if (el) return el.textContent?.trim();
                }
                return null;
            }""")

            if rank:
                print(f"  ✓ Global rank: {rank}")
                data['全球排名'] = rank
        except Exception as e:
            print(f"  ⚠ Could not extract rank: {str(e)[:50]}")

        # Method 3: Look for average visit duration
        try:
            duration = await page.evaluate("""() => {
                const selectors = [
                    '[data-testid="avg-duration"]',
                    '.avg-visit-duration',
                    '.engagement-metric__value'
                ];
                for (const sel of selectors) {
                    const el = document.querySelector(sel);
                    if (el) return el.textContent?.trim();
                }
                return null;
            }""")

            if duration:
                print(f"  ✓ Avg duration: {duration}")
                data['平均访问时长'] = duration
        except Exception as e:
            print(f"  ⚠ Could not extract duration: {str(e)[:50]}")

        # Method 4: Check for any data cards
        try:
            metrics = await page.evaluate("""() => {
                const cards = document.querySelectorAll('[class*="metric"], [class*="card"], [class*="overview"]');
                const results = [];
                cards.forEach(card => {
                    const label = card.querySelector('[class*="label"], [class*="title"]');
                    const value = card.querySelector('[class*="value"], [class*="number"]');
                    if (label && value) {
                        results.push(`${label.textContent.trim()}: ${value.textContent.trim()}`);
                    }
                });
                return results.slice(0, 5);  // First 5 metrics
            }""")

            if metrics:
                print(f"  ✓ Found {len(metrics)} metrics")
                data['发现的指标'] = ' | '.join(metrics)
        except Exception as e:
            print(f"  ⚠ Could not extract metrics: {str(e)[:50]}")

        # If we got any data, mark success
        if len(data) > 8:  # More than base fields
            data['状态'] = '成功'
            data['状态码'] = 'SUCCESS'
        else:
            data['状态'] = '部分成功'
            data['状态码'] = 'PARTIAL'

        # Save screenshot for manual review
        screenshot_path = Path(f"market_research/charts/screenshot_{name.replace(' ', '_')}.png")
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=str(screenshot_path), full_page=False)
        print(f"  ✓ Screenshot saved: {screenshot_path}")

    except PlaywrightTimeout as e:
        print(f"  ⚠ Timeout loading page: {str(e)[:50]}")
        data['状态'] = '超时'
        data['状态码'] = 'TIMEOUT'
    except Exception as e:
        print(f"  ⚠ Error: {str(e)[:100]}")
        data['状态'] = '错误'
        data['状态码'] = 'ERROR'
        data['错误信息'] = str(e)[:200]

    return data

async def main():
    """Main async function"""
    print("=" * 60)
    print("SimilarWeb Data Collection with Playwright")
    print("=" * 60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Load competitors
    print("\nLoading competitor list...")
    competitors = load_competitors()
    if not competitors:
        print("\n✗ Error: No competitors loaded")
        return

    # Load cookies (optional, for authenticated sessions)
    cookies = []
    cookie_path = Path(COOKIE_FILE)
    if cookie_path.exists():
        print(f"\nLoading cookies from {COOKIE_FILE}...")
        cookies = load_cookies(COOKIE_FILE)
    else:
        print(f"\n⚠ No cookies file found at {COOKIE_FILE}")
        print("  Will proceed without authentication (may hit limits)")

    async with async_playwright() as p:
        # Launch browser
        print("\nLaunching Chromium browser...")
        browser = await p.chromium.launch(
            headless=False,  # Set to True for production
            args=['--disable-blink-features=AutomationControlled']
        )

        # Create context with realistic settings
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            locale='zh-HK',
            timezone_id='Asia/Hong_Kong'
        )

        # Add cookies if available
        if cookies:
            # Filter and normalize cookies for SimilarWeb
            sw_cookies = []
            same_site_map = {'no_restriction': 'None', 'lax': 'Lax', 'strict': 'Strict', 'none': 'None'}

            for c in cookies:
                if c.get('domain', '') in ['.similarweb.com', 'similarweb.com']:
                    # Normalize cookie format for Playwright
                    cookie = {
                        'name': c.get('name', ''),
                        'value': c.get('value', ''),
                        'domain': c.get('domain', ''),
                        'path': c.get('path', '/'),
                        'httpOnly': c.get('httpOnly', False),
                        'secure': c.get('secure', False),
                        'sameSite': 'None',  # Default to None
                    }

                    # Map sameSite value (handle None)
                    raw_same_site = c.get('sameSite')
                    if raw_same_site:
                        raw_same_site = str(raw_same_site).lower()
                        if raw_same_site in same_site_map:
                            cookie['sameSite'] = same_site_map[raw_same_site]
                        elif raw_same_site in ['strict', 'lax', 'none']:
                            cookie['sameSite'] = raw_same_site.capitalize()

                    # Set expiration if available
                    if c.get('expirationDate'):
                        cookie['expires'] = c['expirationDate']

                    sw_cookies.append(cookie)

            if sw_cookies:
                print(f"  → Adding {len(sw_cookies)} normalized cookies to context")
                await context.add_cookies(sw_cookies)

        # Create page
        page = await context.new_page()

        results = []
        total = len(competitors)

        for i, comp in enumerate(competitors, 1):
            print(f"\n[Processing {i}/{total}]")
            data = await scrape_similarweb_page(page, comp)
            results.append(data)

            # Delay between requests
            if i < total:
                delay = 3 + (i % 3)  # 3-5 seconds
                print(f"  → Waiting {delay}s before next request...")
                await asyncio.sleep(delay)

        # Close browser
        await browser.close()

    # Save results
    print("\n" + "=" * 60)
    print("Saving results...")

    timestamp = datetime.now().strftime('%Y%m%d')
    output_file = f"similarweb_data_playwright_{timestamp}.xlsx"

    try:
        df = pd.DataFrame(results)
        output_path = Path("market_research/data") / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_excel(output_path, index=False, engine='openpyxl')
        print(f"✓ Data saved: {output_path}")
    except Exception as e:
        print(f"✗ Save failed: {str(e)}")

    print(f"\nComplete time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Collected {len(results)} records")
    print("\nCheck market_research/data/ for output files")
    print("Screenshots saved in market_research/charts/")

if __name__ == "__main__":
    asyncio.run(main())
