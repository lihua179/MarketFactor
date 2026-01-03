# -*- coding: utf-8 -*-
"""
@author: Zed
@file: Factor.py
@time: 2026/1/3 19:04
@describe:自定义描述
"""
from typing import Callable, Tuple, Dict, Any, List

Rule = str
Rules = Tuple[Rule, ...]
FactorConf = Tuple[Callable[[Dict[str, List], Any], Dict[str, Any]], Dict[str, Any], Rules]
def _daily_vol(data: Dict[str, List], n: int = 30,*params,**kwargs) -> Dict[str, float]:
    high, low, yd_close = data['high'][-n:], data['low'][-n:], data['yd_close'][-n:]
    vols = [(h - l) / yc for h, l, yc in zip(high, low, yd_close) if yc]
    return {"daily_vol": sum(vols) / len(vols) if vols else 0.0}

def _price_level(data: Dict[str, List], n: int = 30,*params,**kwargs) -> Dict[str, float]:

    high = max(data['high'][-n:])
    low = min(data['low'][-n:])
    close = data['close'][-1]
    return {"price_level": (close - low) / (high - low)}
# ---------- 1. 因子命名空间 ----------
class Factor:

    # 配置工厂
    @staticmethod
    def price_level(n: int = 30,rules: Rules = ("price_level > 0",)) -> FactorConf:
        return _price_level, {"n": n}, rules

    @staticmethod
    def daily_vol(n: int = 30, rules: Rules = ("daily_vol < 0.05",)) -> FactorConf:
        return _daily_vol, {"n": n}, rules