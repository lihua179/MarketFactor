# 自定义名称功能实现总结

## 概述

成功为 StockFilter 框架添加了自定义名称功能，允许用户在配置因子时指定自定义的详情键名，避免了数字序号的局限性。

## 核心改动

### 1. 类型定义更新

**文件**: `factor.py`, `stock_filter.py`, `indicators.py`

```python
# 旧版（3元组）
FactorConf = Tuple[Callable, Dict, Any], Rules]

# 新版（4元组，向后兼容）
FactorConf = Tuple[Callable[[Dict[str, List], Any], Dict[str, Any]], Dict[str, Any], Rules, Optional[str]]
#                                                                                            ^^^^^^^^^^^^^^^^
#                                                                                            自定义名称参数
```

### 2. 核心逻辑更新

**文件**: `stock_filter.py` 的 `run_one()` 函数

```python
def run_one(data: Dict[str, List], chain: List[FactorConf]) -> Dict[str, Any]:
    details, ok = {}, True
    func_count = {}

    for item in chain:
        # 支持3元组（旧）和4元组（新）
        if len(item) == 4:
            func, params, rules, custom_name = item
        else:
            func, params, rules = item
            custom_name = None

        # 执行因子
        res = func(data, **params)
        if not pass_filter(res, rules):
            ok = False
            break

        # 优先使用自定义名称
        if custom_name is not None:
            key = custom_name
        else:
            # 自动编号逻辑（只统计没有自定义名称的调用）
            func_count[func_name] = func_count.get(func_name, 0) + 1
            count = func_count[func_name]

            if count == 1:
                key = func_name
            else:
                if count == 2:
                    # 发现重复，修改第1次的键名
                    old_key = func_name
                    new_key = f"{func_name}1"
                    if old_key in details:
                        details[new_key] = details.pop(old_key)
                key = f"{func_name}{count}"

        details[key] = res

    return {"pass": ok, "details": details}
```

### 3. Factor 类更新

**文件**: `indicators.py`（17个方法全部更新）

```python
@staticmethod
def ma(n: int = 5, rules: Rules = ("ma > 0",), name: Optional[str] = None) -> FactorConf:
    """移动平均线"""
    return _ma, {"n": n}, rules, name
                               # ^^^^ 新增参数

# 其他16个方法同理：
# ema, close_price, high_price, low_price, volume,
# max_price, min_price, price_range, return_rate,
# cumulative_return, volatility, volume_mean, volume_ratio,
# rsi, bollinger_upper, bollinger_lower
```

## 使用示例

### 基本用法

```python
from stock_filter import Config
from indicators import Factor

# 用户原始需求（来自 stock_filter.py:95-109）
report = Config(
    Factor.price_level(n=30),
    Factor.daily_vol(n=30, rules=("daily_vol < 1.15",), name='daily_vol101')
).run(data)

# 结果：
# {
#     'pass': True,
#     'details': {
#         'price_level': {'price_level': 0.83},
#         'daily_vol101': {'daily_vol': 0.096}  # 使用自定义名称
#     }
# }
```

### 多周期策略

```python
# 多周期均线
report = Config(
    Factor.ma(n=5, name='ma5', rules=("ma > 0",)),
    Factor.ma(n=10, name='ma10', rules=("ma > 0",)),
    Factor.ma(n=20, name='ma20', rules=("ma > 0",)),
    Factor.ma(n=60, name='ma60', rules=("ma > 0",))
).run(data)

# 详情键：['ma5', 'ma10', 'ma20', 'ma60']
# 方便访问：report['details']['ma5']['ma']
```

### 混合使用

```python
# 自定义名称 + 自动编号
report = Config(
    Factor.ma(n=5, name='short_ma', rules=("ma > 0",)),    # 自定义
    Factor.ma(n=20, name='long_ma', rules=("ma > 0",)),    # 自定义
    Factor.rsi(n=14, rules=("rsi > 0",)),                  # 自动编号：rsi
    Factor.rsi(n=6, rules=("rsi > 0",))                    # 自动编号：rsi1
).run(data)

# 详情键：['short_ma', 'long_ma', 'rsi1', 'rsi2']
```

### 链式调用

```python
from factor_chain import Chain

report = Chain(
    Factor.ma(n=5, name='ma5', rules=("ma > 0",)),
    Factor.rsi(n=14, name='rsi14', rules=("rsi > 30",))
).and_(
    Factor.volatility(n=20, name='vol20', rules=("volatility > 0",))
).run(data)

# 详情键：['ma5', 'rsi14', 'vol20']
```

## 重要说明

### 规则验证与自定义名称

**关键点**：规则中使用的是因子函数返回的键名，而不是自定义的详情键名。

```python
# 正确 ✅
Factor.ma(n=5, name='ma5', rules=("ma > 0",))
#                      ^^^^^^ 自定义详情键名
#                            ^^^^ 规则中使用函数返回的键名

# 错误 ❌
Factor.ma(n=5, name='ma5', rules=("ma5 > 0",))
#                            ^^^^ 规则中不能用自定义名称
```

**原因**：
- 因子函数 `_ma()` 返回 `{"ma": 13.0}`
- 规则验证时使用这个返回值
- 自定义名称只影响在 `details` 中保存的键名
- 访问值：`report['details']['ma5']['ma']`（外层用自定义名，内层用函数返回名）

### 向后兼容性

完全支持旧的3元组格式：

```python
# 旧代码无需修改，继续工作
old_config = [
    (_ma, {"n": 5}, ("ma > 0",)),
    (_rsi, {"n": 14}, ("rsi > 0",))
]
report = Config(*old_config).run(data)
# 详情键：['ma', 'rsi']
```

## 测试覆盖

创建了完整的测试套件 `test_custom_name.py`：

1. **测试 1**: 自定义名称基本功能 ✅
2. **测试 2**: 混合使用自定义名称和自动编号 ✅
3. **测试 3**: 重复函数使用不同自定义名称 ✅
4. **测试 4**: 向后兼容性（3元组） ✅
5. **测试 5**: 链式调用 + 自定义名称 ✅

所有测试均通过！

## 新增文件

1. **factor_chain.py**: 链式调用支持
2. **test_custom_name.py**: 完整测试套件（5个测试）
3. **custom_name_usage.py**: 使用示例（5个示例）
4. **debug_values.py**: 调试脚本

## 修改文件

1. **stock_filter.py**: 核心逻辑，支持4元组
2. **indicators.py**: 17个因子方法添加 `name` 参数
3. **factor.py**: 类型定义更新

## 设计原则

### KISS（简单至上）
- API 简单：只需添加 `name` 参数
- 逻辑清晰：优先级明确（自定义 > 自动）

### DRY（杜绝重复）
- 统一的配置接口
- 复用现有的自动编号逻辑

### SOLID
- **单一职责**：`run_one` 只负责执行和命名
- **开闭原则**：扩展支持4元组，不修改3元组行为
- **里氏替换**：3元组和4元组可互换使用

## 优势

1. **可读性**: 详情键名具有业务含义（`ma5`, `short_ma` vs `ma1`, `ma2`）
2. **可维护性**: 清晰的命名便于后续修改和调试
3. **灵活性**: 支持自定义名称、自动编号、混合使用
4. **向后兼容**: 不影响现有代码
5. **健壮性**: 避免键名冲突导致的覆盖问题

## 完成状态

✅ **功能实现完成**
- 核心逻辑实现
- 17个因子方法更新
- 链式调用支持
- 向后兼容保证

✅ **测试验证完成**
- 5个测试场景
- 所有测试通过
- 边界情况覆盖

✅ **文档完善**
- 使用示例
- 测试套件
- 总结文档
