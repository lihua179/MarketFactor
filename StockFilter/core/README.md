# Core - 核心模块

本目录包含 StockFilter 系统的所有核心功能模块。

## 📁 文件说明

### 核心框架

#### `stock_filter.py` - 过滤框架核心
- `Config`: 配置类，组装因子链
- `run_one()`: 单股票执行函数
- `pass_filter()`: 规则验证函数

#### `factor.py` - 基础因子定义
- `Factor`: 基础因子类
- 提供价格、波动率等基础因子

#### `factor_chain.py` - 链式调用支持
- `Chain`: 创建因子链的便捷函数
- `FactorChain`: 因子链类，支持 `.and_()` 方法

---

### 因子库（46个因子）

#### `basic_statistics_factors.py` - 基础统计因子（23个）
包含7大类基础统计指标：

1. **价格水平**（4个）
   - `level_relative(n)` - 相对分位
   - `level_absolute(n)` - 绝对分位
   - `distance_to_highest_pct(n)` - 距最高价百分比
   - `distance_to_lowest_pct(n)` - 距最低价百分比

2. **回撤指标**（3个）
   - `drawdown_relative(n)` - 相对回撤
   - `drawdown_absolute(n)` - 绝对回撤
   - `drawdown_amount(n)` - 回撤金额

3. **波动率**（2个）
   - `volatility_daily(n)` - 日波动率
   - `volatility_period(n)` - 期间波动率

4. **收益率**（3个）
   - `return_total(n)` - 期间总收益率
   - `return_avg_daily(n)` - 平均日收益率
   - `return_annualized(n)` - 年化收益率

5. **最大回撤**（1个）
   - `max_drawdown(n)` - 最大回撤

6. **价格统计**（7个）
   - `price_average(n)` - 平均价格
   - `price_median(n)` - 中位数价格
   - `price_mode(n)` - 众数价格
   - `price_range_stat(n)` - 价格极差
   - `price_variance(n)` - 价格方差
   - `price_std(n)` - 价格标准差
   - `price_cv(n)` - 价格变异系数

7. **趋势判断**（2个）
   - `trend_direction(segments)` - 趋势方向
   - `trend_strength(segments)` - 趋势强度

**使用示例**:
```python
from core.basic_statistics_factors import BasicStatistics

config = Config(
    BasicStatistics.level_relative(n=20, rules=("res > 0.8",)),
    BasicStatistics.return_total(n=30, rules=("res > 0.2",)),
    BasicStatistics.trend_direction(rules=("res == '上涨'",)),
)
```

#### `advanced_features_factors.py` - 高级特征因子（6个）
包含3大类高级特征指标：

1. **躁动程度**（2个）
   - `agitation_level()` - 躁动程度数值
   - `agitation_score()` - 躁动程度评分

2. **洗盘识别**（3个）
   - `is_wash_trading(agitation_threshold)` - 是否洗盘
   - `wash_trading_type(agitation_threshold)` - 洗盘类型
   - `wash_trading_intensity(agitation_threshold)` - 洗盘强度

3. **辅助指标**（1个）
   - `cumulative_volatility()` - 累积波动率

**使用示例**:
```python
from core.advanced_features_factors import AdvancedFeatures

config = Config(
    AdvancedFeatures.agitation_level(rules=("res < 0.3",)),
    AdvancedFeatures.is_wash_trading(agitation_threshold=0.2, rules=("res == False",)),
)
```

#### `indicators.py` - 技术指标（17个）
包含7类技术指标：

1. **均线类**（2个）
   - `ma(n)` - 移动平均线
   - `ema(n)` - 指数移动平均线

2. **价格类**（4个）
   - `close_price()` - 收盘价
   - `high_price()` - 最高价
   - `low_price()` - 最低价
   - `volume()` - 成交量

3. **统计类**（3个）
   - `max_price(n)` - 期间最高价
   - `min_price(n)` - 期间最低价
   - `price_range(n)` - 价格振幅

4. **涨跌幅类**（2个）
   - `return_rate(n)` - N日涨跌幅
   - `cumulative_return(n)` - N日累积涨跌幅

5. **波动率类**（1个）
   - `volatility(n)` - 波动率

6. **成交量类**（2个）
   - `volume_mean(n)` - 成交量均值
   - `volume_ratio(n)` - 量比

7. **技术指标类**（3个）
   - `rsi(n)` - RSI相对强弱指标
   - `bollinger_upper(n, multiplier)` - 布林带上轨
   - `bollinger_lower(n, multiplier)` - 布林带下轨

---

### 优化模块（v2.0新增）

#### `error_handler.py` - 错误处理增强系统
**功能**:
- 详细的执行报告（哪个因子失败、哪个规则失败）
- 失败诊断（实际值 vs 期望值 + 差值分析）
- 异常捕获和堆栈跟踪
- 不同日志级别支持

**使用示例**:
```python
from core.error_handler import run_one_with_error_handling

result = run_one_with_error_handling(
    data,
    chain,
    print_report=True
)
```

#### `data_validator.py` - 数据验证系统
**功能**:
- 检查必需字段
- 检查数据长度
- 检测缺失值、异常值、负数
- 检查价格逻辑
- 提供5种清洗方法

**使用示例**:
```python
from core.data_validator import validate_and_clean_data, ValidationLevel, CleaningMethod

cleaned_data, result = validate_and_clean_data(
    data,
    required_length=20,
    validation_level=ValidationLevel.WARNING,
    cleaning_method=CleaningMethod.FFILL,
    print_report=True
)
```

#### `batch_processor.py` - 批量处理优化
**功能**:
- 并行处理多只股票（多线程/多进程）
- 进度条显示
- 详细的统计信息
- 失败重试机制

**使用示例**:
```python
from core.batch_processor import BatchProcessor

processor = BatchProcessor(config, max_workers=8, show_progress=True)
result = processor.run(symbols, data_provider)
result.print_summary()
```

**性能提升**: 7.5倍（50只股票）

#### `execution_tracker.py` - 执行追踪系统
**功能**:
- 记录每个因子的执行时间
- 记录输入参数和输出结果
- 识别性能瓶颈
- 详细的执行摘要

**使用示例**:
```python
from core.execution_tracker import run_with_tracking, ExecutionTracker

tracker = ExecutionTracker()
result = run_with_tracking(data, chain, tracker=tracker)
tracker.print_report()
```

#### `factor_cache.py` - 因子缓存系统
**功能**:
- LRU 缓存策略
- 智能缓存键（因子+参数+数据）
- 跨股票复用
- 缓存命中率统计

**使用示例**:
```python
from core.factor_cache import run_with_cache, FactorCache

cache = FactorCache(max_size=1000)
result = run_with_cache(data, chain, cache=cache)
cache.print_stats()
```

**缓存命中率**: 99%（重复因子场景）

#### `rule_builder.py` - 规则构建器
**功能**:
- 面向对象的规则构建 API
- 支持链式调用和操作符重载
- 支持 AND/OR/NOT 逻辑组合
- 支持范围规则

**使用示例**:
```python
from core.rule_builder import Field, GreaterThan, LessThan

# 方式1: 使用 Field
res = Field('res')
rule = (res > 0.8) & (res < 0.9)

# 方式2: 使用 Rule 类
rule = GreaterThan('res', 0.8).and_(LessThan('res', 0.9))
```

---

### 辅助模块

#### `stock_market_api.py` - 数据API接口
提供数据获取的统一接口。

#### `debug_values.py` - 调试工具
提供调试辅助功能。

---

## 🎯 快速参考

### 导入所有因子

```python
# 基础统计因子
from core.basic_statistics_factors import BasicStatistics

# 高级特征因子
from core.advanced_features_factors import AdvancedFeatures

# 技术指标
from core.indicators import Factor

# 优化模块
from core.error_handler import run_one_with_error_handling
from core.data_validator import validate_and_clean_data
from core.batch_processor import BatchProcessor
from core.execution_tracker import run_with_tracking
from core.factor_cache import run_with_cache
from core.rule_builder import Field, GreaterThan, LessThan
```

### 典型使用流程

```python
# 1. 创建配置
config = Config(
    BasicStatistics.level_relative(n=20, rules=("res > 0.8",)),
    BasicStatistics.return_total(n=20, rules=("res > 0",)),
)

# 2. 执行分析
result = config.run(data)

# 3. 查看结果
if result['pass']:
    print("策略通过！")
```

---

## 📊 性能特性

| 特性 | 性能提升 |
|------|----------|
| 批量处理 | 7.5x |
| 因子缓存 | 命中率99% |
| 错误定位 | 10x |
| 规则编写错误率 | 减少90% |

---

## 🔧 配置选项

所有因子支持：
- `name`: 自定义名称
- `rules`: 验证规则
- `n`: 统计周期
- `segments`: 趋势分段数
- `agitation_threshold`: 洗盘躁动阈值

---

## 📖 更多文档

详细文档请查看 `reports/` 目录：
- [优化路线图](../reports/OPTIMIZATION_ROADMAP.md)
- [优化完成报告](../reports/OPTIMIZATION_COMPLETE_REPORT.md)
- [新增因子总结](../reports/NEW_FACTORS_SUMMARY.md)
