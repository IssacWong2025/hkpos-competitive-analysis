#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SimilarWeb Data Collection with Manual Login
User logs in once, script automatically scrapes all competitors
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
from playwright.async_api import async_playwright

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

SIMILARWEB_BASE = "https://similarweb.com"
COMPETITOR_CSV = "market_research/data/competitor_apps.csv"
USER_DATA_DIR = "./browser_profile_similarweb"

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

async def wait_for_login(page, timeout=300):
    """Wait for user to manually log in to SimilarWeb"""
    print("\n" + "="*60)
    print("🔐 LOGIN REQUIRED")
    print("="*60)
    print("\n1. A browser window will open")
    print("2. Please log in to SimilarWeb in that window")
    print("3. Script will automatically continue after login")
    print("\nWaiting for login...")

    # Navigate to SimilarWeb homepage
    try:
        await page.goto("https://similarweb.com", wait_until='domcontentloaded', timeout=60000)
    except Exception as e:
        print(f"  ⚠ Navigation had issues: {str(e)[:50]}")
        print("  → Continuing anyway...")

    # Check if already logged in from previous session
    try:
        # Check for login button (not logged in)
        login_btn = await page.query_selector('a[href*="login"], button:has-text("Log in"), .login-button')
        if login_btn:
            print("\n⚠ Not logged in. Please log in now...")
        else:
            # Check for user avatar/menu (logged in)
            user_menu = await page.query_selector('.user-menu, [class*="user-avatar"], [class*="user-profile"]')
            if user_menu:
                print("\n✓ Already logged in! Proceeding...")
                return True
    except:
        pass

    # Wait for login - poll for changes
    start_time = time.time()
    last_url = page.url

    while time.time() - start_time < timeout:
        await asyncio.sleep(2)

        # Check if URL changed (might be redirected after login)
        current_url = page.url
        if current_url != last_url:
            print(f"  → URL changed: {current_url}")

        # Try to detect successful login
        try:
            # Check for user menu/profile elements
            logged_in_indicators = [
                '.user-menu',
                '[class*="user-avatar"]',
                '[class*="user-profile"]',
                '[data-testid="user-menu"]',
                '.header__user',
            ]

            for selector in logged_in_indicators:
                element = await page.query_selector(selector)
                if element:
                    print("\n✓ Login detected!")
                    await asyncio.sleep(2)  # Wait for page to settle
                    return True

            # Check if login button disappeared
            login_btn = await page.query_selector('a[href*="login"], button:has-text("Log in")')
            if not login_btn:
                print("\n✓ Login button disappeared - assuming success!")
                await asyncio.sleep(2)
                return True

        except Exception as e:
            pass

        # Progress indicator
        elapsed = int(time.time() - start_time)
        if elapsed % 15 == 0 and elapsed > 0:
            print(f"  → Still waiting... ({elapsed}s)")

    print("\n⚠ Timeout waiting for login")
    return False

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
        print("  → Navigating to page...")
        await page.goto(url, wait_until='domcontentloaded', timeout=30000)

        # Wait for dynamic content to load
        await asyncio.sleep(5)

        # Check for access denied
        title = await page.title()
        print(f"  → Page title: {title}")

        if 'access denied' in title.lower() or 'error' in title.lower() or 'could not be satisfied' in title.lower():
            print(f"  ⚠ Access denied/error page detected")
            data['状态'] = '访问被拒绝'
            data['状态码'] = 'ACCESS_DENIED'

            # Save screenshot for debugging
            screenshot_path = Path(f"market_research/charts/debug_{name.replace(' ', '_')}.png")
            await page.screenshot(path=str(screenshot_path))
            return data

        # Try to extract data with multiple methods
        print("  → Extracting data...")

        # Method 1: SimilarWeb's structured data (if available in page)
        try:
            metrics = await page.evaluate("""() => {
                const results = {};

                // Look for data in various possible selectors
                const metricCards = document.querySelectorAll('[class*="metric"], [class*="card"], [class*="overview"]');

                metricCards.forEach(card => {
                    const labelEl = card.querySelector('[class*="label"], [class*="title"], [class*="name"], [class*="description"]');
                    const valueEl = card.querySelector('[class*="value"], [class*="number"], [class*="count"]');

                    if (labelEl && valueEl) {
                        const label = labelEl.textContent?.trim().replace(/\\n/g, ' ');
                        const value = valueEl.textContent?.trim().replace(/\\n/g, ' ');
                        if (label && value && label.length < 50 && value.length < 50) {
                            results[label] = value;
                        }
                    }
                });

                return results;
            }""")

            if metrics:
                print(f"  ✓ Found {len(metrics)} data points")
                for key, value in list(metrics.items())[:8]:  # First 8
                    data[f'指标_{key}'] = value
                    print(f"    - {key}: {value}")
        except Exception as e:
            print(f"  ⚠ Metric extraction failed: {str(e)[:50]}")

        # Method 2: Look for specific text patterns
        try:
            page_text = await page.evaluate("""() => {
                return document.body.innerText;
                    }""")

            # Extract common metrics using regex
            import re
            patterns = {
                '总访问量': r'Total Visits[:\\s]+([\\d.]+[KMB]?)',
                '平均访问时长': r'Avg.*Duration[:\\s]+([\\d:]+)',
                '跳出率': r'Bounce Rate[:\\s]+([\\d.]+%)',
                '全球排名': r'Global Rank[:\\s]+#?([\\d,]+)',
            }

            for label, pattern in patterns.items():
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    value = match.group(1)
                    data[label] = value
                    print(f"  ✓ {label}: {value}")
        except Exception as e:
            print(f"  ⚠ Pattern extraction failed: {str(e)[:50]}")

        # Method 3: Look for structured JSON data in page
        try:
            json_data = await page.evaluate("""() => {
                // Look for Next.js data
                const nextData = document.getElementById('__NEXT_DATA__');
                if (nextData) {
                    return JSON.parse(nextData.textContent);
                }

                // Look for other embedded JSON
                const scripts = document.querySelectorAll('script[type="application/json"]');
                if (scripts.length > 0) {
                    return Array.from(scripts).map(s => {
                        try { return JSON.parse(s.textContent); }
                        catch(e) { return null; }
                    }).filter(Boolean);
                }

                return null;
            }""")

            if json_data:
                print(f"  ✓ Found embedded JSON data")
                data['has_json_data'] = 'Y'
        except Exception as e:
            pass

        # Determine success
        extracted_fields = [k for k in data.keys() if not k.startswith(('指标_', '竞品', '域名', '官网', 'SimilarWeb', '查询时间', '状态'))]
        if len(extracted_fields) > 0 or 'has_json_data' in data:
            data['状态'] = '成功'
            data['状态码'] = 'SUCCESS'
            print(f"  ✓ Data extraction successful ({len(extracted_fields)} fields)")
        else:
            data['状态'] = '页面加载但无数据'
            data['状态码'] = 'NO_DATA'
            print(f"  ⚠ Page loaded but no data extracted")

        # Save screenshot
        screenshot_path = Path(f"market_research/charts/screenshot_{name.replace(' ', '_')}.png")
        await page.screenshot(path=str(screenshot_path), full_page=False)
        print(f"  ✓ Screenshot saved")

    except Exception as e:
        print(f"  ⚠ Error: {str(e)[:100]}")
        data['状态'] = '错误'
        data['状态码'] = 'ERROR'
        data['错误信息'] = str(e)[:200]

    return data

async def main():
    """Main async function"""
    print("=" * 60)
    print("SimilarWeb Data Collection (Interactive Login)")
    print("=" * 60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Load competitors
    print("\nLoading competitor list...")
    competitors = load_competitors()
    if not competitors:
        print("\n✗ Error: No competitors loaded")
        return

    async with async_playwright() as p:
        # Use persistent context to save login state
        print(f"\nLaunching browser with persistent profile...")
        print(f"  Profile dir: {USER_DATA_DIR}")

        browser = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,  # Must be visible for manual login
            args=['--disable-blink-features=AutomationControlled'],
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        )

        # Get or create page
        existing_pages = browser.pages
        if len(existing_pages) > 0:
            page = existing_pages[0]
        else:
            page = await browser.new_page()

        # Wait for manual login
        login_success = await wait_for_login(page, timeout=300)

        if not login_success:
            print("\n⚠ Login failed or timeout. You may need to:")
            print("  1. Delete the browser_profile_similarweb folder")
            print("  2. Run the script again")
            print("  3. Log in properly this time")
            await browser.close()
            return

        print("\n" + "="*60)
        print("✓ LOGIN SUCCESSFUL - Starting data collection")
        print("="*60)

        results = []
        total = len(competitors)

        for i, comp in enumerate(competitors, 1):
            print(f"\n[Processing {i}/{total}]")
            data = await scrape_similarweb_page(page, comp)
            results.append(data)

            # Small delay between requests
            if i < total:
                delay = 2 + (i % 3)
                await asyncio.sleep(delay)

        # Close browser
        await browser.close()

    # Save results
    print("\n" + "=" * 60)
    print("Saving results...")

    timestamp = datetime.now().strftime('%Y%m%d')
    output_file = f"similarweb_data_interactive_{timestamp}.xlsx"

    try:
        df = pd.DataFrame(results)
        output_path = Path("market_research/data") / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_excel(output_path, index=False, engine='openpyxl')
        print(f"✓ Data saved: {output_path}")

        # Print summary
        success_count = len(df[df['状态码'] == 'SUCCESS'])
        print(f"\nSummary: {success_count}/{total} successful")
    except Exception as e:
        print(f"✗ Save failed: {str(e)}")

    print(f"\nComplete time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Collected {len(results)} records")
    print("\nNote: Browser profile saved. Next run will skip login if still valid.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
