# -*- coding: utf-8 -*-
"""
验证用户原始需求示例

来自 stock_filter.py 第95-109行的代码
"""
from stock_filter import Config
from indicators import Factor as IndicatorsFactor
from factor import Factor as FactorFactor


class Factor(IndicatorsFactor):
    """合并的因子配置类"""
    price_level = FactorFactor.price_level
    daily_vol = FactorFactor.daily_vol


def create_test_data():
    """创建测试数据"""
    return {
        'open': [10.0, 10.5, 11.0, 11.5, 12.0] * 10,
        'high': [10.5, 11.0, 11.5, 12.0, 12.5] * 10,
        'low': [9.5, 10.0, 10.5, 11.0, 11.5] * 10,
        'close': [10.0, 10.5, 11.0, 11.5, 12.0] * 10,
        'volume': [10000, 11000, 12000, 13000, 14000] * 10,
        'yd_close': [9.5, 10.0, 10.5, 11.0, 11.5] * 10
    }


if __name__ == "__main__":
    print("="*70)
    print("验证用户原始需求示例")
    print("="*70)

    data = create_test_data()

    # 用户原始代码（来自 stock_filter.py 第95-109行）
    report = Config(
        Factor.price_level(n=30),
        Factor.daily_vol(n=30, rules=("daily_vol < 1.15",), name='daily_vol101')
    ).run(data)

    print("\n配置代码:")
    print("  report = Config(")
    print("      Factor.price_level(n=30),")
    print("      Factor.daily_vol(n=30, rules=('daily_vol < 1.15',), name='daily_vol101')")
    print("  ).run(data)")

    print("\n执行结果:")
    print(f"  通过: {report['pass']}")
    print(f"  详情键: {list(report['details'].keys())}")
    print(f"  完整详情: {report['details']}")

    # 验证结果
    expected_keys = ['price_level', 'daily_vol101']
    actual_keys = list(report['details'].keys())

    if actual_keys == expected_keys:
        print("\n[SUCCESS] 用户原始需求验证成功！")
        print("  - price_level: 使用默认名称")
        print("  - daily_vol101: 使用自定义名称 'daily_vol101'")
    else:
        print(f"\n[FAIL] 键名不匹配")
        print(f"  期望: {expected_keys}")
        print(f"  实际: {actual_keys}")

    print("\n" + "="*70)
    print("验证完成")
    print("="*70)
