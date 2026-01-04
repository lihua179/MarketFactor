# -*- coding: utf-8 -*-
"""
高级特征指标因子 - 基于 StockFilter 框架

基于 stock_advanced_features.py 的实现公式，为 StockFilter 系统提供高级特征指标
包括：躁动程度、洗盘识别等

特性：
1. 支持参数化配置（agitation_threshold 等）
2. 统一使用 'res' 作为结果键名（便于规则编写）
3. 规则编写更简洁：rules=("res > 0.5",) 而不用 ("agitation_level > 0.5",)
"""
from typing import Dict, List, Tuple, Any, Optional

Rule = str
Rules = Tuple[Rule, ...]
FactorConf = Tuple[callable, Dict[str, Any], Rules, Optional[str]]


# ==================== 辅助函数 ====================

def _get_daily_volatility_series(data: Dict[str, List]) -> List[float]:
    """获取日波动率序列"""
    high_list = data['high']
    low_list = data['low']
    yd_close_list = data.get('yd_close', [])

    if not high_list or not low_list or not yd_close_list:
        return []

    min_len = min(len(high_list), len(low_list), len(yd_close_list))
    daily_volatilities = []

    for i in range(min_len):
        if yd_close_list[i] > 0:
            vol = (high_list[i] - low_list[i]) / yd_close_list[i]
            daily_volatilities.append(vol)
        else:
            daily_volatilities.append(0.0)

    return daily_volatilities


def _get_return_total(data: Dict[str, List]) -> float:
    """获取期间总收益率"""
    close_list = data['close']

    if len(close_list) < 2:
        return 0.0

    start_price = close_list[0]
    end_price = close_list[-1]

    if start_price == 0:
        return 0.0

    return (end_price - start_price) / start_price


# ==================== 躁动程度指标 ====================

def _agitation_level(data: Dict[str, List], **kwargs) -> Dict[str, float]:
    """
    躁动程度（数值）
    计算：|期间累计收益率| / 每日波动率累积之和

    说明：
    - 值越接近1，躁动越高（累积收益小但累积波动大）
    - 值越接近0，躁动越低（累积收益与累积波动匹配）
    - 含义：价格频繁波动但累积实际收益变化小
    """
    # 获取期间累计收益率绝对值
    total_return = abs(_get_return_total(data))

    # 获取每日波动率序列
    daily_volatility_series = _get_daily_volatility_series(data)

    if not daily_volatility_series:
        return {"res": 0.0}

    # 计算每日波动率累积之和
    cumulative_volatility = sum(daily_volatility_series)

    # 避免除零
    if cumulative_volatility == 0:
        return {"res": 0.0}

    agitation_level = total_return / cumulative_volatility
    return {"res": agitation_level}


def _agitation_score(data: Dict[str, List], **kwargs) -> Dict[str, str]:
    """
    躁动程度评分（分级）

    评分标准（基于躁动程度值）：
    - 极高躁动: agitation_level > 0.8
    - 高躁动: 0.6 < agitation_level <= 0.8
    - 中高躁动: 0.4 < agitation_level <= 0.6
    - 中等躁动: 0.2 < agitation_level <= 0.4
    - 低躁动: 0.1 < agitation_level <= 0.2
    - 极低躁动: agitation_level <= 0.1
    """
    result = _agitation_level(data)
    level = result['res']

    if level > 0.8:
        score = "极高躁动"
    elif level > 0.6:
        score = "高躁动"
    elif level > 0.4:
        score = "中高躁动"
    elif level > 0.2:
        score = "中等躁动"
    elif level > 0.1:
        score = "低躁动"
    else:
        score = "极低躁动"

    return {"res": score}


# ==================== 洗盘识别指标 ====================

def _is_wash_trading(data: Dict[str, List], agitation_threshold: float = 0.2, **kwargs) -> Dict[str, bool]:
    """
    是否为洗盘模式

    定义：
    洗盘 = 震荡趋势下的躁动

    参数:
        agitation_threshold: 躁动程度阈值（默认0.2）

    洗盘判断条件：
    1. 趋势为震荡
    2. 躁动程度 > 阈值
    """
    # 获取趋势方向
    close_list = data['close']

    if len(close_list) < 6:
        return {"res": False}

    n = len(close_list)
    segment_size = n // 3

    segment1 = close_list[:segment_size]
    segment2 = close_list[segment_size:segment_size*2]
    segment3 = close_list[segment_size*2:]

    avg1 = sum(segment1) / len(segment1)
    avg2 = sum(segment2) / len(segment2)
    avg3 = sum(segment3) / len(segment3)

    # 判断趋势
    if avg1 < avg2 < avg3:
        trend_direction = "上涨"
    elif avg1 > avg2 > avg3:
        trend_direction = "下跌"
    else:
        trend_direction = "震荡"

    # 获取躁动程度
    agitation_result = _agitation_level(data)
    agitation = agitation_result['res']

    # 洗盘判断逻辑：震荡趋势 + 躁动
    is_wash = (trend_direction == "震荡" and agitation > agitation_threshold)

    return {"res": is_wash}


def _wash_trading_type(data: Dict[str, List], agitation_threshold: float = 0.2, **kwargs) -> Dict[str, str]:
    """
    洗盘类型

    定义：
    洗盘 = 震荡趋势下的躁动
    统一返回"震荡洗盘"或"无洗盘"

    参数:
        agitation_threshold: 躁动程度阈值
    """
    result = _is_wash_trading(data, agitation_threshold)
    is_wash = result['res']

    if is_wash:
        return {"res": "震荡洗盘"}
    else:
        return {"res": "无洗盘"}


def _wash_trading_intensity(data: Dict[str, List], agitation_threshold: float = 0.2, **kwargs) -> Dict[str, float]:
    """
    洗盘强度

    计算：躁动程度值

    说明：
    - 直接使用躁动程度作为洗盘强度
    - 值越大，洗盘越剧烈
    - 如果不是洗盘，返回0

    参数:
        agitation_threshold: 躁动程度阈值
    """
    result = _is_wash_trading(data, agitation_threshold)
    is_wash = result['res']

    if not is_wash:
        return {"res": 0.0}

    agitation_result = _agitation_level(data)
    agitation = agitation_result['res']

    return {"res": agitation}


# ==================== 辅助统计 ====================

def _cumulative_volatility(data: Dict[str, List], **kwargs) -> Dict[str, float]:
    """
    累积波动率
    计算：每日波动率累积之和
    """
    daily_volatility_series = _get_daily_volatility_series(data)
    cumulative_volatility = sum(daily_volatility_series) if daily_volatility_series else 0

    return {"res": cumulative_volatility}


# ==================== 因子配置工厂 ====================

class AdvancedFeatures:
    """
    高级特征指标配置工厂类

    所有因子都支持：
    1. 参数化配置（agitation_threshold 等）
    2. 自定义名称（name 参数）
    3. 统一的结果键名 'res'（便于规则编写）
    """

    # ========== 躁动程度 ==========
    @staticmethod
    def agitation_level(rules: Rules = ("0 <= res <= 1",), name: Optional[str] = None) -> FactorConf:
        """躁动程度数值"""
        return _agitation_level, {}, rules, name

    @staticmethod
    def agitation_score(rules: Rules = ("res in ['极高躁动', '高躁动', '中高躁动', '中等躁动', '低躁动', '极低躁动']",), name: Optional[str] = None) -> FactorConf:
        """躁动程度评分"""
        return _agitation_score, {}, rules, name

    # ========== 洗盘识别 ==========
    @staticmethod
    def is_wash_trading(agitation_threshold: float = 0.2,
                       rules: Rules = ("res == True or res == False",),
                       name: Optional[str] = None) -> FactorConf:
        """是否洗盘"""
        return _is_wash_trading, {"agitation_threshold": agitation_threshold}, rules, name

    @staticmethod
    def wash_trading_type(agitation_threshold: float = 0.2,
                         rules: Rules = ("res in ['震荡洗盘', '无洗盘']",),
                         name: Optional[str] = None) -> FactorConf:
        """洗盘类型"""
        return _wash_trading_type, {"agitation_threshold": agitation_threshold}, rules, name

    @staticmethod
    def wash_trading_intensity(agitation_threshold: float = 0.2,
                              rules: Rules = ("res >= 0",),
                              name: Optional[str] = None) -> FactorConf:
        """洗盘强度"""
        return _wash_trading_intensity, {"agitation_threshold": agitation_threshold}, rules, name

    # ========== 辅助指标 ==========
    @staticmethod
    def cumulative_volatility(rules: Rules = ("res > 0",), name: Optional[str] = None) -> FactorConf:
        """累积波动率"""
        return _cumulative_volatility, {}, rules, name
