# StockFilter 新增因子总结

## 概述

基于 `demo_indicators` 文件夹中的 `stock_statistics.py` 和 `stock_advanced_features.py`，为 StockFilter 系统一一补充了**29个新因子**，包括基础统计指标和高级特征指标。

## 新增文件

### 1. `basic_statistics_factors.py` - 基础统计指标因子

**包含23个因子**，分为7大类：

#### 价格水平指标（4个）
1. **level_relative** - 相对分位
   - 计算：(当前-最低)/(最高-最低)
   - 范围：[0, 1]，0表示在最低位，1表示在最高位

2. **level_absolute** - 绝对分位
   - 计算：当前/最高
   - 范围：(0, 1]，接近1表示越接近历史最高

3. **distance_to_highest_pct** - 距离最高价百分比
   - 计算：(最高-当前)/最高 * 100%

4. **distance_to_lowest_pct** - 距离最低价百分比
   - 计算：(当前-最低)/最低 * 100%

#### 回撤指标（3个）
5. **drawdown_relative** - 相对回撤
   - 计算：1 - 相对分位
   - 范围：[0, 1]，0表示无回撤，1表示最大回撤

6. **drawdown_absolute** - 绝对回撤
   - 计算：1 - 绝对分位
   - 范围：[0, 1)，0表示无回撤

7. **drawdown_amount** - 回撤金额
   - 计算：最高价 - 当前价

#### 波动率指标（2个）
8. **volatility_daily** - 日波动率
   - 计算：每天[(最高价 - 最低价) / 昨收价] 的平均值

9. **volatility_period** - 期间波动率
   - 计算：(期间最高价 - 期间最低价) / 期间开盘价

#### 收益率指标（3个）
10. **return_total** - 期间总收益率
    - 计算：(期末价 - 期初价) / 期初价

11. **return_avg_daily** - 平均日收益率
    - 计算：每天[(收盘价 - 昨收价) / 昨收价] 的平均值

12. **return_annualized** - 年化收益率
    - 计算：(1 + 总收益率)^(252/交易日数) - 1

#### 最大回撤（1个）
13. **max_drawdown** - 最大回撤
    - 从价格序列中计算期间内最大回撤

#### 价格统计指标（7个）
14. **price_average** - 平均价格（算术平均）
15. **price_median** - 中位数价格
16. **price_mode** - 众数价格（出现最频繁的价格）
17. **price_range_stat** - 价格极差
    - 计算：最高价 - 最低价
18. **price_variance** - 价格方差
19. **price_std** - 价格标准差
20. **price_cv** - 价格变异系数
    - 计算：标准差 / 平均值

#### 趋势指标（2个）
21. **trend_direction** - 趋势方向
    - 判断：上涨/下跌/震荡
    - 方法：将数据分为三段，判断每段平均价格的变化

22. **trend_strength** - 趋势强度
    - 计算：第一段到第三段的价格变化幅度
    - 正值表示上涨强度，负值表示下跌强度

### 2. `advanced_features_factors.py` - 高级特征指标因子

**包含6个因子**，分为3大类：

#### 躁动程度指标（2个）
1. **agitation_level** - 躁动程度（数值）
   - 计算：|期间累计收益率| / 每日波动率累积之和
   - 含义：价格频繁波动但累积实际收益变化小
   - 值越接近1，躁动越高；值越接近0，躁动越低

2. **agitation_score** - 躁动程度评分（分级）
   - 评分标准：
     - 极高躁动: > 0.8
     - 高躁动: 0.6 - 0.8
     - 中高躁动: 0.4 - 0.6
     - 中等躁动: 0.2 - 0.4
     - 低躁动: 0.1 - 0.2
     - 极低躁动: ≤ 0.1

#### 洗盘识别指标（3个）
3. **is_wash_trading** - 是否洗盘
   - 定义：洗盘 = 震荡趋势下的躁动
   - 判断条件：
     1. 趋势为震荡
     2. 躁动程度 > 阈值（默认0.2）

4. **wash_trading_type** - 洗盘类型
   - 返回："震荡洗盘" 或 "无洗盘"

5. **wash_trading_intensity** - 洗盘强度
   - 计算：躁动程度值
   - 值越大，洗盘越剧烈

#### 辅助指标（1个）
6. **cumulative_volatility** - 累积波动率
   - 计算：每日波动率累积之和

## 使用示例

### 基础统计指标示例

```python
from stock_filter import Config
from basic_statistics_factors import BasicStatistics

# 价格水平分析
report = Config(
    BasicStatistics.level_relative(name='price_level'),
    BasicStatistics.distance_to_highest_pct(name='dist_high')
).run(data)

# 查看结果
print(f"相对分位: {report['details']['price_level']['level_relative']:.2%}")
print(f"距最高价: {report['details']['dist_high']['distance_to_highest_pct']:.2f}%")
```

### 高级特征示例

```python
from stock_filter import Config
from advanced_features_factors import AdvancedFeatures

# 躁动程度分析
report = Config(
    AdvancedFeatures.agitation_level(name='agitation'),
    AdvancedFeatures.agitation_score(name='agitation_score')
).run(data)

print(f"躁动程度: {report['details']['agitation']['agitation_level']:.4f}")
print(f"躁动评分: {report['details']['agitation_score']['agitation_score']}")
```

### 洗盘识别示例

```python
from stock_filter import Config
from basic_statistics_factors import BasicStatistics
from advanced_features_factors import AdvancedFeatures

# 综合分析：识别洗盘股票
report = Config(
    # 基础条件
    BasicStatistics.trend_direction(name='trend'),
    BasicStatistics.return_total(rules=("return_total > -0.3",), name='return_ret'),

    # 洗盘识别
    AdvancedFeatures.is_wash_trading(agitation_threshold=0.2, name='is_wash'),
    AdvancedFeatures.wash_trading_intensity(name='wash_intensity')
).run(data)

if report['details']['is_wash']['is_wash_trading']:
    print("检测到洗盘特征！")
    print(f"洗盘强度: {report['details']['wash_intensity']['wash_trading_intensity']:.4f}")
```

### 链式调用示例

```python
from factor_chain import Chain
from basic_statistics_factors import BasicStatistics
from advanced_features_factors import AdvancedFeatures

# 多因子组合筛选
report = Chain(
    BasicStatistics.level_relative(rules=("level_relative >= 0.8",), name='high_position'),
    BasicStatistics.trend_direction(rules=("trend_direction == '上涨'",), name='uptrend'),
    AdvancedFeatures.agitation_level(rules=("agitation_level < 0.3",), name='low_agitation')
).and_(
    AdvancedFeatures.is_wash_trading(agitation_threshold=0.2, rules=("is_wash_trading == False",), name='not_wash')
).run(data)
```

## 测试验证

创建了完整的测试套件 `test_new_factors.py`，包含8个测试场景：

1. ✅ **测试 1**: 基础统计指标 - 价格水平
2. ✅ **测试 2**: 回撤指标
3. ✅ **测试 3**: 波动率和收益率指标
4. ✅ **测试 4**: 价格统计指标
5. ✅ **测试 5**: 趋势指标
6. ✅ **测试 6**: 高级特征指标（躁动程度）
7. ✅ **测试 7**: 洗盘识别指标
8. ✅ **测试 8**: 综合使用（基础+高级）

**所有测试均通过！**

## 技术特性

### 遵循 StockFilter 规范

所有新因子都严格遵循 StockFilter 的设计规范：

1. **类型定义**：使用 `FactorConf = Tuple[callable, Dict[str, Any], Rules, Optional[str]]`
2. **自定义名称**：支持 `name` 参数避免键名冲突
3. **规则验证**：支持 `rules` 参数进行因子过滤
4. **数据格式**：兼容 OHLCV 格式的数据字典

### 核心原则

- **KISS（简单至上）**：每个因子函数职责单一，逻辑清晰
- **DRY（杜绝重复）**：复用辅助函数，避免代码重复
- **SOLID 原则**：
  - 单一职责：每个因子只计算一个指标
  - 开闭原则：易于扩展新因子
  - 依赖倒置：依赖抽象的 FactorConf 接口

## 统计总结

### 新增因子总数：**29个**

#### 按模块分类：
- `basic_statistics_factors.py`: 23个
- `advanced_features_factors.py`: 6个

#### 按类别分类：
- 价格水平：4个
- 回撤指标：3个
- 波动率：2个
- 收益率：3个
- 最大回撤：1个
- 价格统计：7个
- 趋势判断：2个
- 躁动程度：2个
- 洗盘识别：3个
- 辅助指标：2个

### 与原有因子的关系

- **原有因子**：17个技术指标（indicators.py）
- **新增因子**：29个基础统计和高级特征
- **总计**：46个因子

## 应用场景

### 1. 量化选股
```python
# 筛选上涨趋势、低躁动、非洗盘的股票
report = Config(
    BasicStatistics.trend_direction(rules=("trend_direction == '上涨'"),),
    AdvancedFeatures.agitation_level(rules=("agitation_level < 0.3",)),
    AdvancedFeatures.is_wash_trading(rules=("is_wash_trading == False",))
).run(data)
```

### 2. 风险控制
```python
# 筛选回撤可控的股票
report = Config(
    BasicStatistics.drawdown_relative(rules=("drawdown_relative < 0.2",)),
    BasicStatistics.max_drawdown(rules=("max_drawdown < 0.3",))
).run(data)
```

### 3. 交易信号
```python
# 寻找洗盘后的机会
report = Config(
    AdvancedFeatures.is_wash_trading(agitation_threshold=0.3, rules=("is_wash_trading == True",)),
    BasicStatistics.level_relative(rules=("level_relative < 0.3",))  # 低位洗盘
).run(data)
```

## 优势

1. **完整性**：覆盖价格、回撤、波动率、收益率、趋势等多个维度
2. **专业性**：基于成熟的统计分析方法
3. **实用性**：直接来自实际交易场景的需求
4. **易用性**：统一的接口，支持链式调用和自定义名称
5. **可扩展性**：遵循 SOLID 原则，易于添加新因子

## 完成！

所有因子已成功实现并通过测试，可以直接在 StockFilter 系统中使用！
