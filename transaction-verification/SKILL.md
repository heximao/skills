---
name: transaction-verification
description: This skill should be used when the user asks to "核对交易记录", "检查交易文件", "verify transactions", "audit trade files", "check YAML metadata", or "recalculate costs". It verifies naming conventions, checks YAML schemas, validates values, performs mathematical checks, and recalculates average costs.
version: 1.0.0
---

# 交易记录核查与校验规范 (Transaction Record Verification and Audit Specification)

负责核对、验证、审计和核算所有存在于 `us-stocks/`、`a-shares/`、`hk-stocks/`、`currency-exchange/`、`transfer/` 及 `Holdings_Snapshots/` 等目录中的交易记录文件，确保其命名、元数据结构和数值逻辑完全符合本库标准。

---

## 核心核查流程 (Core Verification Workflow)

对任何交易记录的核核检查必须严格按照以下四个步骤进行，并生成详细的检测报告。

### 第一步：文件名校验 (Filename Validation)

检查目标文件或待创建文件的文件名是否符合分类规范。

1. **基本格式核对**：
   - 股票/ETF 交易：`YYYY-MM-DD_Broker_Symbol_TradeID_Side.md`
     - 示例：`2025-03-17_VB_AAPL_T001_Buy.md`
   - 期权交易：`YYYY-MM-DD_Broker_SymbolExpiryTypeStrike_TradeID_Side.md`
     - 示例：`2025-03-28_LB_NVDA20250328Put109000_T001_BuyOpen.md`
     - **行权价特殊校验**：文件名中行权价整数部分后必须填充三个零（如 `109` 写为 `109000`）。
   - 出入金与转账：`YYYY-MM-DD_Broker_Currency_Amount_Deposits.md` / `YYYY-MM-DD_Broker_Currency_Amount_Withdrawals.md`
     - **金额特殊校验**：文件名中的金额必须是 YAML 元数据中 `金额` 字段向下取整后的整数。
     - 示例：YAML 中 `金额: 8.39`，文件名必须为 `..._8_Withdrawals.md`。
   - 外汇兑换：每笔兑换生成两个文件，分别为 `_FX_Sent.md` 和 `_FX_Received.md`。
     - 示例：`2026-01-16_IB_USDHKD_FX_Sent.md` 与 `2026-01-16_IB_USDHKD_FX_Received.md`。

2. **简码合规性核对**：
   - 券商必须属于以下标准简码之一：
     - `LB`（长桥证券）
     - `IB`（盈透证券）
     - `VB`（华盛证券）
     - `DFCF`（东方财富证券）
     - `HB`（华宝证券）
     - `CS`（嘉信理财）
   - 银行或兑换机构简码：
     - `XY`（兴业银行）
     - `ICBC`（工商银行）

3. **代码大小写和前缀核对**：
   - 股票代码必须为全大写字母（美股如 `NVDA`）或规定长度的纯数字（港股如 `'02605'`，A股如 `'600519'`）。
   - 计划或挂单文件必须带 `计划_` 前缀。
     - 示例：`计划_2027-02-12_LB_AAPL_T005_Buy.md`。

---

### 第二步：YAML Frontmatter 校验 (YAML Frontmatter Audit)

读取文件元数据，核对所有声明的键值对。

1. **硬约束：禁止使用英文键名**：
   - YAML 中的所有键名必须使用中文，严格参照 `template/中英文名词对照.md`。
   - 正确：`时间`、`券商`、`证券代码`、`数量`、`成交价`、`手续费`、`交易编号`。
   - 错误：`date`、`broker`、`symbol`、`quantity`、`price`、`fee`、`trade_id`。
   - *例外*：仅限于 `.github/agents/*.agent.md` 和 `.claude/skills/*/SKILL.md` 可使用标准英文键名。

2. **必填及类型格式校验**：
   - **时间**：强制采用 ISO 8601 格式，如 `2026-03-27T10:30:00`。
   - **市场**：必须属于 `us-stocks`、`a-shares`、`hk-stocks`、`crypto` 之一。
   - **证券代码**：
     - 港股和A股的纯数字代码必须用**单引号或双引号**包裹（如 `'02833'`、`"510900"`），防止解析器将其当作数字截断。
   - **动作**：必须属于允许的值：
     - 股票：`买入`、`卖出`、`股息`、`分红`、`拆股`
     - 期权：`买入开仓`、`卖出开仓`、`买入平仓`、`卖出平仓`
     - 出入金：`入金`、`出金`
     - 外汇兑换：`出账`、`入账`
   - **金额正数原则**：
     - **元数据中的 `金额` 和 `手续费` 强制必须为正数**。绝对不允许在元数据中记录负值，方向由 `动作` 决定。

---

### 第三步：数学与计算一致性核查 (Mathematical Consistency Checks)

核实各数值指标在数学逻辑上是否自洽。

1. **基本金额计算公式核查**：
   - 公式：`金额 = 成交价 × 数量`
   - 允许的尾数误差：成交价 × 数量 与 元数据中记录的“金额”差值必须在 `< 0.5` 范围内（由于交易所四舍五入或佣金分摊，允许极小误差）。
   - 如果差值 `≥ 0.5`，必须输出警告并提示修正。

2. **交叉校验外汇兑换汇率**：
   - 外汇兑换的 `_FX_Sent` 文件与 `_FX_Received` 文件对应的金额与实际汇率必须交叉验证：
     - 汇率公式：`实际汇率 = Received金额 / Sent金额` （或倒数，根据货币对定义）
     - 检测两文件元数据声明的 `汇率`、`送出金额`、`收到金额` 是否满足公式。

---

### 第四步：成本与持仓重新核算 (Cost & Holding Recalculation)

对于给定的证券和特定账户，通过扫描所有相关的交易记录，执行累计计算以确认成本的一致性。计算时必须遵循 **账户隔离原则**，严禁跨券商或跨子账户合并持仓。

1. **净投入法 (Net Investment Method)**：
   - 累计持有量计算：
     $$\text{当前持仓数量} = \sum \text{买入数量} - \sum \text{卖出数量} + \sum \text{拆股数量增加}$$
   - 净投入成本计算：
     $$\text{净投入成本} = \sum \text{买入金额} - \sum \text{卖出金额} + \sum \text{手续费} - \sum \text{股息金额} - \sum \text{分红金额}$$
   - 平均成本：
     $$\text{平均成本} = \frac{\text{净投入成本}}{\text{当前持仓数量}}$$

2. **持仓成本法 / 交易轮次法 (Trade Cycle Method)**：
   - 按 YAML 中的 `交易编号`（如 `T001`）对文件进行分组。
   - 每个交易编号代表一个独立的交易轮次。
   - 针对单个交易编号：
     $$\text{交易编号持仓数量} = \sum_{TradeID} \text{买入数量} - \sum_{TradeID} \text{卖出数量}$$
     $$\text{交易编号净成本} = \sum_{TradeID} \text{买入金额} - \sum_{TradeID} \text{卖出金额} + \sum_{TradeID} \text{手续费}$$
     $$\text{交易编号平均每股成本} = \frac{\text{交易编号净成本}}{\text{交易编号持仓数量}}$$
   - 如果一个交易编号的累计数量变为 0，则该交易轮次标记为“已结清”，该轮次的最终盈亏 = 净流入。

---

## 报告输出格式规范

核查完毕后，必须生成一份格式规范、一目了然的 Markdown 核查报告。报告应分为五个板块：

1. **核查汇总**：显示核查的文件数、合规文件数、存在问题的文件数。
2. **文件名校验报告**：列出不合规的文件名，并给出修改建议。
3. **元数据校验报告**：详细指出哪些文件的 Frontmatter 存在违规（例如使用英文键名、数值为负、证券代码缺失引号、时间非 ISO 8601 格式等）。
4. **数学校验报告**：指出 `成交价 × 数量 ≠ 金额` 且误差 `≥ 0.5` 的记录。
5. **持仓与成本审计 (当指定证券时输出)**：
   - 显示通过“净投入法”和“交易轮次法”计算出的持仓情况。
   - 若本地存在 `Holdings_Snapshots/` 中的最新记录，核对计算出的持仓数与快照持仓数是否吻合。

---

## 附加资源与工具

### 辅助参考文件
- **`references/validation_rules.md`**：详细的键名中英文对照、券商/账户标识清单、允许的动作类型枚举。
- **`references/math_check_guide.md`**：复杂的股息扣税、期权平仓、拆股折算成本等特殊场景的计算边界说明。

### 核查脚本 (Scripts)
- **`scripts/verify_transactions.py`**：可自动执行的 Python 核查工具。传入目录或文件路径，自动扫描并输出 JSON 或 Markdown 格式的校验报告。

### 实战样例 (Examples)
- **`examples/perfect_buy_record.md`**：完全合规的买入股票交易记录示例。
- **`examples/perfect_option_record.md`**：完全合规的期权交易记录示例。
- **`examples/perfect_fx_pair/`**：完全合规的一对双向外汇兑换文件示例。
