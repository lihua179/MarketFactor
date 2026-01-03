# -*- coding: utf-8 -*-
"""
简单测试 - 验证StockFilter框架和新指标
"""
from stock_market_api import get_history, get_symbols
from stock_filter import Config
from indicators import Factor


def test_single_stock():
    """测试单个股票"""
    print("=" * 100)
    print("测试单个股票: 000001.SZ")
    print("=" * 100)

    symbol = "000001.SZ"

    try:
        # 获取数据
        data = get_history(symbol, limit=60)
        print(f"\n获取数据成功: {symbol}")
        print(f"数据长度: {len(data.get('close', []))} 条")

        # 测试1: 均线
        print("\n--- 测试1: 均线 ---")
        config1 = Config(
            Factor.ma(n=5, rules=("ma > -2",)),
            Factor.ma(n=20, rules=("ma > 0",)),
        )
        result1 = config1.run(data)
        print(f"通过: {result1['pass']}")
        if result1['pass']:
            print(f"MA5: {result1['details']}")
            print(f"MA20: {result1['details']}")

        # 测试2: 涨跌幅
        print("\n--- 测试2: 涨跌幅 ---")
        config2 = Config(
            Factor.return_rate(n=5, rules=("return_rate > -0.1",)),
            Factor.return_rate(n=20, rules=("return_rate > -0.3",)),
            Factor.return_rate(n=30, rules=("return_rate > -0.3",)),
        )
        result2 = config2.run(data)
        print(f"通过: {result2['pass']}")
        print("result2['details']",result2['details'])
        if result2['pass']:
            print(f"5日涨跌幅: {result2['details']}")
            print(f"20日涨跌幅: {result2['details']['return_rate1']['return_rate']:.2%}")

        # 测试3: 波动率
        print("\n--- 测试3: 波动率 ---")
        config3 = Config(
            Factor.volatility(n=20, rules=("volatility < 1.0",)),
        )
        result3 = config3.run(data)
        print(f"通过: {result3['pass']}")
        if result3['pass']:
            print(f"20日波动率: {result3['details']['volatility']['volatility']:.4f}")

        # 测试4: RSI
        print("\n--- 测试4: RSI ---")
        config4 = Config(
            Factor.rsi(n=14, rules=("0 <= rsi <= 100",)),
        )
        result4 = config4.run(data)
        print(f"通过: {result4['pass']}")
        if result4['pass']:
            print(f"RSI: {result4['details']['rsi']['rsi']:.2f}")

        # # 测试5: 多因子组合
        print("\n--- 测试5: 多因子组合 ---")
        config5 = Config(
            # Factor.return_rate(n=20, rules=("return_rate > -0.1",)),
            Factor.volatility(n=20, rules=("volatility < 0.5",)),
            Factor.rsi(n=14, rules=("30 <= rsi <= 70",)),
        )
        result5 = config5.run(data)
        # print(f"通过: {result5['pass']}")
        # print('now ',result5)
        # if result5['pass']:
        #     print(f"20日涨跌幅: {result5['details']['return_rate']['return_rate']:.2%}")
        #     print(f"20日波动率: {result5['details']['volatility']['volatility']:.4f}")
        #     print(f"RSI: {result5['details']['rsi']['rsi']:.2f}")

        print("\n" + "=" * 100)
        print("测试完成!")
        print("=" * 100)

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


def test_multiple_stocks():
    """测试多个股票"""
    print("\n" + "=" * 100)
    print("测试多个股票")
    print("=" * 100)

    try:
        symbols = get_symbols()
        print(f"\n获取到 {len(symbols)} 只股票")

        # 测试前5只股票
        test_symbols = symbols[:5]
        passed_count = 0

        for symbol in test_symbols:
            try:
                data = get_history(symbol, limit=60)

                config = Config(
                    Factor.return_rate(n=20, rules=("return_rate > 0",)),  # 20日上涨
                    Factor.volatility(n=20, rules=("volatility < 0.5",)),  # 波动率<50%
                    Factor.rsi(n=14, rules=("rsi < 70",)),  # RSI不超买
                )

                result = config.run(data)

                if result['pass']:
                    passed_count += 1
                    print(f"[通过] {symbol}")
                else:
                    print(f"[未通过] {symbol}")

            except Exception as e:
                print(f"[错误] {symbol}: {str(e)}")

        print(f"\n通过率: {passed_count}/{len(test_symbols)} ({passed_count/len(test_symbols)*100:.1f}%)")
        print("=" * 100)

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    # 测试单个股票
    test_single_stock()

    # 测试多个股票
    test_multiple_stocks()
