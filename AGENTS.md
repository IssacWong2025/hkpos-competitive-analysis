# Project Brief: HK POS Competitive Analysis (Tappo)

## What This Repo Is

This repo hosts a **single-page HTML competitive analysis report** for Hong Kong restaurant POS, intended for **internal alignment** (Product, Ops, Marketing).

It is published as a static site via **GitHub Pages** from `docs/`.

## Audience / Use

- Primary: internal stakeholders who want a quick, evidence-linked view of the landscape
- Style: information organization first; avoid over-claiming
- Consumption: open a URL; no GitHub account required

## Our Product

- Name: **Tappo** (not “Gotappo”)
- Positioning notes (high-level): usage-based billing, no hardware + long contract, quick onboarding, monthly cap

## Target ICP (Default Assumption)

- Hong Kong, **single-store fast food / cha chaan teng**
- Owner/manager not too old, sees digital value, can self-learn basic software operation

## Competitive Set (Must Not Shrink)

Core direct competitors (priority in updates):
- **Eats365**
- **ezPOS**
- **ROKA**
- **OmniWe**

Rule: competitors can be added, but **do not remove** existing ones (except explicitly requested removals like `e-POSHK`, which is already removed).

## Report Mechanics (How To Maintain Correctness)

### Feature Matrix Status Legend

In `docs/index.html` feature matrix:
- `Y`: public evidence found (link in cell)
- `P`: partial/limited or weaker inference (still linked)
- `U`: no public evidence found yet (not “doesn't have”)
- `N`: for **Tappo only**, inferred “not supported yet” based on *absence of public evidence*; used for internal gap alignment

### Gap View Logic

The section “差距视图（Tappo 暂不支持 vs 竞品证据）” is auto-generated from the feature matrix:
- pick rows where `Tappo = N`
- show competitors where `status in {Y,P}` and the cell includes a source link

Do not maintain the gap table manually; fix the feature matrix and let the JS rebuild it.

### Evidence Policy

- Prefer official public sources: product pages, pricing pages, help centers, app stores
- “Supplementary channels” means: **use them to reduce `U`**, not to list the channels in the report
- Avoid turning marketing slogans into factual claims without clear wording on the page

## Repo Structure

- `docs/index.html`: the live report (GitHub Pages serves this)
- `docs/versions/`: archived historical HTML snapshots
- `scripts/publish.ps1`: stage+commit+push helper
- `scripts/watch-publish.ps1`: watch `docs/index.html` and auto commit+push on save

## Publishing

GitHub Pages:
- branch: `main`
- folder: `/docs`

Automation:
- run `.\scripts\watch-publish.ps1` while editing to auto-publish updates

## Current Priorities (Next Iteration Ideas)

- Reduce remaining `U` for core competitors (especially OmniWe / ROKA / ezPOS) using official sources
- Keep the matrix readable (sticky capability column, consistent hints, working links)
- Keep “Tappo supported” grounded strictly in Tappo public info; avoid internal assumptions

