# -*- coding: utf-8 -*-
"""
调试脚本 - 查看因子实际值
"""
from stock_filter import Config
from indicators import Factor as IndicatorsFactor
from factor import Factor as FactorFactor

class Factor(IndicatorsFactor):
    price_level = FactorFactor.price_level
    daily_vol = FactorFactor.daily_vol


def create_test_data():
    """创建测试数据"""
    return {
        'open': [10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.5, 14.0, 14.5,
                 15.0, 15.5, 16.0, 16.5, 17.0, 17.5, 18.0, 18.5, 19.0, 19.5,
                 20.0, 20.5, 21.0, 21.5, 22.0, 22.5, 23.0, 23.5, 24.0, 24.5],
        'high': [10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.5, 14.0, 14.5, 15.0,
                 15.5, 16.0, 16.5, 17.0, 17.5, 18.0, 18.5, 19.0, 19.5, 20.0,
                 20.5, 21.0, 21.5, 22.0, 22.5, 23.0, 23.5, 24.0, 24.5, 25.0],
        'low': [9.5, 10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.5, 14.0,
                14.5, 15.0, 15.5, 16.0, 16.5, 17.0, 17.5, 18.0, 18.5, 19.0,
                19.5, 20.0, 20.5, 21.0, 21.5, 22.0, 22.5, 23.0, 23.5, 24.0],
        'close': [10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.5, 14.0, 14.5,
                  15.0, 15.5, 16.0, 16.5, 17.0, 17.5, 18.0, 18.5, 19.0, 19.5,
                  20.0, 20.5, 21.0, 21.5, 22.0, 22.5, 23.0, 23.5, 24.0, 24.5],
        'volume': [10000, 11000, 12000, 13000, 14000, 15000, 16000, 17000, 18000, 19000,
                   20000, 21000, 22000, 23000, 24000, 25000, 26000, 27000, 28000, 29000,
                   30000, 31000, 32000, 33000, 34000, 35000, 36000, 37000, 38000, 39000],
        'yd_close': [9.5, 10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.5, 14.0,
                     14.5, 15.0, 15.5, 16.0, 16.5, 17.0, 17.5, 18.0, 18.5, 19.0,
                     19.5, 20.0, 20.5, 21.0, 21.5, 22.0, 22.5, 23.0, 23.5, 24.0]
    }


data = create_test_data()

# 测试 RSI
report = Config(
    Factor.rsi(n=14, rules=("rsi > 0",))
).run(data)

print("RSI 测试:")
print(f"  通过: {report['pass']}")
print(f"  详情: {report['details']}")

# 测试 volatility
report = Config(
    Factor.volatility(n=20, rules=("volatility > 0",))
).run(data)

print("\nVolatility 测试:")
print(f"  通过: {report['pass']}")
print(f"  详情: {report['details']}")

# 测试多个 ma
report = Config(
    Factor.ma(n=5, rules=("ma > 0",)),
    Factor.ma(n=20, rules=("ma > 0",))
).run(data)

print("\n多个 MA 测试:")
print(f"  通过: {report['pass']}")
print(f"  详情键: {list(report['details'].keys())}")
print(f"  详情: {report['details']}")
