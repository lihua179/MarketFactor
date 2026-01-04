# -*- coding: utf-8 -*-
"""
基础统计指标因子 - 基于 StockFilter 框架

基于 stock_statistics.py 的实现公式，为 StockFilter 系统提供基础统计指标

特性：
1. 支持参数化配置（如 n=20, period=30 等）
2. 当返回结果唯一时，统一使用 'res' 作为 key
3. 便于规则编写：rules=("res > 0.5",) 而不用 ("level_relative > 0.5",)
"""
from typing import Dict, List, Tuple, Any, Optional
import math

Rule = str
Rules = Tuple[Rule, ...]
FactorConf = Tuple[callable, Dict[str, Any], Rules, Optional[str]]


# ==================== 价格水平指标 ====================

def _level_relative(data: Dict[str, List], n: int = None, **kwargs) -> Dict[str, float]:
    """
    当前价格水平位相对（相对分位）
    计算：(当前-最低)/(最高-最低)
    范围：[0, 1]，0表示在最低位，1表示在最高位

    参数:
        n: 统计周期（None表示使用全部数据）
    """
    if n is None:
        n = len(data['close'])

    current = data['close'][-1]
    high = max(data['high'][-n:])
    low = min(data['low'][-n:])

    if high == low:
        return {"res": 0.5}

    return {"res": (current - low) / (high - low)}


def _level_absolute(data: Dict[str, List], n: int = None, **kwargs) -> Dict[str, float]:
    """
    当前价格水平位绝对（绝对分位）
    计算：当前/最高
    范围：(0, 1]，接近1表示越接近历史最高

    参数:
        n: 统计周期（None表示使用全部数据）
    """
    if n is None:
        n = len(data['close'])

    current = data['close'][-1]
    high = max(data['high'][-n:])

    if high == 0:
        return {"res": 0.0}

    return {"res": current / high}


def _distance_to_highest_pct(data: Dict[str, List], n: int = None, **kwargs) -> Dict[str, float]:
    """
    距离最高价的百分比距离
    计算：(最高-当前)/最高 * 100%

    参数:
        n: 统计周期（None表示使用全部数据）
    """
    if n is None:
        n = len(data['close'])

    current = data['close'][-1]
    high = max(data['high'][-n:])

    if high == 0:
        return {"res": 0.0}

    return {"res": (high - current) / high * 100}


def _distance_to_lowest_pct(data: Dict[str, List], n: int = None, **kwargs) -> Dict[str, float]:
    """
    距离最低价的百分比距离
    计算：(当前-最低)/最低 * 100%

    参数:
        n: 统计周期（None表示使用全部数据）
    """
    if n is None:
        n = len(data['close'])

    current = data['close'][-1]
    low = min(data['low'][-n:])

    if low == 0:
        return {"res": 0.0}

    return {"res": (current - low) / low * 100}


# ==================== 回撤指标 ====================

def _drawdown_relative(data: Dict[str, List], n: int = None, **kwargs) -> Dict[str, float]:
    """
    相对回撤（从最高点的回撤幅度）
    计算：1 - 相对分位 = 1 - (当前-最低)/(最高-最低)
    范围：[0, 1]，0表示无回撤（在最高位），1表示最大回撤（在最低位）

    参数:
        n: 统计周期（None表示使用全部数据）
    """
    result = _level_relative(data, n)
    level_relative = result['res']
    return {"res": 1.0 - level_relative}


def _drawdown_absolute(data: Dict[str, List], n: int = None, **kwargs) -> Dict[str, float]:
    """
    绝对回撤（从最高点的回撤幅度）
    计算：1 - 绝对分位 = 1 - 当前/最高
    范围：[0, 1)，0表示无回撤（当前=最高）

    参数:
        n: 统计周期（None表示使用全部数据）
    """
    result = _level_absolute(data, n)
    level_absolute = result['res']
    return {"res": 1.0 - level_absolute}


def _drawdown_amount(data: Dict[str, List], n: int = None, **kwargs) -> Dict[str, float]:
    """
    回撤金额
    计算：最高价 - 当前价

    参数:
        n: 统计周期（None表示使用全部数据）
    """
    if n is None:
        n = len(data['close'])

    current = data['close'][-1]
    high = max(data['high'][-n:])
    return {"res": high - current}


# ==================== 波动率指标 ====================

def _volatility_daily(data: Dict[str, List], n: int = None, **kwargs) -> Dict[str, float]:
    """
    日波动率（日内振幅的平均值）
    计算：每天[(最高价 - 最低价) / 昨收价] 的平均值

    参数:
        n: 统计周期（None表示使用全部数据）
    """
    high_list = data['high'][-n:] if n else data['high']
    low_list = data['low'][-n:] if n else data['low']
    yd_close_list = data.get('yd_close', [])[-n:] if n else data.get('yd_close', [])

    if not high_list or not low_list or not yd_close_list:
        return {"res": 0.0}

    min_len = min(len(high_list), len(low_list), len(yd_close_list))
    if min_len == 0:
        return {"res": 0.0}

    daily_volatilities = []
    for i in range(min_len):
        if yd_close_list[i] > 0:
            vol = (high_list[i] - low_list[i]) / yd_close_list[i]
            daily_volatilities.append(vol)

    if not daily_volatilities:
        return {"res": 0.0}

    return {"res": sum(daily_volatilities) / len(daily_volatilities)}


def _volatility_period(data: Dict[str, List], n: int = None, **kwargs) -> Dict[str, float]:
    """
    期间波动率
    计算：(期间最高价 - 期间最低价) / 期间开盘价
    反映整个统计期间的价格波动幅度

    参数:
        n: 统计周期（None表示使用全部数据）
    """
    if n is None:
        n = len(data['close'])

    high_list = data['high'][-n:]
    low_list = data['low'][-n:]
    open_list = data['open'][-n:]

    if not high_list or not low_list or not open_list:
        return {"res": 0.0}

    highest = max(high_list)
    lowest = min(low_list)
    start_price = open_list[0]

    if start_price == 0:
        return {"res": 0.0}

    return {"res": (highest - lowest) / start_price}


# ==================== 收益率指标 ====================

def _return_total(data: Dict[str, List], n: int = None, **kwargs) -> Dict[str, float]:
    """
    期间总收益率
    计算：(期末价 - 期初价) / 期初价

    参数:
        n: 统计周期（None表示使用全部数据）
    """
    if n is None:
        n = len(data['close'])

    close_list = data['close'][-n:]

    if len(close_list) < 2:
        return {"res": 0.0}

    start_price = close_list[0]
    end_price = close_list[-1]

    if start_price == 0:
        return {"res": 0.0}

    return {"res": (end_price - start_price) / start_price}


def _return_avg_daily(data: Dict[str, List], n: int = None, **kwargs) -> Dict[str, float]:
    """
    期间平均日收益率
    计算：每天[(收盘价 - 昨收价) / 昨收价] 的平均值

    参数:
        n: 统计周期（None表示使用全部数据）
    """
    if n is None:
        n = len(data['close'])

    close_list = data['close'][-n:] if n else data['close']
    yd_close_list = data.get('yd_close', [])[-n:] if n else data.get('yd_close', [])

    if not close_list or not yd_close_list:
        # 简化计算
        if len(close_list) < 2:
            return {"res": 0.0}
        result = _return_total(data, n)
        total_return = result['res']
        days = len(close_list) - 1
        return {"res": total_return / days if days > 0 else 0.0}

    min_len = min(len(close_list), len(yd_close_list))
    if min_len == 0:
        return {"res": 0.0}

    daily_returns = []
    for i in range(min_len):
        if yd_close_list[i] > 0:
            ret = (close_list[i] - yd_close_list[i]) / yd_close_list[i]
            daily_returns.append(ret)

    if not daily_returns:
        return {"res": 0.0}

    return {"res": sum(daily_returns) / len(daily_returns)}


def _return_annualized(data: Dict[str, List], n: int = None, **kwargs) -> Dict[str, float]:
    """
    年化收益率
    使用复利计算：(1 + 总收益率)^(252/交易日数) - 1

    参数:
        n: 统计周期（None表示使用全部数据）
    """
    if n is None:
        n = len(data['close'])

    close_list = data['close'][-n:]

    if len(close_list) < 2:
        return {"res": 0.0}

    result = _return_total(data, n)
    total_return = result['res']
    days = len(close_list) - 1

    if days == 0:
        return {"res": 0.0}

    annualized = (1 + total_return) ** (252 / days) - 1
    return {"res": annualized}


# ==================== 最大回撤 ====================

def _max_drawdown(data: Dict[str, List], n: int = None, **kwargs) -> Dict[str, float]:
    """
    最大回撤（期间内最大回撤）
    从价格序列中计算最大回撤

    参数:
        n: 统计周期（None表示使用全部数据）
    """
    if n is None:
        n = len(data['close'])

    close_list = data['close'][-n:]

    if len(close_list) < 2:
        return {"res": 0.0}

    max_price = close_list[0]
    max_dd = 0.0

    for price in close_list:
        if price > max_price:
            max_price = price

        drawdown = (max_price - price) / max_price if max_price > 0 else 0
        if drawdown > max_dd:
            max_dd = drawdown

    return {"res": max_dd}


# ==================== 价格统计指标 ====================

def _price_average(data: Dict[str, List], n: int = None, **kwargs) -> Dict[str, float]:
    """
    平均价格（算术平均）
    计算：价格序列的算术平均值

    参数:
        n: 统计周期（None表示使用全部数据）
    """
    if n is None:
        n = len(data['close'])

    close_list = data['close'][-n:]

    if not close_list:
        return {"res": 0.0}

    return {"res": sum(close_list) / len(close_list)}


def _price_median(data: Dict[str, List], n: int = None, **kwargs) -> Dict[str, float]:
    """
    中位数价格
    计算：价格序列的中位数

    参数:
        n: 统计周期（None表示使用全部数据）
    """
    if n is None:
        n = len(data['close'])

    close_list = data['close'][-n:]

    if not close_list:
        return {"res": 0.0}

    sorted_prices = sorted(close_list)
    n_len = len(sorted_prices)

    if n_len % 2 == 0:
        median = (sorted_prices[n_len//2 - 1] + sorted_prices[n_len//2]) / 2
    else:
        median = sorted_prices[n_len//2]

    return {"res": median}


def _price_mode(data: Dict[str, List], n: int = None, **kwargs) -> Dict[str, float]:
    """
    众数价格（出现最频繁的价格）
    计算：价格序列中出现次数最多的价格（保留2位小数后统计）

    参数:
        n: 统计周期（None表示使用全部数据）
    """
    if n is None:
        n = len(data['close'])

    close_list = data['close'][-n:]

    if not close_list:
        return {"res": 0.0}

    from collections import Counter
    rounded_prices = [round(p, 2) for p in close_list]
    counter = Counter(rounded_prices)

    if not counter:
        return {"res": 0.0}

    return {"res": counter.most_common(1)[0][0]}


def _price_range_stat(data: Dict[str, List], n: int = None, **kwargs) -> Dict[str, float]:
    """
    价格极差
    计算：最高价 - 最低价

    参数:
        n: 统计周期（None表示使用全部数据）
    """
    if n is None:
        n = len(data['close'])

    high_list = data['high'][-n:]
    low_list = data['low'][-n:]

    if not high_list or not low_list:
        return {"res": 0.0}

    return {"res": max(high_list) - min(low_list)}


def _price_variance(data: Dict[str, List], n: int = None, **kwargs) -> Dict[str, float]:
    """
    价格方差
    计算：价格偏离平均值的程度

    参数:
        n: 统计周期（None表示使用全部数据）
    """
    if n is None:
        n = len(data['close'])

    close_list = data['close'][-n:]

    if not close_list:
        return {"res": 0.0}

    avg = sum(close_list) / len(close_list)
    variance = sum((p - avg) ** 2 for p in close_list) / len(close_list)

    return {"res": variance}


def _price_std(data: Dict[str, List], n: int = None, **kwargs) -> Dict[str, float]:
    """
    价格标准差
    计算：方差的平方根

    参数:
        n: 统计周期（None表示使用全部数据）
    """
    result = _price_variance(data, n)
    variance = result['res']
    return {"res": math.sqrt(variance) if variance > 0 else 0.0}


def _price_cv(data: Dict[str, List], n: int = None, **kwargs) -> Dict[str, float]:
    """
    价格变异系数
    计算：标准差 / 平均值
    衡量价格的相对波动性

    参数:
        n: 统计周期（None表示使用全部数据）
    """
    avg_result = _price_average(data, n)
    std_result = _price_std(data, n)

    avg = avg_result['res']
    std = std_result['res']

    if avg == 0:
        return {"res": 0.0}

    return {"res": std / avg}


# ==================== 趋势判断指标 ====================

def _trend_direction(data: Dict[str, List], segments: int = 3, **kwargs) -> Dict[str, str]:
    """
    趋势方向（上涨/下跌/震荡）
    计算：将数据分为多段，分别计算每段的平均价格
    判断规则：
    - 三段平均价都上涨 → 上涨趋势
    - 三段平均价都下跌 → 下跌趋势
    - 其他组合 → 震荡趋势

    参数:
        segments: 分段数量（默认3段）
    """
    close_list = data['close']

    if len(close_list) < segments * 2:
        return {"res": "数据不足"}

    n = len(close_list)
    segment_size = n // segments

    # 计算每段的平均价格
    segment_avgs = []
    for i in range(segments):
        start_idx = i * segment_size
        end_idx = (i + 1) * segment_size if i < segments - 1 else n
        segment = close_list[start_idx:end_idx]
        avg = sum(segment) / len(segment)
        segment_avgs.append(avg)

    # 判断趋势
    if all(segment_avgs[i] < segment_avgs[i+1] for i in range(len(segment_avgs)-1)):
        return {"res": "上涨"}
    elif all(segment_avgs[i] > segment_avgs[i+1] for i in range(len(segment_avgs)-1)):
        return {"res": "下跌"}
    else:
        return {"res": "震荡"}


def _trend_strength(data: Dict[str, List], segments: int = 3, **kwargs) -> Dict[str, float]:
    """
    趋势强度
    计算：第一段到最后段的价格变化幅度
    正值表示上涨强度，负值表示下跌强度，绝对值越大趋势越强

    参数:
        segments: 分段数量（默认3段）
    """
    close_list = data['close']

    if len(close_list) < segments * 2:
        return {"res": 0.0}

    n = len(close_list)
    segment_size = n // segments

    # 第一段
    segment1 = close_list[:segment_size]
    avg1 = sum(segment1) / len(segment1)

    # 最后一段
    last_segment = close_list[segment_size * (segments - 1):]
    avg_last = sum(last_segment) / len(last_segment)

    if avg1 == 0:
        return {"res": 0.0}

    return {"res": (avg_last - avg1) / avg1}


# ==================== 因子配置工厂 ====================

class BasicStatistics:
    """
    基础统计指标配置工厂类

    所有因子都支持：
    1. 参数化配置（n, segments 等）
    2. 自定义名称（name 参数）
    3. 统一的结果键名 'res'（便于规则编写）
    """

    # ========== 价格水平 ==========
    @staticmethod
    def level_relative(n: int = None, rules: Rules = ("0 <= res <= 1",), name: Optional[str] = None) -> FactorConf:
        """相对分位"""
        return _level_relative, {"n": n}, rules, name

    @staticmethod
    def level_absolute(n: int = None, rules: Rules = ("0 < res <= 1",), name: Optional[str] = None) -> FactorConf:
        """绝对分位"""
        return _level_absolute, {"n": n}, rules, name

    @staticmethod
    def distance_to_highest_pct(n: int = None, rules: Rules = ("res >= 0",), name: Optional[str] = None) -> FactorConf:
        """距离最高价百分比"""
        return _distance_to_highest_pct, {"n": n}, rules, name

    @staticmethod
    def distance_to_lowest_pct(n: int = None, rules: Rules = ("res >= 0",), name: Optional[str] = None) -> FactorConf:
        """距离最低价百分比"""
        return _distance_to_lowest_pct, {"n": n}, rules, name

    # ========== 回撤 ==========
    @staticmethod
    def drawdown_relative(n: int = None, rules: Rules = ("0 <= res <= 1",), name: Optional[str] = None) -> FactorConf:
        """相对回撤"""
        return _drawdown_relative, {"n": n}, rules, name

    @staticmethod
    def drawdown_absolute(n: int = None, rules: Rules = ("0 <= res < 1",), name: Optional[str] = None) -> FactorConf:
        """绝对回撤"""
        return _drawdown_absolute, {"n": n}, rules, name

    @staticmethod
    def drawdown_amount(n: int = None, rules: Rules = ("res >= 0",), name: Optional[str] = None) -> FactorConf:
        """回撤金额"""
        return _drawdown_amount, {"n": n}, rules, name

    # ========== 波动率 ==========
    @staticmethod
    def volatility_daily(n: int = None, rules: Rules = ("res > 0",), name: Optional[str] = None) -> FactorConf:
        """日波动率"""
        return _volatility_daily, {"n": n}, rules, name

    @staticmethod
    def volatility_period(n: int = None, rules: Rules = ("res > 0",), name: Optional[str] = None) -> FactorConf:
        """期间波动率"""
        return _volatility_period, {"n": n}, rules, name

    # ========== 收益率 ==========
    @staticmethod
    def return_total(n: int = None, rules: Rules = ("res > -1",), name: Optional[str] = None) -> FactorConf:
        """期间总收益率"""
        return _return_total, {"n": n}, rules, name

    @staticmethod
    def return_avg_daily(n: int = None, rules: Rules = ("res > -1",), name: Optional[str] = None) -> FactorConf:
        """平均日收益率"""
        return _return_avg_daily, {"n": n}, rules, name

    @staticmethod
    def return_annualized(n: int = None, rules: Rules = ("res > -1",), name: Optional[str] = None) -> FactorConf:
        """年化收益率"""
        return _return_annualized, {"n": n}, rules, name

    # ========== 最大回撤 ==========
    @staticmethod
    def max_drawdown(n: int = None, rules: Rules = ("0 <= res <= 1",), name: Optional[str] = None) -> FactorConf:
        """最大回撤"""
        return _max_drawdown, {"n": n}, rules, name

    # ========== 价格统计 ==========
    @staticmethod
    def price_average(n: int = None, rules: Rules = ("res > 0",), name: Optional[str] = None) -> FactorConf:
        """平均价格"""
        return _price_average, {"n": n}, rules, name

    @staticmethod
    def price_median(n: int = None, rules: Rules = ("res > 0",), name: Optional[str] = None) -> FactorConf:
        """中位数价格"""
        return _price_median, {"n": n}, rules, name

    @staticmethod
    def price_mode(n: int = None, rules: Rules = ("res > 0",), name: Optional[str] = None) -> FactorConf:
        """众数价格"""
        return _price_mode, {"n": n}, rules, name

    @staticmethod
    def price_range_stat(n: int = None, rules: Rules = ("res > 0",), name: Optional[str] = None) -> FactorConf:
        """价格极差"""
        return _price_range_stat, {"n": n}, rules, name

    @staticmethod
    def price_variance(n: int = None, rules: Rules = ("res >= 0",), name: Optional[str] = None) -> FactorConf:
        """价格方差"""
        return _price_variance, {"n": n}, rules, name

    @staticmethod
    def price_std(n: int = None, rules: Rules = ("res >= 0",), name: Optional[str] = None) -> FactorConf:
        """价格标准差"""
        return _price_std, {"n": n}, rules, name

    @staticmethod
    def price_cv(n: int = None, rules: Rules = ("res >= 0",), name: Optional[str] = None) -> FactorConf:
        """价格变异系数"""
        return _price_cv, {"n": n}, rules, name

    # ========== 趋势 ==========
    @staticmethod
    def trend_direction(segments: int = 3, rules: Rules = ("res in ['上涨', '下跌', '震荡']",), name: Optional[str] = None) -> FactorConf:
        """趋势方向"""
        return _trend_direction, {"segments": segments}, rules, name

    @staticmethod
    def trend_strength(segments: int = 3, rules: Rules = ("res > -1",), name: Optional[str] = None) -> FactorConf:
        """趋势强度"""
        return _trend_strength, {"segments": segments}, rules, name
