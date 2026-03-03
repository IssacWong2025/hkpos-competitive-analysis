# 香港餐饮 POS 竞品分析（静态站点）

- 最新版入口：`docs/index.html`（GitHub Pages 会发布它）
- 历史版本：`docs/versions/`
- 项目背景与维护规则：`AGENTS.md`

## 广告情报一键产出

运行：

```powershell
cd "C:\Users\Administrator\Desktop\hk-pos-competitive-analysis"
python scripts/run_all.py
```

可选参数：

```powershell
python scripts/run_all.py --database hk --display-limit 200 --dry-run-count 3
```

输出文件：

- `data/competitors_master.csv`
- `data/meta_ads_intel.csv`
- `data/meta_ads_todo.csv`
- `data/meta_copy_keywords.csv`
- `data/semrush_google_ads_signals.csv`
- `reports/hk_competitor_ads_summary.md`
- `docs/data/ads_snapshot.json`（供 `docs/index.html` 的“增长投放情报”章节自动渲染）
- `output/run_all.log`

## Semrush Units 控制

- API key 只从环境变量读取：`SEMRUSH_API_KEY`
- 禁止把 key 写入代码或仓库
- `display_limit` 默认 `200`，脚本限制上限 `300`
- 脚本按两段执行：先 dry-run 3 个域名，再批量跑剩余域名
- 脚本会记录 `units_before` / `units_after`
- 若环境变量缺失，脚本会生成占位结果并在日志标记 `missing_semrush_api_key`

PowerShell 设置临时环境变量示例：

```powershell
$env:SEMRUSH_API_KEY = "<your_key>"
python scripts/run_all.py
```

## Meta 手工补全（轻量流程）

当 `meta_ads_intel.csv` 中 `collection_method=manual_needed` 时：

1. 打开 `data/meta_ads_todo.csv` 的 `ad_library_url`
2. 在 Meta Ad Library 记录：
   - 活跃广告数
   - 代表广告文案（primary text/headline/CTA）
   - 落地页或 WhatsApp/Messenger 入口
3. 回填到 `data/meta_ads_intel.csv` 对应行
4. 重新运行 `python scripts/run_all.py` 更新关键词统计和报告

说明：Meta Ad Library 有动态渲染与访问限制，脚本提供半自动采集 + 容错待办，不承诺 100% 自动成功。

手工补全重点字段（至少）：
- `call_to_action`
- `landing_page_url` 或 `message_destination_hint`（`whatsapp` / `messenger` / `website`）
- `objective_path_hint` 与 `objective_reason`
- `status`（建议填 `active`）和 `ad_count_active`（可填观察到的数量）

执行位置：
- 你只需要编辑：`data/meta_ads_todo.csv`
- 不要手改 `data/meta_ads_intel.csv`（它由脚本自动合并更新）

回填后更新结果：

```powershell
cd "C:\Users\Administrator\Desktop\hk-pos-competitive-analysis"
python scripts/run_all.py
```

脚本会把你在 `meta_ads_todo.csv` 的人工字段合并到 `meta_ads_intel.csv`，并更新报告中：
- `Active (confirmed)`（来自手工/自动确认）
- `Likely Active (blocked/needs manual confirm)`（自动被阻断但疑似在投）

## 数据质量自检

每次运行后做以下检查：

```powershell
Import-Csv data/competitors_master.csv | ? { -not $_.facebook_page_url -and -not $_.instagram_handle } | ft competitor_name,website_domain
Import-Csv data/meta_ads_todo.csv | ft competitor_name,error_reason,manual_required_fields
Import-Csv data/semrush_google_ads_signals.csv | ft competitor_name,paid_keywords_count,units_before,units_after
```

判定标准：
- 社媒覆盖率（Facebook/Instagram）目标 >= 80%
- `meta_ads_todo.csv` 中条目可被人工补全 CTA + 目标路径
- Semrush units 字段不能留空；不可用时应显示 `unavailable:<reason>`

## 回滚方式

如本次采集结果不理想，可回滚到上一个稳定版本：

```powershell
git log --oneline -n 5
git checkout <stable_commit_hash> -- data reports scripts/run_all.py README.md
```

## 发布到 GitHub Pages（同事无需 GitHub 账号）

1. 在 GitHub 新建 **Public** 仓库（例如 `hk-pos-competitive-analysis`）。
2. 本地推送本仓库到 GitHub：

```powershell
cd "C:\Users\Administrator\Desktop\hk-pos-competitive-analysis"
git init
git add -A
git commit -m "publish v1.1"
# 把下面 URL 换成你自己的仓库地址
git remote add origin https://github.com/<you>/<repo>.git
git branch -M main
git push -u origin main
```

3. GitHub 仓库里：`Settings -> Pages`

- Source: `Deploy from a branch`
- Branch: `main`
- Folder: `/docs`

保存后等待 1-2 分钟，会得到一个网址，发给同事直接打开即可。

## 自动发布（可选）

```powershell
cd "C:\Users\Administrator\Desktop\hk-pos-competitive-analysis"
.\scripts\watch-publish.ps1
```
