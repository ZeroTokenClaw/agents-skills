---
name: calc-analysis-skills
description: >-
  Use when computing, analyzing data, writing Excel formulas, doing statistics,
  financial models, scientific numerics, or choosing among math/data skills.
  Trigger on 计算、公式、统计、数据分析、财务模型、SymPy、pandas、numpy、DCF、
  算账、单位换算、数值计算。
---

# 计算 / 分析 Skills 详细路由

先读本 skill，再打开目标 `SKILL.md`。配套总表：`practical-skills-index`。

## 1. 数学与符号计算

| 意图 | Skill | 能力要点 |
| --- | --- | --- |
| 解方程 / 积分 / 特征值 / 证明检查 | `math`（parcadei） | SymPy 求解、Z3、Pint 单位换算；统一入口 |
| 数值货币 / 精度敏感加减乘除 | `decimal-js` | 避免浮点误差（金额、税率） |
| 统计基础 | `statistics-fundamentals` | 描述统计、推断入门 |
| 科研向统计表述 | `nature-statistics` | 论文级统计写法与检验习惯 |
| 工程师向统计+数学 | `statistics-math` | 数据工程场景的统计数学 |

**规则：** 符号推导 → `math`；金额/汇率 → `decimal-js` + `xlsx`；论文统计措辞 → `nature-statistics`。

## 2. 表格公式与电子表

| 意图 | Skill | 能力要点 |
| --- | --- | --- |
| 写/修 Excel·Sheets 公式 | `spreadsheet-formula-helper` | 动态数组、`LET`/`LAMBDA`、跨 Excel/Sheets 方言 |
| 生成/编辑 xlsx 文件 | `xlsx`、`xlsx-author` | 结构化表格与财务表输出 |
| 通用表格工作流 | `excel`、`spreadsheets` | 办公自动化向 |
| 复杂财务三表 | `3-statement-model` | 损益/资产负债/现金流勾稽 |
| DCF 估值模型 | `dcf-model` | 折现现金流建模 |

**规则：** 「帮我写个 SUMIFS」→ `spreadsheet-formula-helper`；「做一个可打开的 xlsx」→ `xlsx` / `xlsx-author`。

## 3. 数据分析

| 意图 | Skill | 能力要点 |
| --- | --- | --- |
| 通用数据分析 | `data-analysis` | 清洗、汇总、洞察（office 栈） |
| EDA 探索分析 | `exploratory-data-analysis` | 分布、缺失、相关、可视化起点 |
| Jupyter 笔记本分析 | `data-analysis-jupyter` | notebook 流程 |
| NumPy 数值数组 | `numpy-best-practices` | 向量化、广播、性能 |
| 科学计算栈 | `scientific-computing` | 科研数值工作流 |
| 学术工具箱 | `scientific-toolkit-skill` | 学术计算工具集合 |

**规则：** 有 CSV/表要结论 → `data-analysis` 或 `exploratory-data-analysis`；写 Python 数值码 → `numpy-best-practices` + `scientific-computing`。

## 4. 财务建模

| 意图 | Skill | 能力要点 |
| --- | --- | --- |
| 通用财务建模 | `financial-modeling` | 假设、驱动、情景 |
| 创业财务模型 | `startup-financial-modeling` | 融资/增长假设表 |
| 三报表 | `3-statement-model` | 勾稽与预测 |
| DCF | `dcf-model` | 估值 |

**规则：** 先定模型类型再开 skill；输出优先落到 `xlsx` / `xlsx-author`。

## 5. 执行清单（任意计算任务）

1. 明确：符号 / 数值 / 表格公式 / 财务模型 / 统计检验
2. 选上表对应 skill 并 **Read SKILL.md**
3. 金额类强制十进制或表格单元格格式，禁止裸 float 累加
4. 公式类给出：主公式 + 2–3 行样例输入输出 + 边界（空值/重复）
5. 分析类给出：假设 → 方法 → 数字结果 → 局限
6. 需要可交付文件时接 `xlsx` / `pdf` / `pptx`

## 禁止

- 未读 skill 就编造 SymPy/Excel 方言细节
- 用近似浮点直接报「精确金额」
- 财务模型不写清假设与单位（元/%/年）
