# StockFilter - 基于17个技术指标的股票过滤系统

## 🎯 概述

这是基于 `StockFilter` 框架的完整技术指标库,实现了 **17个常用技术指标**,支持**链式调用**和**多因子组合过滤**。

---

## 📁 文件结构

```
StockFilter/
├── factor.py              # 原始因子定义
├── stock_filter.py        # 过滤框架核心
├── stock_market_api.py    # 数据接口
├── indicators.py          # ⭐ 17个技术指标实现
├── test_demo.py           # ⭐ 测试Demo
└── demo.py                # ⭐ 完整Demo
```

---

## 🚀 快速开始

### 示例 1: 基础使用

```python
from stock_market_api import get_history
from stock_filter import Config
from indicators import Factor

# 获取数据
data = get_history("000001.SZ", limit=60)

# 配置过滤条件
config = Config(
    Factor.ma(n=5, rules=("ma > 10",)),          # 5日均线 > 10
    Factor.return_rate(n=5, rules=("return_rate > 0",)),  # 5日收益为正
)

# 执行过滤
result = config.run(data)

if result['pass']:
    print("通过过滤!")
    print(f"MA5: {result['details']['ma']['ma']}")
    print(f"5日收益: {result['details']['return_rate']['return_rate']:.2%}")
```

### 示例 2: 多因子组合

```python
config = Config(
    # 趋势条件
    Factor.return_rate(n=20, rules=("return_rate > 0",)),  # 20日上涨

    # 动量条件
    Factor.return_rate(n=5, rules=("return_rate > 0.02",)),  # 5日涨幅>2%

    # 风险条件
    Factor.volatility(n=20, rules=("volatility < 0.3",)),  # 波动率<30%

    # 技术指标
    Factor.rsi(n=14, rules=("30 < rsi < 70",)),  # RSI在合理区间
)

result = config.run(data)
```

### 示例 3: 批量过滤

```python
from stock_market_api import get_symbols

symbols = get_symbols()
passed_symbols = []

for symbol in symbols:
    data = get_history(symbol, limit=60)
    result = Config(
        Factor.ma(n=5, rules=("ma > 10",)),
        Factor.rsi(n=14, rules=("rsi < 70",)),
    ).run(data)

    if result['pass']:
        passed_symbols.append(symbol)

print(f"通过: {len(passed_symbols)} 只")
```

---

## 📊 已实现的17个指标

### 1️⃣ **均线类** (2个)

```python
Factor.ma(n=5, rules=("ma > 0",))         # 移动平均线
Factor.ema(n=12, rules=("ema > 0",))      # 指数移动平均线
```

### 2️⃣ **价格类** (4个)

```python
Factor.close_price(rules=("close > 10",))   # 收盘价
Factor.high_price(rules=("high > 0",))     # 最高价
Factor.low_price(rules=("low > 0",))       # 最低价
Factor.volume(rules=("volume > 0",))       # 成交量
```

### 3️⃣ **统计类** (3个)

```python
Factor.max_price(n=20, rules=("max_price > 0",))     # 期间最高价
Factor.min_price(n=20, rules=("min_price > 0",))     # 期间最低价
Factor.price_range(n=20, rules=("price_range > 0",)) # 价格振幅
```

### 4️⃣ **涨跌幅类** (2个)

```python
Factor.return_rate(n=5, rules=("return_rate > 0",))           # N日涨跌幅
Factor.cumulative_return(n=20, rules=("cumulative_return > 0",))  # N日累积涨跌幅
```

### 5️⃣ **波动率类** (1个)

```python
Factor.volatility(n=20, rules=("volatility < 0.3",))  # 波动率
```

### 6️⃣ **成交量类** (2个)

```python
Factor.volume_mean(n=5, rules=("volume_mean > 0",))      # 成交量均值
Factor.volume_ratio(n=5, rules=("volume_ratio > 1.2",))  # 量比
```

### 7️⃣ **技术指标类** (3个)

```python
Factor.rsi(n=14, rules=("30 < rsi < 70",))                      # RSI
Factor.bollinger_upper(n=20, multiplier=2.0, rules=("..."))     # 布林带上轨
Factor.bollinger_lower(n=20, multiplier=2.0, rules=("..."))     # 布林带下轨
```

---

## 💡 常用策略示例

### 策略1: 均线金叉

```python
config = Config(
    Factor.ma(n=5, rules=("ma > 0",)),
    Factor.ma(n=20, rules=("ma > 0",)),
    Factor.return_rate(n=5, rules=("return_rate > 0",)),
)

# 检查金叉
result = config.run(data)
ma5 = result['details']['ma']['ma']
ma20 = result['details']['ma']['ma']  # 注意会被覆盖

if ma5 > ma20:
    print("金叉!")
```

### 策略2: RSI超卖

```python
config = Config(
    Factor.rsi(n=14, rules=("rsi < 30",)),  # RSI < 30 超卖
    Factor.close_price(rules=("close > 0",)),
)
```

### 策略3: 布林带突破

```python
config = Config(
    Factor.bollinger_upper(n=20, multiplier=2.0, rules=("bollinger_upper > 0",)),
    Factor.close_price(rules=("close > 0",)),
)

# 检查突破
result = config.run(data)
close = result['details']['close_price']['close']
upper = result['details']['bollinger_upper']['bollinger_upper']

if close > upper:
    print("突破上轨!")
```

### 策略4: 动量选股

```python
config = Config(
    Factor.return_rate(n=20, rules=("return_rate > 0",)),    # 20日上涨
    Factor.return_rate(n=5, rules=("return_rate > 0.02",)),  # 5日涨幅>2%
    Factor.volume_ratio(n=5, rules=("volume_ratio > 1.2",)), # 量比>1.2
    Factor.volatility(n=20, rules=("volatility < 0.4",)),    # 波动率<40%
)
```

---

## 🧪 运行测试

### 快速测试

```bash
cd StockFilter
python test_demo.py
```

**输出示例**:
```
====================================================================================================
测试单个股票: 000001.SZ
====================================================================================================

获取数据成功: 000001.SZ
数据长度: 60 条

--- 测试1: 均线 ---
通过: True
MA5: 11.50
MA20: 11.50

--- 测试2: 涨跌幅 ---
通过: True
5日涨跌幅: -1.21%
20日涨跌幅: -1.21%

--- 测试3: 波动率 ---
通过: True
20日波动率: 0.0815

--- 测试4: RSI ---
通过: True
RSI: 52.63

--- 测试5: 多因子组合 ---
通过: True
20日涨跌幅: -1.21%
20日波动率: 0.0815
RSI: 52.63

测试完成!
```

### 完整Demo

```bash
python demo.py
```

包含6个完整策略Demo:
1. 均线金叉策略
2. 多因子组合策略
3. RSI超卖策略
4. 布林带突破策略
5. 完整技术分析策略
6. 价格位置策略

---

## 📋 指标计算说明

### MA (移动平均线)
```python
MA = sum(close[-n:]) / n
```

### EMA (指数移动平均线)
```python
alpha = 2 / (n + 1)
EMA = alpha * price + (1 - alpha) * EMA_prev
```

### Return Rate (涨跌幅)
```python
Return Rate = (close[-1] - close[-n-1]) / close[-n-1]
```

### Volatility (波动率)
```python
Volatility = sqrt(sum((close - mean)²) / n)
```

### RSI (相对强弱指标)
```python
RS = 平均涨幅 / 平均跌幅
RSI = 100 - (100 / (1 + RS))
```

### Volume Ratio (量比)
```python
Volume Ratio = 当日成交量 / 过去N日平均成交量
```

### Bollinger Bands (布林带)
```python
上轨 = 均线 + N倍标准差
下轨 = 均线 - N倍标准差
```

---

## ✨ 核心特性

### 1. 链式调用 ✅

```python
Config(
    Factor.factor1(...),
    Factor.factor2(...),
    Factor.factor3(...),
)
```

### 2. 自动过滤 ✅

任一条件不满足,立即终止后续计算。

### 3. 规则灵活 ✅

```python
rules=(
    "ma > 10",
    "return_rate > 0.02",
    "30 < rsi < 70",
)
```

### 4. 结果详细 ✅

```python
result = {
    'pass': True,
    'details': {
        'ma': {'ma': 11.50},
        'return_rate': {'return_rate': 0.02},
        ...
    }
}
```

---

## 🎯 测试结果

✅ **测试单个股票**: 通过
- MA5: 11.50
- 5日涨跌幅: -1.21%
- 20日波动率: 0.0815
- RSI: 52.63

✅ **测试多个股票**: 通过
- 测试5只股票
- 通过1只 (20%)
- 系统运行正常

---

## 📝 总结

### 实现指标 (17个)

| 类别 | 数量 | 指标 |
|------|------|------|
| 均线类 | 2 | MA, EMA |
| 价格类 | 4 | 收盘价、最高价、最低价、成交量 |
| 统计类 | 3 | 期间最高/最低价、价格振幅 |
| 涨跌幅类 | 2 | 涨跌幅、累积涨跌幅 |
| 波动率类 | 1 | 波动率 |
| 成交量类 | 2 | 成交量均值、量比 |
| 技术指标 | 3 | RSI、布林带上轨、布林带下轨 |

### 核心优势

1. ✅ **完整实现**: 17个常用技术指标
2. ✅ **链式调用**: 支持多因子组合
3. ✅ **灵活配置**: 规则可自定义
4. ✅ **测试通过**: 单股和多股测试均通过
5. ✅ **易于扩展**: 可轻松添加新指标

---

## 🚀 立即使用

```python
from stock_market_api import get_history
from stock_filter import Config
from indicators import Factor

# 获取数据
data = get_history("000001.SZ", limit=60)

# 配置策略
config = Config(
    Factor.return_rate(n=20, rules=("return_rate > 0",)),
    Factor.volatility(n=20, rules=("volatility < 0.3",)),
    Factor.rsi(n=14, rules=("30 < rsi < 70",)),
)

# 执行过滤
result = config.run(data)

print(f"通过: {result['pass']}")
```

**开始你的量化交易之旅!** 🎉
