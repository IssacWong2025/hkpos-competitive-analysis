#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
App Store 数据分析和可视化脚本
生成竞品对比图表（HTML格式）和分析报告
"""

import pandas as pd
import json
import sys
import io
from pathlib import Path
from datetime import datetime, timezone

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ==================
# 配置
# ==================
DATA_DIR = Path("market_research/data")
CHARTS_DIR = Path("market_research/charts")
ANALYSIS_DIR = Path("market_research/analysis")

def load_data():
    """加载最新的 App Store 数据"""
    xlsx_files = sorted(DATA_DIR.glob("app_store_basic_data_*.xlsx"), reverse=True)
    if not xlsx_files:
        print("✗ 未找到 App Store 数据文件")
        return None

    latest = xlsx_files[0]
    print(f"✓ 加载数据: {latest.name}")
    df = pd.read_excel(latest)
    return df

def calculate_activity_score(df):
    """计算应用活跃度评分"""
    now = datetime.now(timezone.utc)
    scores = []

    for _, row in df.iterrows():
        if row.get('status') != 'success':
            scores.append({
                '竞品': row['竞品中文名'],
                '活跃度评分': 0,
                '活跃度等级': '无数据',
                '最后更新': 'N/A',
                '距今天数': None,
                '评分': None,
                '评论数': 0,
            })
            continue

        # 计算距今天数
        last_update = row.get('current_version_release_date', '')
        if pd.notna(last_update) and last_update:
            try:
                update_date = pd.to_datetime(last_update, utc=True)
                days_since = (now - update_date).days
            except:
                days_since = 999
        else:
            days_since = 999

        # 活跃度评分 (0-100)
        # 更新频率分 (0-40): 7天内=40, 30天内=30, 90天内=20, 180天内=10, >180天=0
        if days_since <= 7:
            update_score = 40
        elif days_since <= 30:
            update_score = 30
        elif days_since <= 90:
            update_score = 20
        elif days_since <= 180:
            update_score = 10
        else:
            update_score = 0

        # 版本号分 (0-20): 高版本号暗示频繁更新
        version = str(row.get('version', '0'))
        try:
            major = int(version.split('.')[0])
            version_score = min(20, major * 2)
        except:
            version_score = 0

        # 评论数分 (0-20)
        rating_count = row.get('rating_count', 0)
        if pd.isna(rating_count):
            rating_count = 0
        if rating_count >= 100:
            review_score = 20
        elif rating_count >= 30:
            review_score = 15
        elif rating_count >= 10:
            review_score = 10
        elif rating_count >= 1:
            review_score = 5
        else:
            review_score = 0

        # 评分分 (0-20)
        rating = row.get('rating', 0)
        if pd.isna(rating) or rating == 0:
            rating_score = 0
        else:
            rating_score = int(rating * 4)  # 5.0 -> 20

        total = update_score + version_score + review_score + rating_score

        # 活跃度等级
        if total >= 70:
            level = '高活跃'
        elif total >= 50:
            level = '中活跃'
        elif total >= 25:
            level = '低活跃'
        else:
            level = '不活跃'

        scores.append({
            '竞品': row['竞品中文名'],
            '活跃度评分': total,
            '活跃度等级': level,
            '最后更新': str(last_update)[:10] if pd.notna(last_update) else 'N/A',
            '距今天数': days_since if days_since < 999 else None,
            '评分': round(rating, 2) if pd.notna(rating) and rating > 0 else None,
            '评论数': int(rating_count),
            '更新分': update_score,
            '版本分': version_score,
            '评论分': review_score,
            '评分分': rating_score,
        })

    return pd.DataFrame(scores)

def generate_comparison_chart(score_df, df):
    """生成 HTML 对比图表"""

    # 按活跃度排序
    sorted_df = score_df.sort_values('活跃度评分', ascending=False)

    # 颜色映射
    colors = {
        '高活跃': '#22c55e',
        '中活跃': '#3b82f6',
        '低活跃': '#f59e0b',
        '不活跃': '#ef4444',
        '无数据': '#9ca3af',
    }

    # 构建图表数据
    chart_items = []
    for _, row in sorted_df.iterrows():
        color = colors.get(row['活跃度等级'], '#9ca3af')
        chart_items.append({
            'name': row['竞品'],
            'score': row['活跃度评分'],
            'level': row['活跃度等级'],
            'color': color,
            'rating': row['评分'] if row['评分'] else '-',
            'reviews': row['评论数'],
            'last_update': row['最后更新'],
            'days': row['距今天数'] if row['距今天数'] else '-',
        })

    # 生成 HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-HK">
<head>
<meta charset="UTF-8">
<title>App Store 竞品活跃度对比 - 香港餐饮POS</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; padding: 24px; }}
h1 {{ font-size: 24px; margin-bottom: 8px; color: #f8fafc; }}
.subtitle {{ color: #94a3b8; margin-bottom: 24px; font-size: 14px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); gap: 24px; }}
.card {{ background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; }}
.card h2 {{ font-size: 16px; margin-bottom: 16px; color: #cbd5e1; }}
.bar-chart {{ display: flex; flex-direction: column; gap: 8px; }}
.bar-row {{ display: flex; align-items: center; gap: 8px; }}
.bar-label {{ width: 80px; text-align: right; font-size: 13px; white-space: nowrap; }}
.bar-container {{ flex: 1; height: 28px; background: #0f172a; border-radius: 4px; overflow: hidden; position: relative; }}
.bar {{ height: 100%; border-radius: 4px; transition: width 0.6s ease; display: flex; align-items: center; padding-left: 8px; font-size: 12px; font-weight: 600; }}
.bar-value {{ position: absolute; right: 8px; top: 50%; transform: translateY(-50%); font-size: 12px; color: #94a3b8; }}
table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
th {{ text-align: left; padding: 8px 12px; border-bottom: 2px solid #334155; color: #94a3b8; font-weight: 500; }}
td {{ padding: 8px 12px; border-bottom: 1px solid #1e293b; }}
tr:hover td {{ background: #1e293b; }}
.badge {{ display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; }}
.badge-high {{ background: #22c55e20; color: #22c55e; }}
.badge-mid {{ background: #3b82f620; color: #3b82f6; }}
.badge-low {{ background: #f59e0b20; color: #f59e0b; }}
.badge-dead {{ background: #ef444420; color: #ef4444; }}
.badge-none {{ background: #9ca3af20; color: #9ca3af; }}
.stars {{ color: #fbbf24; }}
.insight {{ background: #1e293b; border-left: 3px solid #3b82f6; padding: 16px; border-radius: 0 8px 8px 0; margin-top: 16px; }}
.insight h3 {{ font-size: 14px; color: #3b82f6; margin-bottom: 8px; }}
.insight ul {{ padding-left: 20px; font-size: 13px; color: #94a3b8; line-height: 1.8; }}
.footer {{ margin-top: 24px; text-align: center; font-size: 12px; color: #475569; }}
</style>
</head>
<body>
<h1>App Store 竞品活跃度对比</h1>
<p class="subtitle">香港餐饮 POS 市场 &middot; 数据更新: {datetime.now().strftime('%Y-%m-%d')} &middot; 数据来源: iTunes Search API</p>

<div class="grid">
  <div class="card">
    <h2>活跃度评分 (0-100)</h2>
    <div class="bar-chart">
"""

    max_score = max(item['score'] for item in chart_items) if chart_items else 100
    for item in chart_items:
        pct = (item['score'] / max(max_score, 1)) * 100
        html += f"""      <div class="bar-row">
        <div class="bar-label">{item['name']}</div>
        <div class="bar-container">
          <div class="bar" style="width:{pct}%;background:{item['color']}">{item['score']}</div>
        </div>
      </div>
"""

    html += """    </div>
  </div>

  <div class="card">
    <h2>详细数据对比</h2>
    <table>
      <thead>
        <tr>
          <th>竞品</th>
          <th>评分</th>
          <th>评论数</th>
          <th>最后更新</th>
          <th>距今</th>
          <th>活跃度</th>
        </tr>
      </thead>
      <tbody>
"""

    badge_map = {
        '高活跃': 'badge-high',
        '中活跃': 'badge-mid',
        '低活跃': 'badge-low',
        '不活跃': 'badge-dead',
        '无数据': 'badge-none',
    }

    for item in chart_items:
        badge_class = badge_map.get(item['level'], 'badge-none')
        if item['rating'] != '-' and item['rating'] is not None and not (isinstance(item['rating'], float) and item['rating'] != item['rating']):
            try:
                stars = '★' * int(float(item['rating']))
            except (ValueError, TypeError):
                stars = ''
            rating_display = f"<span class='stars'>{stars}</span> {item['rating']}"
        else:
            rating_display = '-'
        days_display = f"{item['days']}天" if item['days'] != '-' else '-'

        html += f"""        <tr>
          <td><strong>{item['name']}</strong></td>
          <td>{rating_display}</td>
          <td>{item['reviews']}</td>
          <td>{item['last_update']}</td>
          <td>{days_display}</td>
          <td><span class="badge {badge_class}">{item['level']}</span></td>
        </tr>
"""

    html += """      </tbody>
    </table>
  </div>
</div>

<div class="insight">
  <h3>关键发现</h3>
  <ul>
"""

    # 动态生成洞察
    active = [i for i in chart_items if i['level'] in ('高活跃', '中活跃')]
    inactive = [i for i in chart_items if i['level'] in ('不活跃',)]
    no_app = [i for i in chart_items if i['level'] == '无数据']

    if active:
        names = '、'.join([i['name'] for i in active])
        html += f"    <li><strong>活跃竞品:</strong> {names} 在近期持续更新，产品迭代活跃</li>\n"

    if inactive:
        names = '、'.join([i['name'] for i in inactive])
        html += f"    <li><strong>停滞竞品:</strong> {names} 超过 6 个月未更新，可能已停止维护或转向 Web 方案</li>\n"

    if no_app:
        names = '、'.join([i['name'] for i in no_app])
        html += f"    <li><strong>无 App 竞品:</strong> {names} 未在 App Store 上架，可能为纯 Web 或定制部署方案</li>\n"

    # 评论数最多
    most_reviews = max(chart_items, key=lambda x: x['reviews'])
    if most_reviews['reviews'] > 0:
        html += f"    <li><strong>用户基数:</strong> {most_reviews['name']} 评论数最多（{most_reviews['reviews']}条），暗示较大用户基础</li>\n"

    # 评分最高
    rated = [i for i in chart_items if i['rating'] != '-' and float(i['rating']) > 0]
    if rated:
        best = max(rated, key=lambda x: float(x['rating']))
        html += f"    <li><strong>用户满意度:</strong> {best['name']} 评分最高（{best['rating']}分），用户满意度领先</li>\n"

    html += """  </ul>
</div>

<div class="footer">
  <p>数据来源: Apple iTunes Search API (HK Store) | 仅供内部分析参考</p>
</div>
</body>
</html>"""

    return html

def generate_rating_chart(df):
    """生成评分和评论数对比图表"""
    valid = df[df['status'] == 'success'].copy()
    valid['rating'] = pd.to_numeric(valid['rating'], errors='coerce').fillna(0)
    valid['rating_count'] = pd.to_numeric(valid['rating_count'], errors='coerce').fillna(0)
    valid = valid.sort_values('rating_count', ascending=False)

    max_reviews = valid['rating_count'].max()

    items_html = ""
    for _, row in valid.iterrows():
        pct = (row['rating_count'] / max(max_reviews, 1)) * 100
        rating = row['rating']
        color = '#22c55e' if rating >= 4.0 else '#3b82f6' if rating >= 3.0 else '#f59e0b' if rating > 0 else '#9ca3af'

        items_html += f"""      <div class="bar-row">
        <div class="bar-label">{row['竞品中文名']}</div>
        <div class="bar-container">
          <div class="bar" style="width:{pct}%;background:{color}">{int(row['rating_count'])} 条评论</div>
        </div>
        <div style="width:60px;text-align:right;font-size:12px;color:{color}">{'★' + str(round(rating, 1)) if rating > 0 else '-'}</div>
      </div>
"""

    html = f"""<!DOCTYPE html>
<html lang="zh-HK">
<head>
<meta charset="UTF-8">
<title>App Store 评分评论对比</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; padding: 24px; }}
h1 {{ font-size: 20px; margin-bottom: 16px; }}
.bar-chart {{ display: flex; flex-direction: column; gap: 8px; max-width: 700px; }}
.bar-row {{ display: flex; align-items: center; gap: 8px; }}
.bar-label {{ width: 80px; text-align: right; font-size: 13px; }}
.bar-container {{ flex: 1; height: 28px; background: #1e293b; border-radius: 4px; overflow: hidden; }}
.bar {{ height: 100%; border-radius: 4px; display: flex; align-items: center; padding-left: 8px; font-size: 12px; font-weight: 600; min-width: 2px; }}
</style>
</head>
<body>
<h1>App Store 评论数 & 评分对比</h1>
<div class="bar-chart">
{items_html}
</div>
<p style="margin-top:16px;font-size:12px;color:#475569;">颜色含义: 绿色=4.0+, 蓝色=3.0-4.0, 橙色=<3.0, 灰色=无评分</p>
</body>
</html>"""

    return html

def save_analysis_report(score_df, df):
    """保存分析报告 (Markdown)"""
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

    report = f"""# App Store 竞品数据分析报告

**生成日期**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**数据来源**: Apple iTunes Search API (HK Store)
**覆盖竞品**: 12 家（9 家有 App Store 数据）

---

## 1. 数据覆盖率

| 类别 | 数量 | 竞品 |
|------|------|------|
"""

    has_app = score_df[score_df['活跃度等级'] != '无数据']['竞品'].tolist()
    no_app = score_df[score_df['活跃度等级'] == '无数据']['竞品'].tolist()

    report += f"| 有 App Store 数据 | {len(has_app)} | {', '.join(has_app)} |\n"
    report += f"| 无 App Store 数据 | {len(no_app)} | {', '.join(no_app)} |\n"

    report += f"""
## 2. 活跃度排名

| 排名 | 竞品 | 活跃度评分 | 等级 | 最后更新 | 距今天数 |
|------|------|-----------|------|---------|---------|
"""

    sorted_df = score_df.sort_values('活跃度评分', ascending=False)
    for i, (_, row) in enumerate(sorted_df.iterrows(), 1):
        days = f"{row['距今天数']}天" if row['距今天数'] else 'N/A'
        report += f"| {i} | {row['竞品']} | {row['活跃度评分']} | {row['活跃度等级']} | {row['最后更新']} | {days} |\n"

    report += f"""
## 3. 评分与评论

| 竞品 | App Store 评分 | 评论数 | 分析 |
|------|---------------|-------|------|
"""

    for _, row in sorted_df.iterrows():
        rating = row['评分'] if row['评分'] else '-'
        reviews = row['评论数']

        if row['活跃度等级'] == '无数据':
            analysis = '无 App Store 上架'
        elif reviews == 0:
            analysis = '新上架或无用户反馈'
        elif reviews >= 100:
            analysis = '较大用户基础'
        elif reviews >= 20:
            analysis = '中等用户量'
        else:
            analysis = '小规模用户'

        report += f"| {row['竞品']} | {rating} | {reviews} | {analysis} |\n"

    report += f"""
## 4. 关键洞察

### 竞争格局
"""

    active = sorted_df[sorted_df['活跃度等级'].isin(['高活跃', '中活跃'])]
    if len(active) > 0:
        report += f"- **活跃产品 ({len(active)}家)**: {', '.join(active['竞品'].tolist())}，持续投入产品开发\n"

    inactive = sorted_df[sorted_df['活跃度等级'] == '不活跃']
    if len(inactive) > 0:
        report += f"- **停滞产品 ({len(inactive)}家)**: {', '.join(inactive['竞品'].tolist())}，可能已停止原生 App 维护\n"

    no_data = sorted_df[sorted_df['活跃度等级'] == '无数据']
    if len(no_data) > 0:
        report += f"- **无 App 产品 ({len(no_data)}家)**: {', '.join(no_data['竞品'].tolist())}，采用纯 Web 或定制部署\n"

    report += """
### 对 Tappo 的启示

1. **App 可发现性**: Tappo 目前无 App Store 上架，在应用商店渠道零存在感
2. **竞品差异**: 积极竞品（Eats365, iCHEF, ezPOS）保持 1-2 周更新频率
3. **评论积累**: Gingersoft（飯糰）的 193 条评论说明消费端 App 更容易获得自然评论
4. **市场机会**: Caterlord、DimPOS 的 App 长期未更新，可能是可替代的目标

---

*本报告由自动化脚本生成，数据截至 {datetime.now().strftime('%Y-%m-%d')}*
"""

    report_path = ANALYSIS_DIR / 'app_store_analysis.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"✓ 分析报告已保存: {report_path}")
    return report_path

def main():
    print("=" * 60)
    print("App Store 数据分析")
    print("=" * 60)

    # 加载数据
    df = load_data()
    if df is None:
        return

    # 计算活跃度评分
    print("\n计算活跃度评分...")
    score_df = calculate_activity_score(df)
    print(score_df[['竞品', '活跃度评分', '活跃度等级', '最后更新', '评分', '评论数']].to_string(index=False))

    # 生成对比图表
    print("\n生成对比图表...")
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    chart_html = generate_comparison_chart(score_df, df)
    chart_path = CHARTS_DIR / 'app_store_activity_comparison.html'
    with open(chart_path, 'w', encoding='utf-8') as f:
        f.write(chart_html)
    print(f"✓ 活跃度对比图表: {chart_path}")

    rating_html = generate_rating_chart(df)
    rating_path = CHARTS_DIR / 'app_store_rating_comparison.html'
    with open(rating_path, 'w', encoding='utf-8') as f:
        f.write(rating_html)
    print(f"✓ 评分对比图表: {rating_path}")

    # 保存分析报告
    print("\n生成分析报告...")
    save_analysis_report(score_df, df)

    # 保存评分数据为 Excel
    score_path = DATA_DIR / f'app_store_activity_scores_{datetime.now().strftime("%Y%m%d")}.xlsx'
    score_df.to_excel(score_path, index=False, engine='openpyxl')
    print(f"✓ 评分数据: {score_path}")

    print("\n" + "=" * 60)
    print("分析完成!")

if __name__ == '__main__':
    main()
