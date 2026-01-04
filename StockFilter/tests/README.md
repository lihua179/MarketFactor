# Tests - 测试文件

本目录包含 StockFilter 系统的所有测试文件。

## 📁 测试文件列表

### 核心功能测试

#### `test_new_factors.py` - 新增因子测试（29个因子）
测试从 `demo_indicators` 移植的29个新因子：

1. **测试1**: 基础统计指标 - 价格水平
2. **测试2**: 回撤指标
3. **测试3**: 波动率和收益率指标
4. **测试4**: 价格统计指标
5. **测试5**: 趋势指标
6. **测试6**: 高级特征指标（躁动程度）
7. **测试7**: 洗盘识别指标
8. **测试8**: 综合使用（基础+高级）

**运行**:
```bash
cd tests
python test_new_factors.py
```

#### `test_improved_factors.py` - 改进后因子测试
测试参数化配置和统一 'res' 键名的改进：

1. **演示1**: 参数化配置支持（n=10, 20, 30）
2. **演示2**: 统一 'res' 键名
3. **演示3**: 高级特征 + 参数化
4. **演示4**: 实际应用场景 - 选股策略
5. **演示5**: 新旧对比

**运行**:
```bash
python test_improved_factors.py
```

### 特性测试

#### `test_custom_name.py` - 自定义名称功能测试
测试避免键名冲突的自定义名称功能。

**运行**:
```bash
python test_custom_name.py
```

#### `custom_name_usage.py` - 自定义名称使用示例
展示如何使用自定义名称功能。

### 其他测试

#### `test_demo.py` - 原始系统测试
测试原始的17个技术指标功能。

#### `test_user_example.py` - 用户示例测试
测试用户提供的使用案例。

---

## 🧪 运行所有测试

### 运行单个测试

```bash
# 测试新增因子
python tests/test_new_factors.py

# 测试改进后的因子
python tests/test_improved_factors.py

# 测试自定义名称
python tests/test_custom_name.py
```

### 运行所有测试

```bash
cd tests
for %%f in (test_*.py) do python %%f
```

---

## 📊 测试覆盖

| 测试文件 | 测试场景数 | 状态 |
|----------|-----------|------|
| test_new_factors.py | 8 | ✅ 全部通过 |
| test_improved_factors.py | 5 | ✅ 全部通过 |
| test_custom_name.py | 多个 | ✅ 通过 |
| test_demo.py | 6 | ✅ 通过 |

---

## 🔧 测试数据

所有测试都使用模拟数据，无需真实行情数据。

测试数据格式：
```python
data = {
    'open': [10.0, 10.2, 10.5, ...],
    'high': [10.5, 10.8, 11.0, ...],
    'low': [9.5, 9.8, 10.0, ...],
    'close': [10.0, 10.5, 10.8, ...],
    'volume': [10000, 11000, 12000, ...],
    'yd_close': [9.5, 10.0, 10.5, ...]
}
```

---

## ✅ 测试检查清单

运行测试前确保：

- [ ] 已安装所有依赖 (`pip install -r requirements.txt`)
- [ ] 当前目录为 StockFilter 根目录
- [ ] Python 版本 >= 3.7

---

## 📝 添加新测试

添加新测试时，请遵循以下规范：

1. 使用描述性的测试文件名（`test_*.py`）
2. 包含多个测试场景
3. 使用清晰的输出（使用分隔线、标题等）
4. 验证所有关键功能
5. 包含测试结果摘要

**测试模板**:
```python
# -*- coding: utf-8 -*-
"""
测试 XXX 功能
"""
from core.stock_filter import Config
from core.basic_statistics_factors import BasicStatistics

def create_test_data():
    """创建测试数据"""
    return {
        'open': [...],
        'high': [...],
        'low': [...],
        'close': [...],
        'volume': [...],
        'yd_close': [...]
    }

def test_xxx():
    """测试 XXX"""
    print("\n" + "="*70)
    print("测试: XXX")
    print("="*70)

    data = create_test_data()
    result = Config(...).run(data)

    # 验证结果
    assert result['pass'] == True
    print("✓ 测试通过")

if __name__ == "__main__":
    test_xxx()
    print("\n所有测试完成！")
```

---

## 🎓 测试最佳实践

1. **独立性**: 每个测试应该独立运行
2. **清晰性**: 使用清晰的测试名称和输出
3. **完整性**: 测试成功和失败场景
4. **可维护性**: 使用辅助函数（如 `create_test_data()`）
5. **文档化**: 添加清晰的文档字符串

---

**最后更新**: 2025-01-04
**测试状态**: 全部通过 ✅
