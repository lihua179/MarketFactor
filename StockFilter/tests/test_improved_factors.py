# -*- coding: utf-8 -*-
"""
测试改进后的新因子 - 支持参数化配置和统一的 'res' 键名

改进点：
1. 所有因子都支持参数配置（如 n=20, segments=5 等）
2. 返回值统一使用 'res' 键名，便于规则编写
3. 降低使用成本：rules=("res > 0.5",) 而不用 ("level_relative > 0.5",)
"""
from stock_filter import Config
from basic_statistics_factors import BasicStatistics
from advanced_features_factors import AdvancedFeatures
from factor_chain import Chain


def create_test_data():
    """创建测试数据（模拟真实股票数据）"""
    return {
        'open': [10.0, 10.2, 10.5, 10.3, 10.8, 11.0, 10.9, 11.2, 11.5, 11.3,
                 11.8, 12.0, 11.7, 12.2, 12.5, 12.3, 12.8, 13.0, 12.7, 13.2,
                 13.5, 13.1, 13.8, 14.0, 13.6, 14.2, 14.5, 14.1, 14.8],
        'high': [10.5, 10.8, 11.0, 10.9, 11.2, 11.5, 11.3, 11.8, 12.0, 11.9,
                 12.2, 12.5, 12.3, 12.8, 13.0, 12.9, 13.2, 13.5, 13.1, 13.8,
                 14.0, 14.2, 13.9, 14.5, 14.1, 14.8, 15.0, 14.6, 15.2, 15.5],
        'low': [9.5, 9.8, 10.0, 10.1, 10.5, 10.7, 10.6, 10.9, 11.1, 11.0,
                11.5, 11.6, 11.4, 11.9, 12.1, 12.0, 12.4, 12.6, 12.3, 12.9,
                13.1, 12.8, 13.3, 13.6, 13.4, 13.9, 14.1, 13.8, 14.2, 14.5],
        'close': [10.0, 10.5, 10.8, 10.6, 11.0, 11.2, 11.0, 11.5, 11.8, 11.6,
                  12.0, 12.2, 12.0, 12.5, 12.8, 12.5, 13.0, 13.2, 12.9, 13.5,
                  13.8, 13.4, 14.0, 13.7, 14.2, 14.5, 14.2, 14.8, 15.0, 15.5],
        'volume': [10000, 11000, 12000, 11500, 13000, 14000, 12500, 15000, 16000, 14500,
                   17000, 18000, 16500, 19000, 20000, 18500, 21000, 22000, 20500, 23000,
                   24000, 22500, 25000, 23500, 26000, 27000, 25500, 28000, 29000, 30000],
        'yd_close': [9.5, 10.0, 10.5, 10.8, 10.6, 11.0, 11.2, 11.0, 11.5, 11.8,
                     11.6, 12.0, 12.2, 12.0, 12.5, 12.8, 12.5, 13.0, 13.2, 12.9,
                     13.5, 13.8, 13.4, 14.0, 13.7, 14.2, 14.5, 14.2, 14.8, 15.0]
    }


def demo_parameter_support():
    """演示1: 参数化配置支持"""
    print("\n" + "="*70)
    print("演示 1: 参数化配置支持")
    print("="*70)

    data = create_test_data()

    # 使用不同的周期参数
    report = Config(
        BasicStatistics.level_relative(n=10, name='level_10d'),
        BasicStatistics.level_relative(n=20, name='level_20d'),
        BasicStatistics.level_relative(n=30, name='level_30d')
    ).run(data)

    print("\n配置（使用不同周期）:")
    print("  BasicStatistics.level_relative(n=10, name='level_10d')")
    print("  BasicStatistics.level_relative(n=20, name='level_20d')")
    print("  BasicStatistics.level_relative(n=30, name='level_30d')")

    print("\n结果:")
    print(f"  通过: {report['pass']}")
    print(f"  详情键: {list(report['details'].keys())}")

    if report['pass']:
        print(f"\n  10日相对分位: {report['details']['level_10d']['res']:.2%}")
        print(f"  20日相对分位: {report['details']['level_20d']['res']:.2%}")
        print(f"  30日相对分位: {report['details']['level_30d']['res']:.2%}")
        print("\n[SUCCESS] 参数化配置测试通过 [OK]")


def demo_unified_res_key():
    """演示2: 统一的 'res' 键名"""
    print("\n" + "="*70)
    print("演示 2: 统一的 'res' 键名（降低使用成本）")
    print("="*70)

    data = create_test_data()

    print("\n旧方式（使用具体指标名）:")
    print("  rules=('level_relative > 0.8',)  # 需要记住指标名")
    print("\n新方式（统一使用 'res'）:")
    print("  rules=('res > 0.8',)  # 简洁明了！")

    report = Config(
        BasicStatistics.level_relative(n=20, rules=("res > 0",), name='high_price'),
        BasicStatistics.return_total(n=20, rules=("res > 0.1",), name='profitable'),
        BasicStatistics.trend_direction(rules=("res == '上涨'",), name='uptrend')
    ).run(data)

    print("\n配置:")
    print("  BasicStatistics.level_relative(n=20, rules=('res > 0',), name='high_price')")
    print("  BasicStatistics.return_total(n=20, rules=('res > 0.1',), name='profitable')")
    print("  BasicStatistics.trend_direction(rules=(\"res == '上涨'\"), name='uptrend')")

    print("\n结果:")
    print(f"  通过: {report['pass']}")
    print(f"  详情键: {list(report['details'].keys())}")

    if report['pass']:
        print(f"\n  高位: {report['details']['high_price']['res']:.2%}")
        print(f"  盈利: {report['details']['profitable']['res']:.2%}")
        print(f"  趋势: {report['details']['uptrend']['res']}")
        print("\n[SUCCESS] 统一 'res' 键名测试通过 [OK]")


def demo_advanced_with_parameters():
    """演示3: 高级特征 + 参数化配置"""
    print("\n" + "="*70)
    print("演示 3: 高级特征 + 参数化配置")
    print("="*70)

    data = create_test_data()

    # 使用不同的躁动阈值
    report = Config(
        AdvancedFeatures.agitation_level(name='agitation'),
        AdvancedFeatures.is_wash_trading(agitation_threshold=0.15, name='wash_15'),
        AdvancedFeatures.is_wash_trading(agitation_threshold=0.25, name='wash_25'),
        AdvancedFeatures.is_wash_trading(agitation_threshold=0.35, name='wash_35')
    ).run(data)

    print("\n配置（使用不同躁动阈值）:")
    print("  AdvancedFeatures.agitation_level(name='agitation')")
    print("  AdvancedFeatures.is_wash_trading(agitation_threshold=0.15, name='wash_15')")
    print("  AdvancedFeatures.is_wash_trading(agitation_threshold=0.25, name='wash_25')")
    print("  AdvancedFeatures.is_wash_trading(agitation_threshold=0.35, name='wash_35')")

    print("\n结果:")
    print(f"  通过: {report['pass']}")
    print(f"  详情键: {list(report['details'].keys())}")

    if report['pass']:
        agitation = report['details']['agitation']['res']
        print(f"\n  躁动程度: {agitation:.4f}")
        print(f"  阈值0.15: {report['details']['wash_15']['res']}")
        print(f"  阈值0.25: {report['details']['wash_25']['res']}")
        print(f"  阈值0.35: {report['details']['wash_35']['res']}")
        print("\n[SUCCESS] 高级特征参数化测试通过 [OK]")


def demo_practical_usage():
    """演示4: 实际应用场景"""
    print("\n" + "="*70)
    print("演示 4: 实际应用场景 - 选股策略")
    print("="*70)

    data = create_test_data()

    # 选股策略：上涨趋势 + 高位 + 低躁动 + 非洗盘
    report = Config(
        # 趋势判断（使用5段判断更准确）
        BasicStatistics.trend_direction(segments=5, rules=("res == '上涨'",), name='trend'),

        # 价格位置（最近20天）
        BasicStatistics.level_relative(n=20, rules=("res > 0.8",), name='high_position'),

        # 收益率（最近30天）
        BasicStatistics.return_total(n=30, rules=("res > 0.2",), name='good_return'),

        # 躁动程度（要低）
        AdvancedFeatures.agitation_level(rules=("res < 0.3",), name='low_agitation'),

        # 不能是洗盘
        AdvancedFeatures.is_wash_trading(agitation_threshold=0.2, rules=("res == False",), name='not_wash')
    ).run(data)

    print("\n选股策略:")
    print("  1. 上涨趋势")
    print("  2. 价格高位（>80%）")
    print("  3. 收益率良好（>20%）")
    print("  4. 躁动程度低（<0.3）")
    print("  5. 非洗盘")

    print("\n配置:")
    print("  BasicStatistics.trend_direction(segments=5, rules=(\"res == '上涨'\"), name='trend')")
    print("  BasicStatistics.level_relative(n=20, rules=('res > 0.8',), name='high_position')")
    print("  BasicStatistics.return_total(n=30, rules=('res > 0.2',), name='good_return')")
    print("  AdvancedFeatures.agitation_level(rules=('res < 0.3',), name='low_agitation')")
    print("  AdvancedFeatures.is_wash_trading(agitation_threshold=0.2, rules=('res == False',), name='not_wash')")

    print("\n结果:")
    print(f"  通过: {report['pass']}")
    print(f"  详情键: {list(report['details'].keys())}")

    if report['pass']:
        print(f"\n  [OK] 策略通过！")
        print(f"    趋势: {report['details']['trend']['res']}")
        print(f"    位置: {report['details']['high_position']['res']:.2%}")
        print(f"    收益: {report['details']['good_return']['res']:.2%}")
        print(f"    躁动: {report['details']['low_agitation']['res']:.4f}")
        print(f"    洗盘: {report['details']['not_wash']['res']}")
        print("\n[SUCCESS] 实际应用测试通过 [OK]")
    else:
        print("\n  [FAIL] 策略未通过")


def demo_comparison():
    """演示5: 新旧对比"""
    print("\n" + "="*70)
    print("演示 5: 新旧对比 - 展示改进")
    print("="*70)

    data = create_test_data()

    print("\n旧版本问题:")
    print("  问题1: 不支持参数，只能使用全部数据")
    print("  问题2: 规则中需要写具体指标名，如:")
    print("           rules=('level_relative > 0.8',)")
    print("  问题3: 不同因子返回不同键名，记忆负担大")

    print("\n新版本优势:")
    print("  [OK] 支持参数: n=20, segments=5, agitation_threshold=0.3")
    print("  [OK] 统一键名: 规则中统一使用 'res'")
    print("  [OK] 更简洁:  rules=('res > 0.8',)")
    print("  [OK] 更灵活: 可以配置多个周期的同一指标")

    report = Config(
        BasicStatistics.return_total(n=10, rules=("res > 0",), name='ret_10d'),
        BasicStatistics.return_total(n=20, rules=("res > 0.05",), name='ret_20d'),
        BasicStatistics.return_total(n=30, rules=("res > 0.1",), name='ret_30d')
    ).run(data)

    print("\n示例: 使用不同周期的收益率")
    print("  return_total(n=10, rules=('res > 0',), name='ret_10d')")
    print("  return_total(n=20, rules=('res > 0.05',), name='ret_20d')")
    print("  return_total(n=30, rules=('res > 0.1',), name='ret_30d')")

    print("\n结果:")
    print(f"  通过: {report['pass']}")
    if report['pass']:
        print(f"  10日收益: {report['details']['ret_10d']['res']:.2%}")
        print(f"  20日收益: {report['details']['ret_20d']['res']:.2%}")
        print(f"  30日收益: {report['details']['ret_30d']['res']:.2%}")
        print("\n[SUCCESS] 新旧对比演示完成 [OK]")


def print_summary():
    """打印改进总结"""
    print("\n" + "="*70)
    print("改进总结")
    print("="*70)

    print("\n[OK] 改进点 1: 支持参数化配置")
    print("  - n: 统计周期（如 n=20 表示最近20个数据）")
    print("  - segments: 趋势分段数（默认3段）")
    print("  - agitation_threshold: 洗盘躁动阈值（默认0.2）")

    print("\n[OK] 改进点 2: 统一使用 'res' 作为结果键名")
    print("  - 旧版: rules=('level_relative > 0.8',)")
    print("  - 新版: rules=('res > 0.8',)")
    print("  - 优势: 更简洁、更易记、降低使用成本")

    print("\n[OK] 改进点 3: 完全向后兼容")
    print("  - 支持自定义名称（name 参数）")
    print("  - 支持规则验证（rules 参数）")
    print("  - 支持链式调用（.and_() 方法）")

    print("\n使用示例:")
    print("  # 简洁的规则编写")
    print("  BasicStatistics.level_relative(n=20, rules=('res > 0.8',))")
    print("")
    print("  # 多周期配置")
    print("  Config(")
    print("    BasicStatistics.return_total(n=10, name='ret10'),")
    print("    BasicStatistics.return_total(n=20, name='ret20'),")
    print("    BasicStatistics.return_total(n=30, name='ret30')")
    print("  )")

    print("\n所有改进测试完成！ [COMPLETE]")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("改进后的新因子功能测试")
    print("测试参数化配置和统一的 'res' 键名")
    print("="*70)

    # 运行所有演示
    demo_parameter_support()
    demo_unified_res_key()
    demo_advanced_with_parameters()
    demo_practical_usage()
    demo_comparison()

    # 打印总结
    print_summary()
