# -*- coding: utf-8 -*-
"""
测试新增的基础统计和高级特征因子

验证从 demo_indicators 中移植的所有因子功能
"""
from stock_filter import Config
from basic_statistics_factors import BasicStatistics
from advanced_features_factors import AdvancedFeatures
from factor_chain import Chain


def create_test_data():
    """创建测试数据（模拟真实股票数据）"""
    return {
        'open': [10.0, 10.2, 10.5, 10.3, 10.8, 11.0, 10.9, 11.2, 11.5, 11.3,
                 11.8, 12.0, 11.7, 12.2, 12.5, 12.3, 12.8, 13.0, 12.7, 13.2],
        'high': [10.5, 10.8, 11.0, 10.9, 11.2, 11.5, 11.3, 11.8, 12.0, 11.9,
                 12.2, 12.5, 12.3, 12.8, 13.0, 12.9, 13.2, 13.5, 13.1, 13.8],
        'low': [9.5, 9.8, 10.0, 10.1, 10.5, 10.7, 10.6, 10.9, 11.1, 11.0,
                11.5, 11.6, 11.4, 11.9, 12.1, 12.0, 12.4, 12.6, 12.3, 12.9],
        'close': [10.0, 10.5, 10.8, 10.6, 11.0, 11.2, 11.0, 11.5, 11.8, 11.6,
                  12.0, 12.2, 12.0, 12.5, 12.8, 12.5, 13.0, 13.2, 12.9, 13.5],
        'volume': [10000, 11000, 12000, 11500, 13000, 14000, 12500, 15000, 16000, 14500,
                   17000, 18000, 16500, 19000, 20000, 18500, 21000, 22000, 20500, 23000],
        'yd_close': [9.5, 10.0, 10.5, 10.8, 10.6, 11.0, 11.2, 11.0, 11.5, 11.8,
                     11.6, 12.0, 12.2, 12.0, 12.5, 12.8, 12.5, 13.0, 13.2, 12.9]
    }


def test_basic_statistics():
    """测试基础统计指标"""
    print("\n" + "="*70)
    print("测试 1: 基础统计指标")
    print("="*70)

    data = create_test_data()

    # 价格水平指标
    report = Config(
        BasicStatistics.level_relative(name='level_rel'),
        BasicStatistics.level_absolute(name='level_abs'),
        BasicStatistics.distance_to_highest_pct(name='dist_high'),
        BasicStatistics.distance_to_lowest_pct(name='dist_low')
    ).run(data)

    print("\n价格水平指标:")
    print(f"  通过: {report['pass']}")
    print(f"  详情键: {list(report['details'].keys())}")

    if report['pass']:
        details = report['details']
        print(f"\n  结果:")
        print(f"    相对分位: {details['level_rel']['level_relative']:.4f}")
        print(f"    绝对分位: {details['level_abs']['level_absolute']:.4f}")
        print(f"    距最高价%: {details['dist_high']['distance_to_highest_pct']:.2f}%")
        print(f"    距最低价%: {details['dist_low']['distance_to_lowest_pct']:.2f}%")

        print("\n[SUCCESS] 基础统计指标测试通过 [OK]")
    else:
        print("\n[FAIL] 基础统计指标测试失败 [FAIL]")

    return report


def test_drawdown_indicators():
    """测试回撤指标"""
    print("\n" + "="*70)
    print("测试 2: 回撤指标")
    print("="*70)

    data = create_test_data()

    report = Config(
        BasicStatistics.drawdown_relative(name='dd_rel'),
        BasicStatistics.drawdown_absolute(name='dd_abs'),
        BasicStatistics.drawdown_amount(name='dd_amt')
    ).run(data)

    print("\n回撤指标:")
    print(f"  通过: {report['pass']}")
    print(f"  详情键: {list(report['details'].keys())}")

    if report['pass']:
        details = report['details']
        print(f"\n  结果:")
        print(f"    相对回撤: {details['dd_rel']['drawdown_relative']:.4f}")
        print(f"    绝对回撤: {details['dd_abs']['drawdown_absolute']:.4f}")
        print(f"    回撤金额: {details['dd_amt']['drawdown_amount']:.2f}")

        print("\n[SUCCESS] 回撤指标测试通过 [OK]")
    else:
        print("\n[FAIL] 回撤指标测试失败 [FAIL]")

    return report


def test_volatility_and_returns():
    """测试波动率和收益率指标"""
    print("\n" + "="*70)
    print("测试 3: 波动率和收益率指标")
    print("="*70)

    data = create_test_data()

    report = Config(
        BasicStatistics.volatility_daily(name='vol_daily'),
        BasicStatistics.volatility_period(name='vol_period'),
        BasicStatistics.return_total(name='ret_total'),
        BasicStatistics.return_avg_daily(name='ret_avg'),
        BasicStatistics.return_annualized(name='ret_ann')
    ).run(data)

    print("\n波动率和收益率:")
    print(f"  通过: {report['pass']}")
    print(f"  详情键: {list(report['details'].keys())}")

    if report['pass']:
        details = report['details']
        print(f"\n  结果:")
        print(f"    日波动率: {details['vol_daily']['volatility_daily']:.6f}")
        print(f"    期间波动率: {details['vol_period']['volatility_period']:.6f}")
        print(f"    总收益率: {details['ret_total']['return_total']:.4f}")
        print(f"    平均日收益率: {details['ret_avg']['return_avg_daily']:.6f}")
        print(f"    年化收益率: {details['ret_ann']['return_annualized']:.4f}")

        print("\n[SUCCESS] 波动率和收益率测试通过 [OK]")
    else:
        print("\n[FAIL] 波动率和收益率测试失败 [FAIL]")

    return report


def test_price_statistics():
    """测试价格统计指标"""
    print("\n" + "="*70)
    print("测试 4: 价格统计指标")
    print("="*70)

    data = create_test_data()

    report = Config(
        BasicStatistics.price_average(name='price_avg'),
        BasicStatistics.price_median(name='price_med'),
        BasicStatistics.price_mode(name='price_mode'),
        BasicStatistics.price_range_stat(name='price_range'),
        BasicStatistics.price_std(name='price_std'),
        BasicStatistics.price_cv(name='price_cv')
    ).run(data)

    print("\n价格统计:")
    print(f"  通过: {report['pass']}")
    print(f"  详情键: {list(report['details'].keys())}")

    if report['pass']:
        details = report['details']
        print(f"\n  结果:")
        print(f"    平均价: {details['price_avg']['price_average']:.2f}")
        print(f"    中位数: {details['price_med']['price_median']:.2f}")
        print(f"    众数: {details['price_mode']['price_mode']:.2f}")
        print(f"    极差: {details['price_range']['price_range_stat']:.2f}")
        print(f"    标准差: {details['price_std']['price_std']:.4f}")
        print(f"    变异系数: {details['price_cv']['price_cv']:.4f}")

        print("\n[SUCCESS] 价格统计测试通过 [OK]")
    else:
        print("\n[FAIL] 价格统计测试失败 [FAIL]")

    return report


def test_trend_indicators():
    """测试趋势指标"""
    print("\n" + "="*70)
    print("测试 5: 趋势指标")
    print("="*70)

    data = create_test_data()

    report = Config(
        BasicStatistics.trend_direction(name='trend_dir'),
        BasicStatistics.trend_strength(name='trend_str')
    ).run(data)

    print("\n趋势指标:")
    print(f"  通过: {report['pass']}")
    print(f"  详情键: {list(report['details'].keys())}")

    if report['pass']:
        details = report['details']
        print(f"\n  结果:")
        print(f"    趋势方向: {details['trend_dir']['trend_direction']}")
        print(f"    趋势强度: {details['trend_str']['trend_strength']:.4f}")

        print("\n[SUCCESS] 趋势指标测试通过 [OK]")
    else:
        print("\n[FAIL] 趋势指标测试失败 [FAIL]")

    return report


def test_advanced_features():
    """测试高级特征指标"""
    print("\n" + "="*70)
    print("测试 6: 高级特征指标（躁动程度）")
    print("="*70)

    data = create_test_data()

    report = Config(
        AdvancedFeatures.agitation_level(name='agit_level'),
        AdvancedFeatures.agitation_score(name='agit_score'),
        AdvancedFeatures.cumulative_volatility(name='cum_vol')
    ).run(data)

    print("\n躁动程度:")
    print(f"  通过: {report['pass']}")
    print(f"  详情键: {list(report['details'].keys())}")

    if report['pass']:
        details = report['details']
        print(f"\n  结果:")
        print(f"    躁动程度值: {details['agit_level']['agitation_level']:.6f}")
        print(f"    躁动评分: {details['agit_score']['agitation_score']}")
        print(f"    累积波动率: {details['cum_vol']['cumulative_volatility']:.6f}")

        print("\n[SUCCESS] 躁动程度测试通过 [OK]")
    else:
        print("\n[FAIL] 躁动程度测试失败 [FAIL]")

    return report


def test_wash_trading():
    """测试洗盘识别指标"""
    print("\n" + "="*70)
    print("测试 7: 洗盘识别指标")
    print("="*70)

    data = create_test_data()

    report = Config(
        AdvancedFeatures.is_wash_trading(agitation_threshold=0.2, rules=("is_wash_trading == True or is_wash_trading == False",), name='is_wash'),
        AdvancedFeatures.wash_trading_type(agitation_threshold=0.2, name='wash_type'),
        AdvancedFeatures.wash_trading_intensity(agitation_threshold=0.2, name='wash_intensity')
    ).run(data)

    print("\n洗盘识别:")
    print(f"  通过: {report['pass']}")
    print(f"  详情键: {list(report['details'].keys())}")

    if report['pass']:
        details = report['details']
        print(f"\n  结果:")
        print(f"    是否洗盘: {details['is_wash']['is_wash_trading']}")
        print(f"    洗盘类型: {details['wash_type']['wash_trading_type']}")
        print(f"    洗盘强度: {details['wash_intensity']['wash_trading_intensity']:.6f}")

        print("\n[SUCCESS] 洗盘识别测试通过 [OK]")
    else:
        print("\n[FAIL] 洗盘识别测试失败 [FAIL]")

    return report


def test_combined_usage():
    """测试综合使用（基础+高级）"""
    print("\n" + "="*70)
    print("测试 8: 综合使用（基础指标+高级特征）")
    print("="*70)

    data = create_test_data()

    report = Chain(
        # 基础指标
        BasicStatistics.level_relative(rules=("level_relative >= 0",), name='price_level'),
        BasicStatistics.trend_direction(name='trend'),
        BasicStatistics.return_total(rules=("return_total > -0.5",), name='total_return'),

        # 高级特征
        AdvancedFeatures.agitation_level(rules=("agitation_level < 0.5",), name='agitation'),
        AdvancedFeatures.is_wash_trading(agitation_threshold=0.2, rules=("is_wash_trading == True or is_wash_trading == False",), name='is_wash')
    ).run(data)

    print("\n综合使用:")
    print(f"  通过: {report['pass']}")
    print(f"  详情键: {list(report['details'].keys())}")

    if report['pass']:
        details = report['details']
        print(f"\n  结果:")
        print(f"    价格水平: {details['price_level']['level_relative']:.2%}")
        print(f"    趋势: {details['trend']['trend_direction']}")
        print(f"    总收益率: {details['total_return']['return_total']:.2%}")
        print(f"    躁动程度: {details['agitation']['agitation_level']:.4f}")
        print(f"    是否洗盘: {details['is_wash']['is_wash_trading']}")

        print("\n[SUCCESS] 综合使用测试通过 [OK]")
    else:
        print("\n[FAIL] 综合使用测试失败 [FAIL]")

    return report


def print_summary():
    """打印测试总结"""
    print("\n" + "="*70)
    print("测试总结")
    print("="*70)

    print("\n新增因子模块:")
    print("  1. basic_statistics_factors.py - 基础统计指标（23个）")
    print("  2. advanced_features_factors.py - 高级特征指标（6个）")

    print("\n基础统计指标分类:")
    print("  - 价格水平（4个）: 相对分位、绝对分位、距离最高/最低价")
    print("  - 回撤指标（3个）: 相对回撤、绝对回撤、回撤金额")
    print("  - 波动率（2个）: 日波动率、期间波动率")
    print("  - 收益率（3个）: 总收益率、平均日收益率、年化收益率")
    print("  - 最大回撤（1个）: 最大回撤")
    print("  - 价格统计（7个）: 平均、中位数、众数、极差、方差、标准差、变异系数")
    print("  - 趋势（2个）: 趋势方向、趋势强度")

    print("\n高级特征指标分类:")
    print("  - 躁动程度（2个）: 躁动程度值、躁动评分")
    print("  - 洗盘识别（3个）: 是否洗盘、洗盘类型、洗盘强度")
    print("  - 辅助指标（1个）: 累积波动率")

    print("\n所有测试完成！ [COMPLETE]")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("新增因子功能测试套件")
    print("测试从 demo_indicators 移植的指标")
    print("="*70)

    # 运行所有测试
    test_basic_statistics()
    test_drawdown_indicators()
    test_volatility_and_returns()
    test_price_statistics()
    test_trend_indicators()
    test_advanced_features()
    test_wash_trading()
    test_combined_usage()

    # 打印总结
    print_summary()
