#!/usr/bin/env python3
import os
import sys
import re
import yaml
from datetime import datetime

# Common Constants and Schema Rules
ALLOWED_BROKERS = {"LB", "IB", "VB", "DFCF", "HB", "CS", "XY", "ICBC"}

CHINESE_TO_ENGLISH_KEYS = {
    "时间": "date",
    "挂单时间": "limit_date",
    "成交时间": "filled_date",
    "撤单时间": "cancelled_date",
    "市场": "market",
    "交易所": "exchange",
    "券商": "broker",
    "机构": "institution",
    "账户": "account",
    "证券名称": "symbol_name",
    "证券代码": "symbol_code",
    "动作": "side",
    "数量": "qty",
    "货币": "currency",
    "挂单价": "limit_price",
    "成交价": "filled_price",
    "金额": "amount",
    "实际汇率": "actual_rate",
    "手续费": "fee",
    "策略": "strategy",
    "状态": "status",
    "止盈": "tp",
    "止盈价": "tp",
    "止损": "sl",
    "止损价": "sl",
    "交易编号": "trade_id"
}

ALLOWED_MARKETS = {"us-stocks", "hk-stocks", "a-shares", "crypto"}
ALLOWED_STOCK_ACTIONS = {"买入", "卖出", "股息", "分红", "拆股"}
ALLOWED_OPTION_ACTIONS = {"买入开仓", "卖出开仓", "买入平仓", "卖出平仓"}
ALLOWED_TRANSFER_ACTIONS = {"入金", "出金"}
ALLOWED_FX_ACTIONS = {"出账", "入账"}

def parse_md_frontmatter(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract YAML frontmatter
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return None, "Missing or malformed YAML frontmatter"

    yaml_text = match.group(1)
    try:
        data = yaml.safe_load(yaml_text)
        return data, None
    except Exception as e:
        return None, f"YAML parse error: {str(e)}"

def verify_file(file_path):
    base_name = os.path.basename(file_path)
    errors = []
    warnings = []

    # 1. Filename validation
    name_without_ext, ext = os.path.splitext(base_name)
    if ext.lower() != ".md":
        return None, ["File must have .md extension"], []

    # Ignore hidden files, templates or READMEs
    if name_without_ext.startswith(".") or name_without_ext.lower() in ("readme", "skill"):
        return None, [], []

    # Check if planned/placed order
    is_planned = False
    clean_name = name_without_ext
    if clean_name.startswith("计划_"):
        is_planned = True
        clean_name = clean_name[3:]

    parts = clean_name.split("_")

    # 2. Check general filename pattern length
    # YYYY-MM-DD_Broker_...
    if len(parts) < 3:
        errors.append(f"Filename does not match standard pattern: {base_name}")
        return None, errors, warnings

    date_str, broker_code = parts[0], parts[1]

    # Validate date in filename
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        errors.append(f"Filename date prefix '{date_str}' is not in YYYY-MM-DD format")

    # Validate broker in filename
    if broker_code not in ALLOWED_BROKERS:
        errors.append(f"Broker code '{broker_code}' in filename is not in allowed list: {ALLOWED_BROKERS}")

    # Parse YAML frontmatter
    data, err = parse_md_frontmatter(file_path)
    if err:
        errors.append(err)
        return None, errors, warnings

    if not isinstance(data, dict):
        errors.append("Frontmatter is not a dictionary/YAML object")
        return None, errors, warnings

    # 3. YAML Key verification - Check English keys (forbidden)
    for key in data.keys():
        if key in CHINESE_TO_ENGLISH_KEYS.values() and key not in ("status", "strategy", "market"):
            # some standard configurations can be exempted but raw trade logs shouldn't have english keys
            errors.append(f"Forbidden English key '{key}' found in YAML frontmatter. Must use Chinese.")

    # Check required general fields
    # Every file must have Time, Action, Currency, Amount/Fee at least
    required_keys = {"时间", "动作", "货币", "金额"}
    for r_key in required_keys:
        if r_key not in data:
            errors.append(f"Missing required field '{r_key}' in YAML")

    # Check values
    if "时间" in data:
        time_val = str(data["时间"])
        # Validate ISO 8601
        if not re.match(r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2})?", time_val):
            errors.append(f"Date/Time '{time_val}' is not in valid ISO 8601 format (YYYY-MM-DDThh:mm:ss)")
        elif not time_val.startswith(date_str):
            errors.append(f"Filename date '{date_str}' does not match YAML date/time '{time_val}'")

    # Check for negative values
    for numeric_field in ("数量", "成交价", "金额", "手续费", "实际汇率"):
        if numeric_field in data:
            val = data[numeric_field]
            if val is not None:
                try:
                    num_val = float(val)
                    if num_val < 0:
                        errors.append(f"Numeric field '{numeric_field}' cannot be negative: {num_val}")
                except ValueError:
                    errors.append(f"Field '{numeric_field}' is not a valid number: {val}")

    # Check stock codes quoted rule
    if "证券代码" in data:
        code_val = data["证券代码"]
        # If it's loaded as integer, and it has digits like hk-stocks/a-shares, it's missing quotes
        if isinstance(code_val, int):
            errors.append(f"证券代码: {code_val} is treated as number in YAML. It MUST be wrapped in quotes (e.g. '{code_val}') to preserve leading zeros.")

    # Action-specific validation
    action = data.get("动作")
    if action:
        # Determine asset type from file naming structure or contents
        is_option = False
        is_fx = False
        is_transfer = False

        # Check if option by name length or keys
        if len(parts) >= 5 and any(term in parts[2] for term in ("Call", "Put", "2025", "2026", "2027")):
            is_option = True
        elif action in ALLOWED_OPTION_ACTIONS:
            is_option = True

        if "FX" in parts or action in ALLOWED_FX_ACTIONS:
            is_fx = True

        if "Deposits" in parts or "Withdrawals" in parts or action in ALLOWED_TRANSFER_ACTIONS:
            is_transfer = True

        # Action validations
        if is_option:
            if action not in ALLOWED_OPTION_ACTIONS:
                errors.append(f"Action '{action}' is invalid for an option file. Must be in {ALLOWED_OPTION_ACTIONS}")
        elif is_fx:
            if action not in ALLOWED_FX_ACTIONS:
                errors.append(f"Action '{action}' is invalid for FX transaction. Must be in {ALLOWED_FX_ACTIONS}")
        elif is_transfer:
            if action not in ALLOWED_TRANSFER_ACTIONS:
                errors.append(f"Action '{action}' is invalid for deposits/withdrawals. Must be in {ALLOWED_TRANSFER_ACTIONS}")
        else:
            if action not in ALLOWED_STOCK_ACTIONS:
                errors.append(f"Action '{action}' is invalid for stock/ETF file. Must be in {ALLOWED_STOCK_ACTIONS}")

    # Math consistency checks
    qty = data.get("数量")
    price = data.get("成交价")
    amount = data.get("金额")

    if qty is not None and price is not None and amount is not None and action not in ("拆股", "股息", "分红"):
        try:
            q = float(qty)
            p = float(price)
            a = float(amount)

            # If it's an option, multiply by 100
            multiplier = 100 if is_option else 1

            expected_amount = q * p * multiplier
            diff = abs(a - expected_amount)
            if diff >= 0.5:
                warnings.append(f"Mathematical inconsistency: '成交价'({p}) * '数量'({q}){ ' * 100' if is_option else '' } = {expected_amount}, but '金额' is declared as {a}. Diff is {diff:.2f}")
        except ValueError:
            pass # already handled in numeric check

    # Filename amount check for cash transfers
    if is_transfer and len(parts) >= 4:
        try:
            # File name amount segment (parts[3] usually)
            fn_amt_str = parts[3]
            if fn_amt_str.isdigit() and amount is not None:
                fn_amt = int(fn_amt_str)
                yaml_amt = int(float(amount)) # floor
                if fn_amt != yaml_amt:
                    warnings.append(f"Filename amount '{fn_amt}' does not match floor of YAML amount '{yaml_amt}'")
        except Exception:
            pass

    return data, errors, warnings

def run_verification(paths):
    total_scanned = 0
    total_valid = 0
    total_invalid = 0

    files_to_check = []
    for path in paths:
        if os.path.isdir(path):
            for root, _, files in os.walk(path):
                # Skip .git or .claude
                if any(x in root for x in (".git", ".claude", "node_modules", "Holdings_Snapshots")):
                    continue
                for f in files:
                    if f.endswith(".md") and not f.lower().startswith("readme") and not f.lower().startswith("skill"):
                        files_to_check.append(os.path.join(root, f))
        elif os.path.isfile(path) and path.endswith(".md"):
            files_to_check.append(path)

    print(f"### 交易文件校验报告")
    print(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"扫描目录/文件: {paths}\n")

    all_errors = {}
    all_warnings = {}

    for f in sorted(files_to_check):
        total_scanned += 1
        data, errs, warns = verify_file(f)
        if errs:
            total_invalid += 1
            all_errors[f] = errs
        else:
            total_valid += 1

        if warns:
            all_warnings[f] = warns

    print(f"#### 1. 核查汇总")
    print(f"- 已扫描交易文件: **{total_scanned}**")
    print(f"- 合规文件: **{total_valid}**")
    print(f"- 违规文件: **{total_invalid}**\n")

    if all_errors:
        print(f"#### 2. 文件违规详情 (Errors)")
        for f, errs in all_errors.items():
            rel_path = os.path.relpath(f)
            print(f"- **{rel_path}**")
            for e in errs:
                print(f"  - 🔴 {e}")
        print()

    if all_warnings:
        print(f"#### 3. 潜在警报/数学校核警告 (Warnings)")
        for f, warns in all_warnings.items():
            rel_path = os.path.relpath(f)
            print(f"- **{rel_path}**")
            for w in warns:
                print(f"  - ⚠️ {w}")
        print()

    if total_invalid == 0:
        print("🎉 **所有扫描的文件全部符合校验标准，未发现格式及硬约束违规！**")
        return True
    else:
        print("❌ **发现格式违规，请根据上述提示修正。**")
        return False

if __name__ == "__main__":
    scan_paths = sys.argv[1:] if len(sys.argv) > 1 else ["."]
    success = run_verification(scan_paths)
    sys.exit(0 if success else 1)
