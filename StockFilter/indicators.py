# -*- coding: utf-8 -*-
"""
技术指标库 - 基于 StockFilter 框架

所有指标遵循 StockFilter 的因子配置规范
"""
from typing import Dict, List, Tuple, Any

Rule = str
Rules = Tuple[Rule, ...]
FactorConf = Tuple[callable, Dict[str, Any], Rules]


# ==================== 工具函数 ====================

def _safe_mean(values: List[float]) -> float:
    """安全计算均值"""
    return sum(values) / len(values) if values else 0.0


def _safe_max(values: List[float]) -> float:
    """安全计算最大值"""
    return max(values) if values else 0.0


def _safe_min(values: List[float]) -> float:
    """安全计算最小值"""
    return min(values) if values else 0.0


# ==================== 1. 均线类指标 ====================

def _ma(data: Dict[str, List], n: int = 5, **kwargs) -> Dict[str, float]:
    """移动平均线"""
    closes = data['close'][-n:]
    return {"ma": sum(closes) / len(closes) if closes else 0.0}


def _ema(data: Dict[str, List], n: int = 12, **kwargs) -> Dict[str, float]:
    """指数移动平均线"""
    closes = data['close']
    if len(closes) < n:
        return {"ema": closes[-1] if closes else 0.0}

    alpha = 2 / (n + 1)
    ema = closes[0]
    for price in closes[1:]:
        ema = alpha * price + (1 - alpha) * ema
    return {"ema": ema}


# ==================== 2. 价格类指标 ====================

def _close_price(data: Dict[str, List], **kwargs) -> Dict[str, float]:
    """收盘价"""
    close = data['close'][-1] if data['close'] else 0.0
    return {"close": close}


def _high_price(data: Dict[str, List], **kwargs) -> Dict[str, float]:
    """最高价"""
    high = data['high'][-1] if data['high'] else 0.0
    return {"high": high}


def _low_price(data: Dict[str, List], **kwargs) -> Dict[str, float]:
    """最低价"""
    low = data['low'][-1] if data['low'] else 0.0
    return {"low": low}


def _volume(data: Dict[str, List], **kwargs) -> Dict[str, float]:
    """成交量"""
    vol = data['volume'][-1] if data['volume'] else 0.0
    return {"volume": vol}


# ==================== 3. 统计类指标 ====================

def _max_price(data: Dict[str, List], n: int = 20, **kwargs) -> Dict[str, float]:
    """期间最高价"""
    highs = data['high'][-n:]
    return {"max_price": _safe_max(highs)}


def _min_price(data: Dict[str, List], n: int = 20, **kwargs) -> Dict[str, float]:
    """期间最低价"""
    lows = data['low'][-n:]
    return {"min_price": _safe_min(lows)}


def _price_range(data: Dict[str, List], n: int = 20, **kwargs) -> Dict[str, float]:
    """价格振幅"""
    highs = data['high'][-n:]
    lows = data['low'][-n:]

    max_high = _safe_max(highs)
    min_low = _safe_min(lows)

    if min_low == 0:
        return {"price_range": 0.0}

    range_val = (max_high - min_low) / min_low
    return {"price_range": range_val}


# ==================== 4. 涨跌幅类指标 ====================

def _return_rate(data: Dict[str, List], n: int = 5, **kwargs) -> Dict[str, float]:
    """N日涨跌幅"""
    closes = data['close']

    if len(closes) < n + 1:
        return {"return_rate": 0.0}

    current_close = closes[-1]
    prev_close = closes[-n - 1]

    if prev_close == 0:
        return {"return_rate": 0.0}

    return_rate = (current_close - prev_close) / prev_close
    return {"return_rate": return_rate}


def _cumulative_return(data: Dict[str, List], n: int = 20, **kwargs) -> Dict[str, float]:
    """N日累积涨跌幅"""
    closes = data['close']

    if len(closes) < n + 1:
        return {"cumulative_return": 0.0}

    start_close = closes[-n - 1]
    end_close = closes[-1]

    if start_close == 0:
        return {"cumulative_return": 0.0}

    cum_return = (end_close - start_close) / start_close
    return {"cumulative_return": cum_return}


# ==================== 5. 波动率类指标 ====================

def _volatility(data: Dict[str, List], n: int = 20, **kwargs) -> Dict[str, float]:
    """波动率(标准差)"""
    closes = data['close'][-n:]

    if len(closes) < 2:
        return {"volatility": 0.0}

    mean = _safe_mean(closes)
    variance = sum((x - mean) ** 2 for x in closes) / len(closes)
    volatility = variance ** 0.5

    return {"volatility": volatility}


# ==================== 6. 成交量类指标 ====================

def _volume_mean(data: Dict[str, List], n: int = 5, **kwargs) -> Dict[str, float]:
    """成交量均值"""
    volumes = data['volume'][-n:]
    return {"volume_mean": _safe_mean(volumes)}


def _volume_ratio(data: Dict[str, List], n: int = 5, **kwargs) -> Dict[str, float]:
    """量比"""
    volumes = data['volume']

    if len(volumes) < n + 1:
        return {"volume_ratio": 1.0}

    current_vol = volumes[-1]
    mean_vol = _safe_mean(volumes[-n - 1:-1])

    if mean_vol == 0:
        return {"volume_ratio": 1.0}

    ratio = current_vol / mean_vol
    return {"volume_ratio": ratio}


# ==================== 7. 技术指标 ====================

def _rsi(data: Dict[str, List], n: int = 14, **kwargs) -> Dict[str, float]:
    """RSI指标"""
    closes = data['close']

    if len(closes) < n + 1:
        return {"rsi": 50.0}

    gains = []
    losses = []

    for i in range(1, len(closes)):
        change = closes[i] - closes[i - 1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))

    if len(gains) < n:
        return {"rsi": 50.0}

    avg_gain = _safe_mean(gains[-n:])
    avg_loss = _safe_mean(losses[-n:])

    if avg_loss == 0:
        return {"rsi": 100.0 if avg_gain else 50.0}

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return {"rsi": rsi}


def _bollinger_upper(data: Dict[str, List], n: int = 20, multiplier: float = 2.0, **kwargs) -> Dict[str, float]:
    """布林带上轨"""
    closes = data['close'][-n:]

    if len(closes) < n:
        return {"bollinger_upper": closes[-1] if closes else 0.0}

    mean = _safe_mean(closes)
    variance = sum((x - mean) ** 2 for x in closes) / len(closes)
    std = variance ** 0.5

    upper = mean + multiplier * std
    return {"bollinger_upper": upper}


def _bollinger_lower(data: Dict[str, List], n: int = 20, multiplier: float = 2.0, **kwargs) -> Dict[str, float]:
    """布林带下轨"""
    closes = data['close'][-n:]

    if len(closes) < n:
        return {"bollinger_lower": closes[-1] if closes else 0.0}

    mean = _safe_mean(closes)
    variance = sum((x - mean) ** 2 for x in closes) / len(closes)
    std = variance ** 0.5

    lower = mean - multiplier * std
    return {"bollinger_lower": lower}


# ==================== 8. 因子类(配置工厂) ====================

class Factor:
    """
    因子配置工厂类

    提供17个技术指标的配置方法
    """

    # ========== 均线类 ==========
    @staticmethod
    def ma(n: int = 5, rules: Rules = ("ma > 0",)) -> FactorConf:
        """移动平均线"""
        return _ma, {"n": n}, rules

    @staticmethod
    def ema(n: int = 12, rules: Rules = ("ema > 0",)) -> FactorConf:
        """指数移动平均线"""
        return _ema, {"n": n}, rules

    # ========== 价格类 ==========
    @staticmethod
    def close_price(rules: Rules = ("close > 0",)) -> FactorConf:
        """收盘价"""
        return _close_price, {}, rules

    @staticmethod
    def high_price(rules: Rules = ("high > 0",)) -> FactorConf:
        """最高价"""
        return _high_price, {}, rules

    @staticmethod
    def low_price(rules: Rules = ("low > 0",)) -> FactorConf:
        """最低价"""
        return _low_price, {}, rules

    @staticmethod
    def volume(rules: Rules = ("volume > 0",)) -> FactorConf:
        """成交量"""
        return _volume, {}, rules

    # ========== 统计类 ==========
    @staticmethod
    def max_price(n: int = 20, rules: Rules = ("max_price > 0",)) -> FactorConf:
        """期间最高价"""
        return _max_price, {"n": n}, rules

    @staticmethod
    def min_price(n: int = 20, rules: Rules = ("min_price > 0",)) -> FactorConf:
        """期间最低价"""
        return _min_price, {"n": n}, rules

    @staticmethod
    def price_range(n: int = 20, rules: Rules = ("price_range > 0",)) -> FactorConf:
        """价格振幅"""
        return _price_range, {"n": n}, rules

    # ========== 涨跌幅类 ==========
    @staticmethod
    def return_rate(n: int = 5, rules: Rules = ("return_rate > 0",)) -> FactorConf:
        """N日涨跌幅"""
        return _return_rate, {"n": n}, rules

    @staticmethod
    def cumulative_return(n: int = 20, rules: Rules = ("cumulative_return > 0",)) -> FactorConf:
        """N日累积涨跌幅"""
        return _cumulative_return, {"n": n}, rules

    # ========== 波动率类 ==========
    @staticmethod
    def volatility(n: int = 20, rules: Rules = ("volatility < 0.5",)) -> FactorConf:
        """波动率"""
        return _volatility, {"n": n}, rules

    # ========== 成交量类 ==========
    @staticmethod
    def volume_mean(n: int = 5, rules: Rules = ("volume_mean > 0",)) -> FactorConf:
        """成交量均值"""
        return _volume_mean, {"n": n}, rules

    @staticmethod
    def volume_ratio(n: int = 5, rules: Rules = ("volume_ratio > 1.0",)) -> FactorConf:
        """量比"""
        return _volume_ratio, {"n": n}, rules

    # ========== 技术指标类 ==========
    @staticmethod
    def rsi(n: int = 14, rules: Rules = ("30 < rsi < 70",)) -> FactorConf:
        """RSI指标"""
        return _rsi, {"n": n}, rules

    @staticmethod
    def bollinger_upper(n: int = 20, multiplier: float = 2.0,
                       rules: Rules = ("bollinger_upper > 0",)) -> FactorConf:
        """布林带上轨"""
        return _bollinger_upper, {"n": n, "multiplier": multiplier}, rules

    @staticmethod
    def bollinger_lower(n: int = 20, multiplier: float = 2.0,
                       rules: Rules = ("bollinger_lower > 0",)) -> FactorConf:
        """布林带下轨"""
        return _bollinger_lower, {"n": n, "multiplier": multiplier}, rules
