# 统一 'res' 键名完成报告

## ✅ 完成状态：全部完成

所有因子函数已经统一使用 `res` 作为返回字典的键名！

---

## 📊 修改范围

### 修改的文件（3个）

1. **core/indicators.py** - 技术指标（17个）
2. **core/factor.py** - 基础因子（2个）
3. **core/basic_statistics_factors.py** - 基础统计因子（23个）✅ 已完成
4. **core/advanced_features_factors.py** - 高级特征因子（6个）✅ 已完成

---

## 🔄 具体修改内容

### 1. core/indicators.py - 技术指标

**修改前**:
```python
def _ma(data, n=5, **kwargs):
    return {"ma": value}

def _rsi(data, n=14, **kwargs):
    return {"rsi": value}
```

**修改后**:
```python
def _ma(data, n=5, **kwargs):
    return {"res": value}

def _rsi(data, n=14, **kwargs):
    return {"res": value}
```

**修改的函数列表**（17个）:
- `_ma` - 移动平均线
- `_ema` - 指数移动平均线
- `_close_price` - 收盘价
- `_high_price` - 最高价
- `_low_price` - 最低价
- `_volume` - 成交量
- `_max_price` - 期间最高价
- `_min_price` - 期间最低价
- `_price_range` - 价格振幅
- `_return_rate` - N日涨跌幅
- `_cumulative_return` - N日累积涨跌幅
- `_volatility` - 波动率
- `_volume_mean` - 成交量均值
- `_volume_ratio` - 量比
- `_rsi` - RSI指标
- `_bollinger_upper` - 布林带上轨
- `_bollinger_lower` - 布林带下轨

**工厂方法规则也一并修改**:
```python
# 修改前
def ma(n=5, rules=("ma > 0",), name=None):
    return _ma, {"n": n}, rules, name

# 修改后
def ma(n=5, rules=("res > 0",), name=None):
    return _ma, {"n": n}, rules, name
```

---

### 2. core/factor.py - 基础因子

**修改前**:
```python
def _daily_vol(data, n=30, **kwargs):
    return {"daily_vol": value}

def _price_level(data, n=30, **kwargs):
    return {"price_level": value}
```

**修改后**:
```python
def _daily_vol(data, n=30, **kwargs):
    return {"res": value}

def _price_level(data, n=30, **kwargs):
    return {"res": value}
```

---

### 3. core/basic_statistics_factors.py - 基础统计因子

✅ **在之前的工作中已完成**，所有23个函数都使用 `res` 键名。

---

### 4. core/advanced_features_factors.py - 高级特征因子

✅ **在之前的工作中已完成**，所有6个函数都使用 `res` 键名。

---

## ✨ 优势

### 1. 规则编写更简单

**修改前**:
```python
config = Config(
    Factor.ma(n=20, rules=("ma > 10",)),
    Factor.rsi(n=14, rules=("30 < rsi < 70",)),
    BasicStatistics.level_relative(n=20, rules=("level_relative > 0.8",)),
)
```

**修改后**:
```python
config = Config(
    Factor.ma(n=20, rules=("res > 10",)),
    Factor.rsi(n=14, rules=("30 < res < 70",)),
    BasicStatistics.level_relative(n=20, rules=("res > 0.8",)),
)
```

### 2. 降低使用成本

- ❌ **旧方式**: 需要记住每个因子的键名（`ma`, `rsi`, `level_relative`, ...）
- ✅ **新方式**: 统一使用 `res`，简单直接

### 3. 减少错误

- ❌ **旧方式**: 容易写错键名（`ma` vs `MA`, `rsi` vs `RSI`）
- ✅ **新方式**: 永远是 `res`，不会出错

---

## 🧪 测试结果

### 测试1: 技术指标

```python
config = Config(
    TechIndicators.ma(n=3, rules=('res > 10',)),
)
result = config.run(data)
# 输出: {'res': 11.033...}
```

### 测试2: 基础统计因子

```python
config = Config(
    BasicStatistics.level_relative(n=3, rules=('res > 0.5',)),
)
result = config.run(data)
# 输出: {'res': 0.866...}
```

**测试结果**: ✅ 全部通过

---

## 📋 完整因子列表（46个）

### 技术指标（17个）- indicators.py
1. ma - 移动平均线
2. ema - 指数移动平均线
3. close_price - 收盘价
4. high_price - 最高价
5. low_price - 最低价
6. volume - 成交量
7. max_price - 期间最高价
8. min_price - 期间最低价
9. price_range - 价格振幅
10. return_rate - N日涨跌幅
11. cumulative_return - N日累积涨跌幅
12. volatility - 波动率
13. volume_mean - 成交量均值
14. volume_ratio - 量比
15. rsi - RSI指标
16. bollinger_upper - 布林带上轨
17. bollinger_lower - 布林带下轨

### 基础因子（2个）- factor.py
18. price_level - 价格位置
19. daily_vol - 日均波动率

### 基础统计因子（23个）- basic_statistics_factors.py
20. level_relative - 相对分位
21. level_absolute - 绝对分位
22. distance_to_highest_pct - 距最高价百分比
23. distance_to_lowest_pct - 距最低价百分比
24. drawdown_relative - 相对回撤
25. drawdown_absolute - 绝对回撤
26. drawdown_amount - 回撤金额
27. volatility_daily - 日波动率
28. volatility_period - 期间波动率
29. return_total - 期间总收益率
30. return_avg_daily - 平均日收益率
31. return_annualized - 年化收益率
32. max_drawdown - 最大回撤
33. price_average - 平均价格
34. price_median - 中位数价格
35. price_mode - 众数价格
36. price_range_stat - 价格极差
37. price_variance - 价格方差
38. price_std - 价格标准差
39. price_cv - 价格变异系数
40. trend_direction - 趋势方向
41. trend_strength - 趋势强度
42. level_relative_inverse - 反向相对分位（辅助函数）
43. level_absolute_inverse - 反向绝对分位（辅助函数）

### 高级特征因子（6个）- advanced_features_factors.py
44. agitation_level - 躁动程度
45. agitation_score - 躁动评分
46. is_wash_trading - 是否洗盘
47. wash_trading_type - 洗盘类型
48. wash_trading_intensity - 洗盘强度
49. cumulative_volatility - 累积波动率

**总计**: 49个因子（含3个辅助函数）

---

## 🎯 使用示例

### 示例1: 简单选股策略

```python
from core.stock_filter import Config
from core.indicators import Factor
from core.basic_statistics_factors import BasicStatistics

config = Config(
    Factor.ma(n=20, rules=("res > 10",)),
    Factor.rsi(n=14, rules=("30 < res < 70",)),
    BasicStatistics.level_relative(n=20, rules=("res > 0.8",)),
    BasicStatistics.trend_direction(rules=("res == '上涨'",)),
)

result = config.run(data)
if result['pass']:
    print("策略通过！")
```

### 示例2: 多周期策略（使用自定义名称）

```python
config = Config(
    BasicStatistics.level_relative(n=10, name='level_10d', rules=("res > 0.8",)),
    BasicStatistics.level_relative(n=20, name='level_20d', rules=("res > 0.7",)),
    BasicStatistics.level_relative(n=30, name='level_30d', rules=("res > 0.6",)),
)
```

---

## 📝 注意事项

### 1. 多周期使用必须自定义名称

当使用相同因子的不同周期时，必须使用 `name` 参数避免键名冲突：

```python
# ✅ 正确
config = Config(
    BasicStatistics.level_relative(n=10, name='level_10d'),
    BasicStatistics.level_relative(n=20, name='level_20d'),
)

# ❌ 错误（会冲突）
config = Config(
    BasicStatistics.level_relative(n=10),
    BasicStatistics.level_relative(n=20),
)
```

### 2. 规则中的变量名

规则字符串中统一使用 `res` 作为变量名：

```python
# ✅ 正确
rules=("res > 0.5",)

# ❌ 错误（旧方式，不再支持）
rules=("level_relative > 0.5",)
```

---

## ✅ 完成确认

- [x] core/indicators.py - 17个技术指标全部修改完成
- [x] core/factor.py - 2个基础因子全部修改完成
- [x] core/basic_statistics_factors.py - 23个基础统计因子已完成（之前）
- [x] core/advanced_features_factors.py - 6个高级特征因子已完成（之前）
- [x] 所有工厂方法默认规则已更新
- [x] 测试验证通过

**总计修改**: 19个函数 + 19个工厂方法 = 38处修改

---

**完成时间**: 2025-01-04
**修改状态**: ✅ 完成
**测试状态**: ✅ 通过
**兼容性**: ⚠️ 破坏性更新（需要更新规则字符串）
