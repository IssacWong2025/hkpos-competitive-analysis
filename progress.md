# Progress Log

## 2026-02-14

### Completed

1. 清理旧信源数据与旧分析产物（data/analysis/charts 多文件删除）。
2. 新建 V3 研究计划：`docs/plans/2026-02-14-hk-market-share-research-v3.md`。
3. 创建四张新模板表：
   - `source_registry_20260214.xlsx`
   - `raw_signals_20260214.xlsx`
   - `evidence_log_20260214.xlsx`
   - `model_inputs_20260214.xlsx`
4. 完成 Wave1/Wave2 采集脚本并执行：
   - `scripts/collect_wave1_v3.py`
   - `scripts/collect_wave2_v3.py`
5. 完成聚合与计算：
   - `scripts/build_model_inputs_v3.py`
   - `scripts/calculate_market_share_v3.py`
6. 结果文档已生成：
   - `market_research/analysis/market_share_results_v3_20260214.md`
7. 页面已更新：
   - `docs/index.html` 增加 “市场份额 V3（重建信源）” 区块，版本号更新为 `v1.6`。

### In Progress

1. 等用户确认是否以当前 V3 作为对外/对内版本。
2. 若继续增强说服力，下一步切换到“样本门店可观测证据法”。

### Pending

1. Git 提交与推送（用户确认后执行）。

## 2026-02-27
- Created plan: docs/plans/2026-02-27-hk-pos-ads-intel-plan.md
- Next: write failing tests for scripts/run_all.py output contracts.


## 2026-02-27 HK POS Ads Intel
- Added: scripts/run_all.py
- Added tests: tests/test_run_all.py (3 passing tests)
- Generated outputs under data/, reports/, output/.
- Updated README with run instructions, Meta manual completion steps, Semrush unit controls.
- Verification: python -m unittest tests/test_run_all.py -v (PASS), python scripts/run_all.py (PASS with Semrush key-missing placeholder mode).

## 2026-03-03 Ads Intel Integration into Main Site
- Integrated a new section in `docs/index.html`: `增长投放情报（Meta 为主，Google 为辅）`.
- Added automated snapshot output in `scripts/run_all.py`: `docs/data/ads_snapshot.json`.
- The main site now renders ad intelligence directly from pipeline output:
  - who is advertising on Meta (with Ad Library links),
  - objective distribution,
  - proposition tags,
  - Google paid keyword signals.
- Ran `python scripts/run_all.py --skip-semrush` to refresh data and snapshot without extra Semrush unit consumption.

## 2026-03-03 Project Status Freeze
- Updated main report date in `docs/index.html` to `2026-03-03`.
- Market-share section now keeps final assessment output and plain-language method explanation only.
- Ads intelligence + V2 source workflow have been integrated; this version is a temporary stop point for next planning cycle.

