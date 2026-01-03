# -*- coding: utf-8 -*-
"""
零状态、纯函数、IDE 自动补全的
“单股票因子链式过滤”完整示例
（不含行情获取，仅留接口）
"""
import time
from typing import Callable, Tuple, Dict, Any, List, Optional
from factor import Factor
from collections import Counter
import re
Rule = str
Rules = Tuple[Rule, ...]
FactorConf = Tuple[Callable[[Dict[str, List], Any], Dict[str, Any]], Dict[str, Any], Rules, Optional[str]]


# ---------- 0. 工具 ----------
def pass_filter(result: Dict[str, Any], rules: Rules) -> bool:
    # print('pass_filter',result,rules)
    return all(eval(rule, {}, result) for rule in rules)


# ---------- 2. 单股票链 ----------
def run_one(data: Dict[str, List], chain: List[FactorConf]) -> Dict[str, Any]:
    details, ok = {}, True
    func_count = {}  # 记录每个函数被调用的次数

    for item in chain:
        # 解包 FactorConf,支持4元组或3元组(向后兼容)
        if len(item) == 4:
            func, params, rules, custom_name = item
        else:
            func, params, rules = item
            custom_name = None

        params['detail'] = details
        res = func(data, **params)
        if not pass_filter(res, rules):
            ok = False
            break

        # 获取函数名(去掉下划线前缀)
        func_name = func.__name__[1:] if func.__name__.startswith('_') else func.__name__

        # 优先使用自定义名称
        if custom_name is not None:
            # 使用自定义名称
            key = custom_name
        else:
            # 没有自定义名称,使用自动序号逻辑
            # 统计调用次数（只统计没有自定义名称的调用）
            func_count[func_name] = func_count.get(func_name, 0) + 1
            count = func_count[func_name]

            # 生成唯一键名:
            # - 只调用1次: 不加后缀 (func)
            # - 重复调用: 从第1次开始就加序号 (func1, func2, func3...)
            if count == 1:
                # 第1次调用,先不加后缀
                key = func_name
            else:
                # 第2次及以后调用: 说明是重复调用,所有调用(包括第1次)都要加序号
                # 但因为第1次已经保存了,所以这里只需要改当前的键名
                # 并且要修改之前保存的第1次的键名
                if count == 2:
                    # 第2次调用时,发现是重复调用,需要修改第1次的键名
                    old_key = func_name
                    new_key = f"{func_name}1"
                    if old_key in details:
                        details[new_key] = details.pop(old_key)

                # 当前调用加序号
                key = f"{func_name}{count}"

        details[key] = res

    return {"pass": ok, "details": details}


# ---------- 3. 配置 DSL ----------
class Config:
    def __init__(self, *confs: FactorConf):
        # 组装时自动去重命名
        self.chain = list(confs)

    def run(self, data: Dict[str, List]) -> Dict[str, Any]:
        return run_one(data, self.chain)


# ---------- 4. 使用 ----------
if __name__ == "__main__":
    from stock_market_api import get_symbols, get_history

    symbol_list = get_symbols()
    symbol_list=symbol_list[:1]
    for symbol in symbol_list:
        data = get_history(symbol)
        # report = Config(
        #     Factor.price_level(n=20, rules=("price_level > 0.1",)),
        #     Factor.price_level(n=30, rules=("price_level > 0.1",)),
        #     Factor.price_level(n=30, rules=("price_level > 0.1",)),
        #     Factor.daily_vol(n=30, rules=("daily_vol < 0.05",)),
        #     Factor.daily_vol(n=30, rules=("daily_vol < 0.05",))
        # ).run(data)
        # print(report)
        report = Config(
            Factor.price_level(n=30),
            Factor.daily_vol(n=30, rules=("daily_vol < 1.15",),name='daily_vol101')
        ).run(data)
        print(report)
        # report = Config(
        #     Factor.price_level(n=30, rules=("price_level > 0.1",)),
        #     Factor.price_level(n=20, rules=("price_level > 0.15",)),
        #     Factor.daily_vol(n=30, rules=("daily_vol < 0.05",))
        # ).run(data)
        #
        # print(report)
