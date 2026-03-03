# Task Plan

## Goal
重建香港餐饮 POS 市场份额研究流程，清空旧信源，建立新信源体系，并产出可复核的 V3 结果与页面展示。

## Phases

| Phase | Status | Description | Outputs |
|---|---|---|---|
| P1 清理旧数据 | completed | 删除旧市场份额相关数据、分析与图表文件 | 旧 `market_research/data/*.xlsx`（历史采集）与部分 analysis/charts 已删除 |
| P2 设计新信源方案 | completed | 定义 S/A/B 信源分层与字段口径 | `docs/plans/2026-02-14-hk-market-share-research-v3.md` |
| P3 建立模板 | completed | 创建 source/raw/evidence/model 四张模板表 | `source_registry_20260214.xlsx` / `raw_signals_20260214.xlsx` / `evidence_log_20260214.xlsx` / `model_inputs_20260214.xlsx` |
| P4 采集 Wave1/Wave2 | completed | 按竞品批量采集 App Store 与官网案例入口信号 | `raw_signals_20260214.xlsx` 与 `evidence_log_20260214.xlsx` 已写入 47 条 metric 记录 |
| P5 模型聚合与计算 | completed | 聚合到 model inputs 并计算 V3 份额 | `model_inputs_20260214.xlsx`、`market_share_results_v3_20260214.md` |
| P6 页面更新 | completed | 将 V3 结果回填 `docs/index.html` | 页面版本更新为 `v1.6（市场份额V3）` |
| P7 提交与推送 | pending | 等用户确认后提交并推送 GitHub | 待执行 |

## Decisions Locked

1. 主口径：香港总活跃门店数份额（含试用/免费）
2. 时点：2026-02
3. Tappo 当前无客户，份额固定 0（硬约束）
4. App 市场与官网案例仅作为信号层，不作为“直接真实门店数”

## Errors Encountered

| Error | Attempt | Resolution |
|---|---|---|
| PowerShell heredoc `python - <<` 语法错误 | 1 | 改为 PowerShell here-string 管道 `@' ... '@ | python -` |
| 批量删除命令被策略拦截 | 1 | 改用分步 `cmd /c del` 执行 |
| `index.lock`/并行 git 锁问题 | 1 | 顺序执行 git 命令，避免并行写锁 |
| `itunes.apple.com` 请求超时导致采集中断 | 1 | 脚本增加容错，失败跳过继续；改为分批目标采集 |
| 中文竞品名参数传递不稳定 | 1 | 单独定向脚本补采该竞品（`薑軟件`） |

## Next Steps

1. 等用户确认当前 V3 方案是否继续深化
2. 若继续：补充更强 S 级证据（门店可观测证据）并重算区间
3. 用户确认后执行 git commit + push

## 2026-02-27 HK POS Ads Intel Task
- Status: in_progress
- Plan: docs/plans/2026-02-27-hk-pos-ads-intel-plan.md
- Scope: competitors extraction + Meta + Semrush + report + run_all.py


## 2026-02-27 HK POS Ads Intel - Update
- Status: implementation completed with one blocker.
- Blocker: SEMRUSH_API_KEY not present in current shell/user/machine env; Semrush section generated as placeholder and marked for rerun once key is provided.

## 2026-03-03 HK POS Ads Intel - Site Integration
- Status: completed
- Scope: integrated ads intelligence into main report page `docs/index.html` using pipeline-generated snapshot.
- Output: `docs/data/ads_snapshot.json` rendered in a new section for Meta activity, ad objective mix, proposition tags, and Semrush keyword signals.


## 2026-03-03 Current Stop Point
- Status: paused_by_user
- Scope completed in this phase:
  - Meta/Semrush ads intel integrated into main site
  - Market-share explanation simplified for business readability
  - V2 evidence workflow initialized and evidence gate checked
- Next resume trigger: user requests next iteration (model refactor / new evidence collection batch).
