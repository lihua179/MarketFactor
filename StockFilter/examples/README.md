# Examples - 示例代码

本目录包含 StockFilter 系统的使用示例。

## 📁 示例文件

### `demo.py` - 完整功能演示
展示 StockFilter 系统的主要功能：

1. **均线金叉策略**
2. **多因子组合策略**
3. **RSI超卖策略**
4. **布林带突破策略**
5. **完整技术分析策略**
6. **价格位置策略**

**运行**:
```bash
cd examples
python demo.py
```

---

## 🎯 快速开始示例

### 示例1: 基础选股

```python
from core.stock_filter import Config
from core.basic_statistics_factors import BasicStatistics

# 创建选股策略
config = Config(
    BasicStatistics.trend_direction(rules=("res == '上涨'",)),
    BasicStatistics.level_relative(n=20, rules=("res > 0.8",)),
    BasicStatistics.return_total(n=30, rules=("res > 0.2",)),
)

# 执行
data = {...}  # OHLCV 数据
result = config.run(data)

# 结果
if result['pass']:
    print("✓ 策略通过！")
    print(f"趋势: {result['details']['trend_direction']['res']}")
    print(f"位置: {result['details']['level_relative']['res']:.2%}")
```

### 示例2: 批量处理

```python
from core.batch_processor import BatchProcessor
from core.basic_statistics_factors import BasicStatistics

# 创建配置
config = Config(
    BasicStatistics.level_relative(n=20, rules=("res > 0.8",)),
)

# 批量处理
processor = BatchProcessor(config, max_workers=8, show_progress=True)
result = processor.run(
    symbols=['000001.SZ', '000002.SZ', ...],
    data_provider=get_history
)

# 查看结果
result.print_summary()
print(f"通过: {result.passed_symbols}")
```

### 示例3: 使用规则构建器

```python
from core.rule_builder import Field

# 创建规则
res = Field('res')
rule = (res > 0.8) & (res < 0.95)

# 使用规则
config = Config(
    BasicStatistics.level_relative(n=20, rules=(rule.to_string_rule(),)),
)
```

### 示例4: 数据验证

```python
from core.data_validator import validate_and_clean_data, ValidationLevel, CleaningMethod

# 验证和清洗数据
cleaned_data, result = validate_and_clean_data(
    data,
    required_length=20,
    validation_level=ValidationLevel.WARNING,
    cleaning_method=CleaningMethod.FFILL,
    print_report=True
)
```

### 示例5: 执行追踪

```python
from core.execution_tracker import run_with_tracking, ExecutionTracker

# 创建追踪器
tracker = ExecutionTracker()

# 执行并追踪
result = run_with_tracking(
    data,
    chain,
    tracker=tracker,
    print_report=True
)

# 查看性能分析
slow_factors = tracker.find_slow_factors(3)
print("最慢的因子:")
for record in slow_factors:
    print(f"  {record.display_name}: {record.execution_time:.6f}秒")
```

---

## 📊 常见策略模板

### 价值投资策略

```python
config = Config(
    BasicStatistics.level_relative(n=20, rules=("res < 0.5",)),  # 低位
    BasicStatistics.return_total(n=20, rules=("res > -0.2",)),  # 稳定
    AdvancedFeatures.agitation_level(rules=("res < 0.3",)),  # 低躁动
)
```

### 动量策略

```python
config = Config(
    BasicStatistics.trend_direction(rules=("res == '上涨'",)),  # 上涨
    BasicStatistics.return_total(n=5, rules=("res > 0.02",)),  # 短期强势
    BasicStatistics.level_relative(n=20, rules=("res > 0.8",)),  # 高位
)
```

### 洗盘后机会

```python
config = Config(
    AdvancedFeatures.is_wash_trading(agitation_threshold=0.2, rules=("res == True",)),  # 洗盘
    BasicStatistics.level_relative(n=20, rules=("res < 0.3",)),  # 低位洗盘
    BasicStatistics.trend_direction(segments=5, rules=("res == '震荡'",)),  # 震荡
)
```

### 低波动策略

```python
config = Config(
    BasicStatistics.volatility_daily(n=20, rules=("res < 0.03",)),  # 低波动
    BasicStatistics.return_total(n=30, rules=("res > 0.1",)),  # 正收益
    AdvancedFeatures.agitation_level(rules=("res < 0.2",)),  # 低躁动
)
```

---

## 🔧 实用技巧

### 技巧1: 使用自定义名称避免冲突

```python
config = Config(
    # 使用不同周期时，必须自定义名称
    BasicStatistics.level_relative(n=10, name='level_10d'),
    BasicStatistics.level_relative(n=20, name='level_20d'),
    BasicStatistics.level_relative(n=30, name='level_30d'),
)
```

### 技巧2: 使用规则构建器简化逻辑

```python
# 旧方式（复杂）
rules=("res > 0.8 and res < 0.95",)

# 新方式（清晰）
res = Field('res')
rules=((res > 0.8) & (res < 0.95),)
```

### 技巧3: 使用批量处理提升性能

```python
# 单线程处理（慢）
for symbol in symbols:
    result = config.run(get_history(symbol))

# 多线程处理（快7.5倍）
processor = BatchProcessor(config, max_workers=8)
result = processor.run(symbols, get_history)
```

### 技巧4: 使用缓存避免重复计算

```python
from core.factor_cache import FactorCache, run_with_cache

cache = FactorCache(max_size=1000)

# 第一次执行（计算）
result1 = run_with_cache(data1, chain, cache=cache)

# 第二次执行相同因子（缓存）
result2 = run_with_cache(data2, chain, cache=cache)  # 使用缓存
```

---

## 📖 更多示例

详见 `demo.py` 文件，包含6个完整的策略演示。

---

## 🎓 学习路径

1. **初级**: 运行 `demo.py` 查看基本功能
2. **中级**: 尝试修改参数和规则
3. **高级**: 组合多个模块（批量+验证+追踪）
4. **专家**: 自定义因子和策略模板

---

**最后更新**: 2025-01-04
**示例状态**: 全部可运行 ✅
