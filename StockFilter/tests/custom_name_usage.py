# -*- coding: utf-8 -*-
"""
自定义名称功能使用示例

演示如何在 StockFilter 框架中使用自定义名称来避免因子键名冲突
"""
from stock_filter import Config
from factor_chain import Chain
from indicators import Factor as IndicatorsFactor
from factor import Factor as FactorFactor


class Factor(IndicatorsFactor):
    """合并的因子配置类，包含所有指标"""
    price_level = FactorFactor.price_level
    daily_vol = FactorFactor.daily_vol


def create_sample_data():
    """创建示例数据"""
    return {
        'open': [10.0, 10.5, 11.0, 11.5, 12.0] * 10,
        'high': [10.5, 11.0, 11.5, 12.0, 12.5] * 10,
        'low': [9.5, 10.0, 10.5, 11.0, 11.5] * 10,
        'close': [10.0, 10.5, 11.0, 11.5, 12.0] * 10,
        'volume': [10000, 11000, 12000, 13000, 14000] * 10,
        'yd_close': [9.5, 10.0, 10.5, 11.0, 11.5] * 10
    }


# ========== 示例 1: 用户原始需求 ==========
def example_user_requirement():
    """
    用户原始需求示例
    来自 stock_filter.py 第95-109行
    """
    print("\n" + "="*70)
    print("示例 1: 用户原始需求")
    print("="*70)

    data = create_sample_data()

    report = Config(
        Factor.price_level(n=30),
        Factor.daily_vol(n=30, rules=("daily_vol < 1.15",), name='daily_vol101')
    ).run(data)

    print("\n配置:")
    print("  Factor.price_level(n=30)")
    print("  Factor.daily_vol(n=30, rules=('daily_vol < 1.15',), name='daily_vol101')")

    print("\n结果:")
    print(f"  通过: {report['pass']}")
    print(f"  详情键: {list(report['details'].keys())}")
    print(f"  详情内容: {report['details']}")


# ========== 示例 2: 多周期均线 ==========
def example_multi_period_ma():
    """多周期均线策略"""
    print("\n" + "="*70)
    print("示例 2: 多周期均线策略")
    print("="*70)

    data = create_sample_data()

    report = Config(
        Factor.ma(n=5, name='ma5', rules=("ma > 0",)),
        Factor.ma(n=10, name='ma10', rules=("ma > 0",)),
        Factor.ma(n=20, name='ma20', rules=("ma > 0",)),
        Factor.ma(n=60, name='ma60', rules=("ma > 0",))
    ).run(data)

    print("\n配置:")
    print("  Factor.ma(n=5, name='ma5')    # 规则使用 'ma > 0'")
    print("  Factor.ma(n=10, name='ma10')  # 规则使用 'ma > 0'")
    print("  Factor.ma(n=20, name='ma20')  # 规则使用 'ma > 0'")
    print("  Factor.ma(n=60, name='ma60')  # 规则使用 'ma > 0')")

    print("\n结果:")
    print(f"  通过: {report['pass']}")
    print(f"  详情键: {list(report['details'].keys())}")

    # 可以方便地访问各个均线值
    if 'ma5' in report['details']:
        print(f"\n  均线值:")
        print(f"    MA5: {report['details']['ma5']['ma']:.2f}")   # 注意：这里用 'ma' 不是 'ma5'
        print(f"    MA10: {report['details']['ma10']['ma']:.2f}")
        print(f"    MA20: {report['details']['ma20']['ma']:.2f}")
        print(f"    MA60: {report['details']['ma60']['ma']:.2f}")
        print("\n  说明: 虽然details中用的是自定义键名(ma5)，但值仍是{'ma': 13.0}格式")


# ========== 示例 3: 混合使用自定义名称和自动编号 ==========
def example_mixed_naming():
    """混合使用自定义名称和自动编号"""
    print("\n" + "="*70)
    print("示例 3: 混合使用自定义名称和自动编号")
    print("="*70)

    data = create_sample_data()

    report = Config(
        # 重要的指标用有意义的自定义名称
        Factor.ma(n=5, name='short_ma', rules=("ma > 0",)),
        Factor.ma(n=20, name='long_ma', rules=("ma > 0",)),

        # 辅助指标用自动编号
        Factor.rsi(n=14, rules=("rsi > 0",)),
        Factor.rsi(n=6, rules=("rsi > 0",))  # 会自动编号为 rsi1
    ).run(data)

    print("\n配置:")
    print("  Factor.ma(n=5, name='short_ma')  # 自定义名称，规则用 'ma > 0'")
    print("  Factor.ma(n=20, name='long_ma')  # 自定义名称，规则用 'ma > 0'")
    print("  Factor.rsi(n=14)                 # 自动编号: rsi")
    print("  Factor.rsi(n=6)                  # 自动编号: rsi1")

    print("\n结果:")
    print(f"  通过: {report['pass']}")
    print(f"  详情键: {list(report['details'].keys())}")


# ========== 示例 4: 链式调用 + 自定义名称 ==========
def example_chain_with_custom_names():
    """链式调用配合自定义名称"""
    print("\n" + "="*70)
    print("示例 4: 链式调用 + 自定义名称")
    print("="*70)

    data = create_sample_data()

    report = Chain(
        Factor.ma(n=5, name='ma5', rules=("ma > 0",)),
        Factor.volume_ratio(n=5, name='vr', rules=("volume_ratio > 1",))
    ).and_(
        Factor.rsi(n=14, name='rsi14', rules=("rsi > 30",)),
        Factor.rsi(n=6, name='rsi6', rules=("rsi < 70",))
    ).and_(
        Factor.return_rate(n=5, name='return_5d', rules=("return_rate > -0.05",))
    ).run(data)

    print("\n配置:")
    print("  Chain(")
    print("    Factor.ma(n=5, name='ma5', rules=('ma > 0',)),")
    print("    Factor.volume_ratio(n=5, name='vr', rules=('volume_ratio > 1',))")
    print("  ).and_(")
    print("    Factor.rsi(n=14, name='rsi14', rules=('rsi > 30',)),")
    print("    Factor.rsi(n=6, name='rsi6', rules=('rsi < 70',))")
    print("  ).and_(")
    print("    Factor.return_rate(n=5, name='return_5d', rules=('return_rate > -0.05',))")
    print("  ).run(data)")

    print("\n结果:")
    print(f"  通过: {report['pass']}")
    print(f"  详情键: {list(report['details'].keys())}")


# ========== 示例 5: 向后兼容 ==========
def example_backward_compatibility():
    """向后兼容旧代码"""
    print("\n" + "="*70)
    print("示例 5: 向后兼容旧代码（3元组）")
    print("="*70)

    data = create_sample_data()

    # 旧代码（3元组）仍然可以使用
    old_style_config = [
        (Factor.ma, {"n": 5, "rules": ("ma > 0",), "name": "ma5"}, None),
        (Factor.rsi, {"n": 14, "rules": ("rsi > 0",), "name": "rsi14"}, None)
    ]

    # 更简洁的写法
    report = Config(
        Factor.ma(n=5, rules=("ma > 0",)),
        Factor.rsi(n=14, rules=("rsi > 0",))
    ).run(data)

    print("\n配置:")
    print("  Factor.ma(n=5, rules=('ma > 0',))")
    print("  Factor.rsi(n=14, rules=('rsi > 0',))")

    print("\n结果:")
    print(f"  通过: {report['pass']}")
    print(f"  详情键: {list(report['details'].keys())}")
    print("\n说明: 旧代码无需修改，新代码可以使用 name 参数增强可读性")


# ========== 总结 ==========
def print_summary():
    """打印功能总结"""
    print("\n" + "="*70)
    print("自定义名称功能总结")
    print("="*70)

    print("\n核心特性:")
    print("  1. 自定义名称: 使用 name 参数为因子指定有意义的名称")
    print("  2. 优先级: 自定义名称 > 自动编号")
    print("  3. 向后兼容: 3元组和4元组配置都支持")
    print("  4. 灵活混合: 可以同时使用自定义名称和自动编号")

    print("\n使用场景:")
    print("  - 多周期策略: ma5, ma10, ma20, ma60")
    print("  - 多参数策略: rsi14, rsi6, volatility10, volatility20")
    print("  - 业务语义: short_ma, long_ma, entry_signal, exit_signal")
    print("  - 避免冲突: 同一函数多次调用时使用不同名称")

    print("\n代码质量提升:")
    print("  - 可读性: 详情键名具有业务含义")
    print("  - 可维护性: 清晰的命名便于后续修改")
    print("  - 可调试性: 快速定位问题因子")
    print("  - 健壮性: 避免键名冲突导致的覆盖问题")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("自定义名称功能使用示例")
    print("="*70)

    # 运行所有示例
    example_user_requirement()
    example_multi_period_ma()
    example_mixed_naming()
    example_chain_with_custom_names()
    example_backward_compatibility()

    # 打印总结
    print_summary()

    print("\n" + "="*70)
    print("所有示例运行完成！")
    print("="*70)
