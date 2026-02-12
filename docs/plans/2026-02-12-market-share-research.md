# 香港餐饮 POS 市场占有率数据收集计划

> **For Claude:** REQUIRED SUB-SKILL: 使用 superpowers:executing-plans 来执行此计划任务

**Goal:** 通过多源数据交叉验证，估算 13 家香港餐饮 POS 竞品的市场占有率，为 Tappo 的竞争策略提供数据支撑

**架构:**
- 阶段化执行：5 个阶段，从易到难优先推进
- 数据源多样化：应用商店、招聘数据、社交媒体、支付平台、网站流量
- 交叉验证：多数据源结果相互校验，提高可信度
- 可视化输出：Excel 数据表 + 图表 + 综合报告

**Tech Stack:**
- 数据收集：浏览器（LinkedIn、官网、应用商店）、SimilarWeb（免费版）
- 数据整理：Microsoft Excel / Google Sheets
- 文档记录：Markdown（本文件）

---

## 阶段 0：项目初始化

### Task 0.1: 创建项目目录结构

**Files:**
- Create: `market_research/data/`
- Create: `market_research/analysis/`
- Create: `market_research/charts/`

**Step 1: 创建根目录**
```bash
cd "C:\Users\Administrator\Desktop\hk-pos-competitive-analysis"
mkdir -p market_research/{data,analysis,charts}
```

**Step 2: 创建数据收集表格**
```bash
# 在 market_research/data/ 目录下创建以下 Excel 文件
# 文件名格式：competitor_<data_type>.xlsx
```

**Step 3: 创建文档目录**
```bash
# 创建 market_research/data/README.md 说明数据字典和统计方法
```

---

## 阶段 1：应用商店与公开数据收集（优先级：⭐⭐⭐）

**时间预估:** 2-3 天
**数据源:** App Store、Google Play、SimilarWeb（免费版）

### Task 1.1: 创建竞品 APP 名称映射表

**Files:**
- Create: `market_research/data/competitor_apps.csv`
- Modify: `docs/index.html`（可选：更新矩阵为后续添加市场份额列）

**Step 1: 定义 CSV 表头**
```csv
竞品中文名,竞品英文名,App Store名称,App Store Bundle ID,Google Play包名,官网URL,LinkedIn URL,Facebook Page URL
```

**Step 2: 填充 13 家竞品 APP 映射**
```
Tappo → Gotappo / Tappo
Eats365 → Eats365 POS / HK Restaurateur
OmniWe → OmniWe POS / OmniWe
ROKA → eMenu
ezPOS → ezPOS 餐饮
iCHEF → iCHEF 餐飲
DimPOS → DimPOS
HCTC → HCTC 餐饮
Caterlord → Caterlord POS
DoLA → DoLA Technology
Gingersoft → 薑軟件 POS
Loyverse → Loyverse POS
```

**Step 3: 保存文件**
```bash
# 将 CSV 导入 Excel 并保存
```

---

### Task 1.2: 应用商店数据批量收集

**Files:**
- Modify: `market_research/data/app_downloads.xlsx`
- Modify: `market_research/data/app_ratings.xlsx`
- Modify: `market_research/data/app_activity.xlsx`
- Modify: `market_research/data/app_rankings.xlsx`

**Step 1: 访问 SimilarWeb 免费版**
```
URL: https://similarweb.com/
查询各竞品域名：
- omniwe.com
- eats365pos.com
- ezpos.hk
- roka.com.hk
- ichefpos.com
- dimorder.com
- 等 13 家
```

**Step 2: 收集 App Store 数据**
```
对于每个竞品：
1. 访问 App Store 页面（搜索 APP 名称）
2. 记录以下数据到 Excel：
   - 评分（1-5 星）
   - 评论总数
   - 下载量估算（SimilarWeb 显示）
   - 更新日期（最近版本发布时间）
   - 应用类别（Business/Food & Drink）
```

**Step 3: 收集 Google Play 数据（如适用）**
```
部分竞品可能只在 Android 市场：
- 重复相同数据收集流程
- 注意：Google Play 数据可能与 App Store 不一致
```

**输出格式:**
```xlsx
工作表: app_store_data
列: 竞品名称 | APP ID | 评分 | 评论数 | 下载量(估算) | 更新日期 | 应用类别
```

---

### Task 1.3: 应用活跃度评估

**Files:**
- Modify: `market_research/data/app_activity.xlsx`

**Step 1: 统计更新频率**
```
对于每个竞品，查看 App Store / Google Play:
1. 最近 30 天内的更新次数
2. 最近 90 天内的更新次数
3. 最近一次更新距今天数
```

**Step 2: 评估产品活跃度等级**
```
高活跃: 30 天 ≥ 3 次更新
中活跃: 30 天 ≥ 1 次更新
低活跃: 30 天 < 1 次更新
无更新: 超过 180 天未更新
```

**输出格式:**
```xlsx
工作表: app_activity
列: 竞品名称 | 30天更新次数 | 90天更新次数 | 最后更新距今天 | 活跃度等级
```

---

### Task 1.4: 应用商店排名追踪

**Files:**
- Modify: `market_research/data/app_rankings.xlsx`

**Step 1: 查询当前排名**
```
在 App Store / Google Play Business 类别中：
1. 搜索 "restaurant POS"、"餐飲"
2. 记录各竞品的当前排名位置
3. 截图保存（作为时间点证据）
```

**Step 2: 记录排名变化**
```
如有可能，查询历史排名工具：
1. 记录过去 3-6 个月的排名变化
2. 标注重要事件（如新版本发布、促销活动）
```

**输出格式:**
```xlsx
工作表: app_rankings
列: 竞品名称 | 当前排名 | 30天前排名 | 90天前排名 | 排名变化趋势
```

---

## 阶段 2：招聘与公司规模数据（优先级：⭐⭐⭐）

**时间预估:** 1 天
**数据源:** LinkedIn、公司官网、招聘网站

### Task 2.1: LinkedIn 员工规模统计

**Files:**
- Create: `market_research/data/company_size.xlsx`

**Step 1: 访问各竞品 LinkedIn 页面**
```
URL 映射：
Tappo: 搜索（非上市公司，可能无 LinkedIn）
Eats365: 搜索公司页面
OmniWe: omniwe.com
ROKA: ROKA Service
ezPOS: 搜索公司
iCHEF: iCHEF 餐飲
...
```

**Step 2: 记录员工数据**
```xlsx
列: 竞品名称 | LinkedIn URL | 总员工数 | 餐饮业务员工估算 | 招聘岗位数 | 数据日期
```

**Step 3: 估算餐饮业务占比**
```
判断标准（基于岗位描述）：
- 明确标注 "餐饮"、"餐厅"、"F&B" 的岗位 → 计入餐饮业务
- 标注 "零售"、"电商" 的岗位 → 不计入
- 标注 "销售"、"客户经理" → 按产品线分配（如 70% 餐饮，30% 零售）
```

---

### Task 2.2: 岗位分布分析

**Files:**
- Create: `market_research/data/roles_breakdown.xlsx`

**Step 1: 统计各职能部门员工数**
```
在 LinkedIn 页面记录：
- 研发（R&D）
- 销售（Sales）
- 客服（Customer Service）
- 运营（Operations）
- 市场（Marketing）
```

**Step 2: 计算组织架构对比**
```xlsx
列: 竞品名称 | 研发% | 销售% | 客服% | 运营% | 市场%
```

**推断:**
- 重研发、轻销售 = 产品导向
- 重销售、轻研发 = 销售驱动
- 重客服 = 服务导向

---

### Task 2.3: 招聘活跃度追踪

**Files:**
- Create: `market_research/data/recruitment_activity.xlsx`

**Step 1: 统计招聘岗位数量**
```
在 LinkedIn Jobs / 招聘网站查询：
1. 近 1 个月发布的餐饮相关岗位数
2. 近 3 个月发布的岗位数
3. 招聘地区分布（香港/跨境）
```

**Step 2: 评估业务扩张速度**
```
招聘活跃度等级：
快速扩张: 月均 ≥ 5 个新岗位
稳定增长: 月均 2-4 个岗位
缓慢增长: 月均 < 2 个岗位
收缩: 月均 0 个岗位，且有裁员
```

---

### Task 2.4: 地理分布验证

**Files:**
- Create: `market_research/data/geo_presence.xlsx`

**Step 1: 检查办公室分布**
```
通过 LinkedIn / 官网 "About Us" 页面：
1. 香港办公室数
2. 中国内地办公室数
3. 海外办公室（东南亚、台湾等）
4. 是否列出"服务网点"
```

**Step 2: 评估市场聚焦度**
```
本地化: 仅香港办公室
区域化: 香港 + 中国华南
国际化: 3+ 国家/地区办公室
```

---

## 阶段 3：线上活跃度与客户案例（优先级：⭐⭐⭐）

**时间预估:** 1-2 天
**数据源:** 官网、Google Images、Facebook、Instagram

### Task 3.1: 客户案例统计

**Files:**
- Create: `market_research/data/customer_cases.xlsx`

**Step 1: 浏览各官网"案例"、"客户"、"合作伙伴"版块**
```
统计方法：
1. 大客户案例：展示 logo + 名称
2. 中小客户案例：只计数不记名
3. 行业解决方案案例：如"某某茶餐厅集团"
4. 政府/教育机构客户
```

**Step 2: Google Images 验证**
```
搜索 "[竞品名] + 客户 logo + 餐饮"
下载可见的客户 logo 图片，计数验证
```

**Step 3: 案例质量评估**
```
质量等级：
高质量: 知名连锁品牌（如麦当劳、美心）
中质量: 本地知名餐厅
低质量: 仅展示行业，无具体名称
```

---

### Task 3.2: 社交媒体活跃度

**Files:**
- Create: `market_research/data/social_followers.xlsx`
- Create: `market_research/data/social_activity.xlsx`

**Step 1: Facebook Page 数据收集**
```
URL 映射：
Eats365: facebook.com/Eats365HK
OmniWe: 搜索官方页面
ROKA: facebook.com/emenu.hk
ezPOS: 搜索官方页面
...
```

记录数据：
- 粉丝数（Followers）
- 点赞数（Page Likes）
- 最近 30 天发帖数
- 内容类型分布（产品介绍 vs. 活动促销）

**Step 2: Instagram 数据收集**
```
记录：
- 粉丝数
- 帖文频率
- Hashtag 使用
```

**Step 3: LinkedIn 公开数据**
```
记录：
- 公司主页关注者
- 帖文互动率
- 员工活跃度（发帖、分享）
```

---

### Task 3.3: 网站流量对比

**Files:**
- Create: `market_research/data/web_traffic.xlsx`

**Step 1: 使用 SimilarWeb 免费版查询**
```
已包含在阶段 1.2，但需要深入分析：
1. 总访问量
2. 独特访客数
3. 访问来源（搜索、直接、外链、社交媒体）
4. 停留时间
5. 跳出率
```

**Step 2: 计算流量占比**
```
方法 A: 简单占比
  该竞品流量 / 13 家总流量

方法 B: 加权占比
  总流量 × (域名权重 0.8 + 直接访问权重 1.2)
```

**Step 3: SEO 竞争度**
```
查询关键词：
- "香港 POS 系统"
- "餐厅收银系统"
- "餐饮管理软件"
记录各竞品排名位置
```

---

## 阶段 4：支付平台商户渗透（优先级：⭐⭐⭐）

**时间预估:** 2-3 天
**数据源:** 八达通、PayMe、支付宝 HK

### Task 4.1: 八达通商户统计

**Files:**
- Create: `market_research/data/octopus_merchants.xlsx`

**Step 1: 八达通商户目录浏览**
```
访问：https://www.octopus.com.hk/octopus-customer/enrollment/
搜索标签：餐饮、Restaurant、F&B
过滤条件：
- 显示 "POS"、"收银" 系统的商户
- 排除 "仅支付" 的商户
```

**Step 2: 各 POS 厂商商户计数**
```
统计方法：
1. 搜索 "Eats365" - 记录商户数
2. 搜索 "OmniWe" - 记录商户数
3. 搜索 "ROKA" / "eMenu" - 记录商户数
4. 搜索 "ezPOS" - 记录商户数
5. 对比各厂商的商户数量
```

**注意事项:**
- 八达通可能按"终端"显示，需人工验证是否 POS 系统
- 记录统计日期（商户数会变化）
- 拍照/截图存证

---

### Task 4.2: PayMe from HSBC 商户统计

**Files:**
- Create: `market_research/data/payme_merchants.xlsx`

**Step 1: 浏览 F&B 商户类别**
```
访问 PayMe 商户目录（如有）或通过商户搜索
统计各 POS 接入的商户数量
```

**Step 2: 验证商户真实性**
```
抽查方法：
1. 随机选择 10 个商户
2. Google Maps 搜索验证是否真实餐厅
3. 电话确认是否在使用该 POS 系统
```

---

### Task 4.3: 支付宝 HK 商户统计

**Files:**
- Create: `market_research/data/alipay_merchants.xlsx`

**Step 1: 支付宝 HK 生活号搜索**
```
搜索标签：餐饮、Restaurant
统计各 POS 接入商户
```

**Step 2: 交叉验证**
```
对比三个支付平台的商户列表：
- 去重处理（同一商户多支付）
- 识别高频商户（可能使用多种 POS）
- 估算独立商户数
```

**Step 3: 计算渗透率**
```
渗透率定义：
该 POS 厂商商户数 / 香港餐饮商户总数 × 100%

注意：香港餐饮商户总数约 15,000-17,000 家（需查证）
```

---

### Task 4.4: 支付平台汇总

**Files:**
- Create: `market_research/data/payment_platform_summary.xlsx`

**Step 1: 整合三个支付平台数据**
```xlsx
工作表: payment_comparison
列: POS厂商 | 八达通商户 | PayMe商户 | 支付宝商户 | 合计去重 | 渗透率估算
```

**Step 2: 计算市场份额**
```
方法：
渗透率 × 权重（假设支付平台数据权重 40%）
与其他数据源加权平均
```

---

## 阶段 5：数据整合与市场份额估算（优先级：⭐⭐⭐）

**时间预估:** 1-2 天
**依赖:** 阶段 1-4 全部完成

### Task 5.1: 创建综合对比表

**Files:**
- Create: `market_research/analysis/market_share_master.xlsx`

**Step 1: 数据标准化**
```
对所有指标进行 Min-Max 标准化（0-100 分）：
下载量 → 标准化
员工数 → 标准化
客户案例数 → 标准化
社交媒体粉丝 → 标准化
网站流量 → 标准化
支付商户数 → 标准化
```

**Step 2: 设定权重**
```
权重分配（总和 = 100%）:
- 应用商店数据: 30%（下载量、活跃度）
- 招聘规模: 25%（员工数、餐饮业务占比）
- 线上活跃度: 20%（客户案例、社交粉丝）
- 支付平台: 15%（商户渗透率）
- 网站流量: 10%（SimilarWeb 访问量）

理由：
- 应用数据反映实际使用
- 招聘规模最直接反映业务体量
- 社交和客户反映品牌影响力
- 支付平台是最直接商户验证
- 网站流量可作为辅助验证
```

**Step 3: 计算综合得分**
```excel
列: 竞品名称 | 应用得分(30%) | 招聘得分(25%) | 线上得分(20%) | 支付得分(15%) | 流量得分(10%) | 综合得分 | 市场份额
```

**市场份额计算:**
```
市场份额 = 该竞品综合得分 / (所有竞品综合得分总和)
```

---

### Task 5.2: 置信度评估

**Files:**
- Create: `market_research/analysis/confidence_assessment.md`

**Step 1: 数据质量评级**
```
高置信度:
- 3 个以上数据源一致
- 有外部基准可对齐
- 数据新鲜（30 天内）

中置信度:
- 2-3 个数据源一致
- 部分数据需推断
- 数据较新鲜（3 个月内）

低置信度:
- 仅 1 个数据源
- 大量推断和假设
- 数据陈旧（6 个月以上）
```

**Step 2: 不确定性说明**
```
明确标注:
- Tappo: 无法获取数据（非上市公司）
- 小型竞品: 可能无 LinkedIn 或应用数据
- 支付平台: 商户重复计数问题

建议后续验证:
- 试用/演示时询问商户使用的 POS 系统
- 客户访谈验证
- 行业专家咨询
```

---

### Task 5.3: 可视化

**Files:**
- Create: `market_research/charts/download_comparison.png`
- Create: `market_research/charts/market_share_pie.png`
- Create: `market_research/charts/employee_comparison.png`
- Create: `market_research/charts/radar_chart.png`

**Step 1: 下载量对比图**
```
图表类型: 横向柱状图
X 轴: 13 家竞品
Y 轴: 下载量（应用商店 SimilarWeb）
颜色编码: 高(绿) / 中(蓝) / 低(红)
```

**Step 2: 市场份额饼图**
```
图表类型: 饼图
数据: 综合得分计算的市场份额
突出显示: Tappo vs. 主要竞品
```

**Step 3: 员工规模对比**
```
图表类型: 横向柱状图
X 轴: 13 家竞品
Y 轴: 总员工数（区分餐饮业务）
颜色编码: 大型(绿) / 中型(蓝) / 小型(红)
```

**Step 4: 多维度雷达图**
```
图表类型: 雷达图
维度: 应用下载量 | 员工规模 | 客户案例 | 社交粉丝 | 网站流量 | 支付渗透
目的: 展示各竞品的综合竞争力轮廓
```

---

## 执行清单

### 阶段 0（项目初始化）
- [ ] 创建 market_research 目录结构
- [ ] 创建空的 Excel 模板文件
- [ ] 创建 data/README.md 说明文档

### 阶段 1（应用商店数据）
- [ ] 创建 competitor_apps.csv 映射表
- [ ] 收集 App Store 数据（下载量、评分、评论）
- [ ] 收集 Google Play 数据（如适用）
- [ ] 统计应用更新频率（活跃度）
- [ ] 记录应用商店排名

### 阶段 2（招聘数据）
- [ ] LinkedIn 员工统计（总数+餐饮业务占比）
- [ ] 岗位分布分析（研发/销售/客服/运营）
- [ ] 招聘活跃度统计（近 1/3 个月岗位数）
- [ ] 地理分布验证（办公室位置）

### 阶段 3（线上活跃度）
- [ ] 官网客户案例统计（计数+质量评估）
- [ ] Facebook/Instagram 粉丝数和活跃度
- [ ] LinkedIn 公开数据收集
- [ ] SimilarWeb 网站流量深入分析

### 阶段 4（支付平台）
- [ ] 八达通商户统计（各 POS 接入商户数）
- [ ] PayMe 商户统计
- [ ] 支付宝 HK 商户统计
- [ ] 交叉验证和去重
- [ ] 计算渗透率

### 阶段 5（整合分析）
- [ ] 数据标准化和权重分配
- [ ] 计算综合得分和市场份额
- [ ] 置信度评估
- [ ] 创建可视化图表
- [ ] 编写最终市场研究报告

---

## 完成标准

**阶段完成定义:**
- 所有任务项 100% 完成
- 数据已整合到 master 表
- 图表已生成并导出
- 置信度文档已编写

**交付物:**
1. `market_research/data/` - 所有原始数据表
2. `market_research/analysis/market_share_master.xlsx` - 综合对比表
3. `market_research/analysis/confidence_assessment.md` - 置信度说明
4. `market_research/charts/` - 所有可视化图表
5. `market_research/README.md` - 研究总结报告

---

## 后续 Semrush 整合说明

**当前状态:** 等待用户提供 Semrush 工具

**整合计划:**

**阶段 6: Semrush 深化分析**

### Task 6.1: 流量数据补充
```
使用 Semrush 重新查询各竞品官网流量：
- Organic vs. Paid 流量比例
- 关键词排名（"香港 POS"、"餐饮收银"）
- 反向链接数量（Backlinks）
- 竞争对手流量对比（Traffic Comparison）
```

### Task 6.2: 数据交叉验证
```
对比 Semrush 流量数据与应用商店下载量：
- 识别异常（下载高但流量低 = 可能刷榜）
- 验证相关性（流量占比应接近下载量占比）
- 调整综合模型中的权重
```

### Task 6.3: 发现遗漏竞品
```
使用 Semrush Market Explorer:
- 查询 "Restaurant POS Hong Kong" 相关域名
- 发现未覆盖在现有列表中的小型竞品
- 评估是否需要纳入分析
```

---

## 风险与限制

**数据局限性:**
1. 非上市公司数据缺失（Tappo 可能无公开财报）
2. 小型竞品可能无 LinkedIn/App 数据
3. 应用商店数据包含个人用户下载（高估）
4. 支付平台商户重复计数问题
5. 所有方法均为估算，非官方统计数据

**缓解措施:**
1. 多数据源交叉验证
2. 标注置信度
3. 明确假设前提
4. 建议后续验证方法（客户访谈、行业咨询）

---

## 参考资料

**工具资源:**
- SimilarWeb 免费版: https://similarweb.com/
- App Store: https://apps.apple.com/hk/
- Google Play: https://play.google.com/store
- LinkedIn: https://www.linkedin.com/
- 八达通商户: https://www.octopus.com.hk/

**竞品官网列表:**
- Tappo: https://www.gotappo.com/
- Eats365: https://www.eats365pos.com/hk/
- OmniWe: https://omniwe.com/
- ROKA: https://www.roka.com.hk/
- ezPOS: https://www.ezpos.hk/
- iCHEF: https://www.ichefpos.com/zh-hk/
- DimPOS: https://www.dimorder.com/dimpos/
- HCTC: https://posapp.hctc.com.hk/
- Caterlord: https://caterlord.com/zh-hant/
- DoLA: https://www.dolatechnology.com/zh
- Gingersoft: https://clggroup.com.hk/hk/fbPos
- Loyverse: https://loyverse.com/

---

**保存位置:** `docs/plans/2026-02-12-market-share-research.md`

**下一步:** 立即执行阶段 1（应用商店数据收集）开始项目
