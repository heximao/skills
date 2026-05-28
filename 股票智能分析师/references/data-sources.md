# 数据源URL格式

## A股数据源

### 1. 东方财富（推荐）
```
行情页：https://quote.eastmoney.com/SH600519.html
K线API：https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=1.600519&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58&klt=101&fqt=1&beg=0&end=20500101&lmt=120
```
- 代码格式：将 SH/SZ 前缀转为全小写拼接
- secid格式：沪市前缀 1.，深市前缀 0.
- 例：1.600519 或 0.000001

### 2. 雪球
```
https://xueqiu.com/S/SH600519
```
注意：雪球可能需要登录，如被拦截则换其他源

### 3. 新浪财经
```
https://finance.sina.com.cn/realstock/company/sh600519/nc.shtml
```
代码格式：小写 sh/sz + 6位代码

### 4. 腾讯财经
```
https://gu.qq.com/sh600519
```
代码格式：小写 sh/sz + 6位代码

## 美股数据源

### 1. Yahoo Finance API（JSON格式，推荐）
```
https://query1.finance.yahoo.com/v8/finance/chart/AAPL?interval=1d&range=3mo
```
参数说明：
- `interval`: 时间间隔（1d=日线, 1h=小时线）
- `range`: 时间范围（1d, 5d, 1mo, 3mo, 6mo, 1y, 5y）

### 2. Yahoo Finance 行情页
```
https://finance.yahoo.com/quote/AAPL
```
包含完整的基本面数据（PE、市值、财务报表等）

### 3. 雪球（美股）
```
https://xueqiu.com/S/AAPL
```

## 港股数据源

### 1. 雪球（港股，前加$）
```
https://xueqiu.com/S/$00700
```
代码格式：$ + 5位数字

### 2. 东方财富港股
```
https://quote.eastmoney.com/hk/00700.html
```

## 数据提取要点

### 从行情页提取
- 当前价格、涨跌额、涨跌幅
- 开盘价、昨收、最高价、最低价
- 成交量、成交额、换手率
- 市值、PE（TTM）、PB、股息率

### 从K线数据提取
- 开盘价、收盘价、最高价、最低价
- 成交量
- 用于计算技术指标（MACD、RSI、KDJ等）

## 访问失败处理

如果某个数据源访问失败：
1. 尝试下一个优先级的数据源
2. 如果所有数据源都失败，告知用户当前数据不可用
3. 基于可用数据进行定性分析，明确标注数据缺失部分
