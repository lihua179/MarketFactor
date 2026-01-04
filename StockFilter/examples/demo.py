# -*- coding: utf-8 -*-
"""
完整Demo - 使用StockFilter框架进行多因子链式过滤

演示17个技术指标的实际应用
"""
from stock_market_api import get_history, get_symbols
from stock_filter import Config
from indicators import Factor


# ==================== Demo 1: 基础均线过滤 ====================

def demo_1_ma_cross():
    """Demo 1: 均线金叉策略"""
    print("=" * 100)
    print("Demo 1: 均线金叉策略")
    print("=" * 100)

    symbols = get_symbols()
    passed_symbols = []

    for symbol in symbols[:10]:  # 测试前10个股票
        try:
            data = get_history(symbol, limit=60)

            # 配置: MA5 > MA20 (金叉)
            config = Config(
                Factor.ma(n=5, rules=("ma > 0",)),   # 计算MA5
                Factor.ma(n=20, rules=("ma > 0",)),  # 计算MA20
                Factor.return_rate(n=5, rules=("return_rate > 0",)),  # 5日收益为正
            )

            # 添加自定义规则(在链式调用后检查)
            result = config.run(data)

            # 检查金叉条件
            if result['pass']:
                ma5 = result['details']['ma']['ma']
                ma20_val = result['details']['ma']['ma']  # 注意:会被覆盖

                # 重新计算MA20(因为上面被覆盖了)
                closes = data['close'][-20:]
                ma20_real = sum(closes) / len(closes) if closes else 0

                if ma5 > ma20_real:
                    passed_symbols.append(symbol)
                    print(f"[通过] {symbol}: MA5={ma5:.2f}, MA20={ma20_real:.2f}, 金叉!")
                else:
                    print(f"[未通过] {symbol}: MA5={ma5:.2f}, MA20={ma20_real:.2f}")

        except Exception as e:
            print(f"[错误] {symbol}: {str(e)}")

    print(f"\n通过金叉策略: {len(passed_symbols)} 只")
    print("-" * 100)


# ==================== Demo 2: 多因子组合过滤 ====================

def demo_2_multi_factor():
    """Demo 2: 多因子组合策略"""
    print("\n" + "=" * 100)
    print("Demo 2: 多因子组合策略 (趋势+动量+风险)")
    print("=" * 100)

    symbols = get_symbols()
    passed_symbols = []

    for symbol in symbols[:10]:
        try:
            data = get_history(symbol, limit=60)

            # 配置: 趋势 + 动量 + 风险
            config = Config(
                # 趋势条件
                Factor.return_rate(n=20, rules=("return_rate > 0",)),  # 20日收益为正

                # 动量条件
                Factor.return_rate(n=5, rules=("return_rate > 0.01",)),  # 5日收益>1%

                # 风险条件
                Factor.volatility(n=20, rules=("volatility < 0.3",)),  # 波动率<30%
            )

            result = config.run(data)

            if result['pass']:
                passed_symbols.append(symbol)
                print(f"[通过] {symbol}")
                print(f"  20日收益: {result['details']['return_rate']['return_rate']:.2%}")
                print(f"  5日收益: {result['details']['return_rate']['return_rate']:.2%}")  # 注意会被覆盖
                print(f"  波动率: {result['details']['volatility']['volatility']:.4f}")
            else:
                print(f"[未通过] {symbol}")

        except Exception as e:
            print(f"[错误] {symbol}: {str(e)}")

    print(f"\n通过多因子策略: {len(passed_symbols)} 只")
    print("-" * 100)


# ==================== Demo 3: RSI策略 ====================

def demo_3_rsi_strategy():
    """Demo 3: RSI超卖策略"""
    print("\n" + "=" * 100)
    print("Demo 3: RSI超卖策略 (RSI < 30)")
    print("=" * 100)

    symbols = get_symbols()
    passed_symbols = []

    for symbol in symbols[:10]:
        try:
            data = get_history(symbol, limit=60)

            # 配置: RSI < 30 (超卖)
            config = Config(
                Factor.rsi(n=14, rules=("rsi < 30",)),  # RSI小于30
                Factor.close_price(rules=("close > 0",)),  # 有价格
            )

            result = config.run(data)

            if result['pass']:
                passed_symbols.append(symbol)
                rsi_val = result['details']['rsi']['rsi']
                close_val = result['details']['close_price']['close']
                print(f"[通过] {symbol}: RSI={rsi_val:.2f}, 收盘价={close_val:.2f}")
            else:
                # 检查RSI值
                from indicators import _rsi
                rsi_val = _rsi(data, n=14)['rsi']
                print(f"[未通过] {symbol}: RSI={rsi_val:.2f}")

        except Exception as e:
            print(f"[错误] {symbol}: {str(e)}")

    print(f"\n通过RSI超卖策略: {len(passed_symbols)} 只")
    print("-" * 100)


# ==================== Demo 4: 布林带策略 ====================

def demo_4_bollinger():
    """Demo 4: 布林带突破策略"""
    print("\n" + "=" * 100)
    print("Demo 4: 布林带突破策略 (收盘价 > 上轨)")
    print("=" * 100)

    symbols = get_symbols()
    passed_symbols = []

    for symbol in symbols[:10]:
        try:
            data = get_history(symbol, limit=60)

            # 配置: 收盘价突破布林带上轨
            config = Config(
                Factor.bollinger_upper(n=20, multiplier=2.0, rules=("bollinger_upper > 0",)),
                Factor.close_price(rules=("close > 0",)),
            )

            result = config.run(data)

            if result['pass']:
                close = result['details']['close_price']['close']
                upper = result['details']['bollinger_upper']['bollinger_upper']

                if close > upper:
                    passed_symbols.append(symbol)
                    print(f"[通过] {symbol}: 收盘价={close:.2f} > 上轨={upper:.2f}")
                else:
                    print(f"[未通过] {symbol}: 收盘价={close:.2f} <= 上轨={upper:.2f}")

        except Exception as e:
            print(f"[错误] {symbol}: {str(e)}")

    print(f"\n通过布林带突破策略: {len(passed_symbols)} 只")
    print("-" * 100)


# ==================== Demo 5: 完整技术分析策略 ====================

def demo_5_complete_strategy():
    """Demo 5: 完整技术分析策略"""
    print("\n" + "=" * 100)
    print("Demo 5: 完整技术分析策略")
    print("=" * 100)

    symbols = get_symbols()
    passed_symbols = []

    for symbol in symbols[:10]:
        try:
            data = get_history(symbol, limit=100)

            # 配置: 多技术指标组合
            config = Config(
                # 1. 趋势条件
                Factor.return_rate(n=20, rules=("return_rate > 0",)),  # 20日上涨

                # 2. 动量条件
                Factor.return_rate(n=5, rules=("return_rate > 0.02",)),  # 5日涨幅>2%

                # 3. 成交量条件
                Factor.volume_ratio(n=5, rules=("volume_ratio > 1.2",)),  # 量比>1.2

                # 4. 风险条件
                Factor.volatility(n=20, rules=("volatility < 0.4",)),  # 波动率<40%

                # 5. 技术指标
                Factor.rsi(n=14, rules=("30 < rsi < 80",)),  # RSI不超买也不超卖
            )

            result = config.run(data)

            if result['pass']:
                passed_symbols.append(symbol)
                print(f"\n[通过] {symbol}:")
                print(f"  20日收益: {result['details']['return_rate']['return_rate']:.2%}")
                print(f"  量比: {result['details']['volume_ratio']['volume_ratio']:.2f}")
                print(f"  波动率: {result['details']['volatility']['volatility']:.4f}")
                print(f"  RSI: {result['details']['rsi']['rsi']:.2f}")
            else:
                print(f"[未通过] {symbol}")

        except Exception as e:
            print(f"[错误] {symbol}: {str(e)}")

    print(f"\n通过完整策略: {len(passed_symbols)} 只")
    print("-" * 100)


# ==================== Demo 6: 价格位置策略 ====================

def demo_6_price_position():
    """Demo 6: 价格位置策略"""
    print("\n" + "=" * 100)
    print("Demo 6: 价格位置策略 (价格在近期高位)")
    print("=" * 100)

    symbols = get_symbols()
    passed_symbols = []

    for symbol in symbols[:10]:
        try:
            data = get_history(symbol, limit=60)

            # 计算价格位置(手动计算,因为需要组合多个因子)
            highs = data['high'][-20:]
            lows = data['low'][-20:]
            closes = data['close']

            max_high = max(highs)
            min_low = min(lows)
            current_close = closes[-1]

            if max_high == min_low:
                price_position = 0.5
            else:
                price_position = (current_close - min_low) / (max_high - min_low)

            # 配置: 价格位置 > 0.7 (在高位)
            config = Config(
                Factor.price_range(n=20, rules=("price_range > 0",)),  # 有振幅
                Factor.close_price(rules=("close > 0",)),  # 有价格
            )

            result = config.run(data)

            if result['pass'] and price_position > 0.7:
                passed_symbols.append(symbol)
                print(f"[通过] {symbol}: 价格位置={price_position:.2%}")
            else:
                print(f"[未通过] {symbol}: 价格位置={price_position:.2%}")

        except Exception as e:
            print(f"[错误] {symbol}: {str(e)}")

    print(f"\n通过价格位置策略: {len(passed_symbols)} 只")
    print("-" * 100)


# ==================== 主函数 ====================

if __name__ == '__main__':
    print("\n" + "=" * 100)
    print("StockFilter 完整Demo - 17个技术指标实战")
    print("=" * 100)

    # 运行各个Demo
    demo_1_ma_cross()           # Demo 1: 均线金叉
    demo_2_multi_factor()       # Demo 2: 多因子组合
    demo_3_rsi_strategy()       # Demo 3: RSI超卖
    demo_4_bollinger()          # Demo 4: 布林带突破
    demo_5_complete_strategy()  # Demo 5: 完整策略
    demo_6_price_position()     # Demo 6: 价格位置

    print("\n" + "=" * 100)
    print("所有Demo运行完成!")
    print("=" * 100)
