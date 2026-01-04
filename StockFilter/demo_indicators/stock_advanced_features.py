# -*- coding: utf-8 -*-
"""
@author: Zed
@file: stock_advanced_features.py
@time: 2026/1/2
@describe: 股票高级特征计算模块（基于基础统计指标）
"""
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import math

from stock_statistics import PriceLevelMetrics


@dataclass
class AdvancedFeatures:
    """高级特征数据类"""
    # 基础指标
    metrics: PriceLevelMetrics

    # 特征1: 躁动程度
    _agitation_level: float = None
    _agitation_score: str = None

    # 特征2: 洗盘识别
    _is_wash: bool = None
    _wash_type: str = None
    _wash_intensity: float = None

    @property
    def agitation_level(self) -> float:
        """
        躁动程度（数值）
        计算：|期间累计收益率| / 每日波动率累积之和

        说明：
        - 值越接近1，躁动越高（累积收益小但累积波动大）
        - 值越接近0，躁动越低（累积收益与累积波动匹配）
        - 含义：价格频繁波动但累积实际收益变化小
        """
        if self._agitation_level is not None:
            return self._agitation_level

        # 获取期间累计收益率绝对值
        total_return_abs = abs(self.metrics.return_total)

        # 获取每日波动率序列
        daily_volatility_series = self.metrics.volatility_daily_series

        if not daily_volatility_series:
            self._agitation_level = 0.0
            return self._agitation_level

        # 计算每日波动率累积之和
        cumulative_volatility = sum(daily_volatility_series)

        # 避免除零
        if cumulative_volatility == 0:
            self._agitation_level = 0.0
        else:
            self._agitation_level = total_return_abs / cumulative_volatility

        return self._agitation_level

    @property
    def agitation_score(self) -> str:
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
        if self._agitation_score is not None:
            return self._agitation_score

        level = self.agitation_level

        if level > 0.8:
            self._agitation_score = "极高躁动"
        elif level > 0.6:
            self._agitation_score = "高躁动"
        elif level > 0.4:
            self._agitation_score = "中高躁动"
        elif level > 0.2:
            self._agitation_score = "中等躁动"
        elif level > 0.1:
            self._agitation_score = "低躁动"
        else:
            self._agitation_score = "极低躁动"

        return self._agitation_score

    def is_wash_trading(self,
                       agitation_threshold: float = 0.2) -> bool:
        """
        是否为洗盘模式

        定义：
        洗盘 = 震荡趋势下的躁动

        参数:
            agitation_threshold: 躁动程度阈值（默认0.2）
                               超过此值认为存在躁动

        洗盘判断条件：
        1. 趋势为震荡
        2. 躁动程度 > 阈值

        返回:
            True: 检测到洗盘特征
            False: 未检测到洗盘特征
        """
        # 获取基础指标
        trend_direction = self.metrics.trend_direction
        agitation = self.agitation_level

        # 洗盘判断逻辑：震荡趋势 + 躁动
        if trend_direction == "震荡" and agitation > agitation_threshold:
            return True

        return False

    @property
    def wash_trading_type(self) -> Optional[str]:
        """
        洗盘类型

        定义：
        洗盘 = 震荡趋势下的躁动
        统一返回"震荡洗盘"

        类型：
        - 震荡洗盘: 趋势震荡 + 存在躁动
        - None: 非洗盘模式
        """
        if not self.is_wash_trading():
            return None

        return "震荡洗盘"

    @property
    def wash_trading_intensity(self) -> Optional[float]:
        """
        洗盘强度

        计算：躁动程度值

        说明：
        - 直接使用躁动程度作为洗盘强度
        - 值越大，洗盘越剧烈
        """
        if not self.is_wash_trading():
            return None

        return self.agitation_level

    def get_agitation_details(self) -> Dict[str, any]:
        """
        获取躁动程度详细信息

        返回:
            包含躁动程度详细信息的字典
        """
        # 获取每日波动率序列
        daily_volatility_series = self.metrics.volatility_daily_series
        cumulative_volatility = sum(daily_volatility_series) if daily_volatility_series else 0

        return {
            'agitation_level': round(self.agitation_level, 6),
            'agitation_score': self.agitation_score,
            'total_return': round(self.metrics.return_total, 6),
            'total_return_pct': round(self.metrics.return_total_pct, 4),
            'cumulative_volatility': round(cumulative_volatility, 6),
            'cumulative_volatility_pct': round(cumulative_volatility * 100, 4),
            'interpretation': self._interpret_agitation()
        }

    def get_wash_trading_details(self,
                                agitation_threshold: float = 0.2) -> Dict[str, any]:
        """
        获取洗盘详细信息

        参数:
            agitation_threshold: 躁动程度阈值

        返回:
            包含洗盘详细信息的字典
        """
        is_wash = self.is_wash_trading(agitation_threshold)

        details = {
            'is_wash_trading': is_wash,
            'wash_trading_type': self.wash_trading_type if is_wash else None,
            'trend_direction': self.metrics.trend_direction,
            'agitation_level': round(self.agitation_level, 6),
            'agitation_score': self.agitation_score,
            'agitation_threshold': agitation_threshold
        }

        if is_wash:
            details['wash_trading_intensity'] = self.wash_trading_intensity
            details['interpretation'] = self._interpret_wash_trading()

        return details

    def _interpret_agitation(self) -> str:
        """
        解释躁动程度

        返回:
            躁动程度的文字解释
        """
        level = self.agitation_level
        score = self.agitation_score

        if level > 0.8:
            return (f"【{score}】累积收益率{self.metrics.return_total_pct:+.2f}%，"
                   f"但累积波动率达到{sum(self.metrics.volatility_daily_series)*100:.2f}%，"
                   f"价格频繁波动但实际收益变化极小，处于极度浮躁状态")
        elif level > 0.6:
            return (f"【{score}】累积波动远大于累积收益，"
                   f"价格上蹿下跳但最终结果有限，多空博弈激烈")
        elif level > 0.4:
            return (f"【{score}】累积波动明显大于累积收益，"
                   f"存在一定程度的躁动")
        elif level > 0.2:
            return (f"【{score}】累积波动与累积收益基本匹配，"
                   f"躁动程度适中")
        elif level > 0.1:
            return (f"【{score}】累积波动与累积收益较为匹配，"
                   f"躁动程度较低")
        else:
            return (f"【{score}】累积波动与累积收益高度匹配，"
                   f"价格走势稳健，躁动程度极低")

    def _interpret_wash_trading(self) -> str:
        """
        解释洗盘特征

        返回:
            洗盘特征的文字解释
        """
        if not self.is_wash_trading():
            return "未检测到洗盘特征"

        agitation = self.agitation_level

        if agitation > 0.6:
            return (f"检测到【震荡洗盘】特征，躁动程度({agitation:.2%})较高。"
                   f"价格在区间内剧烈波动但方向不明，可能是主力在清洗浮筹，"
                   f"建议等待突破方向明确后再参与")
        elif agitation > 0.3:
            return (f"检测到【震荡洗盘】特征，躁动程度({agitation:.2%})中等。"
                   f"价格波动较明显但趋势不明，观望为主")
        else:
            return (f"检测到【震荡洗盘】特征，躁动程度({agitation:.2%})较低。"
                   f"虽然趋势震荡但波动有限，风险可控")

    def to_dict(self) -> Dict[str, any]:
        """
        转换为字典格式

        返回:
            包含所有高级特征的字典
        """
        return {
            'agitation': self.get_agitation_details(),
            'wash_trading': self.get_wash_trading_details()
        }

    def __repr__(self):
        return (f"<AdvancedFeatures "
                f"躁动={self.agitation_score} "
                f"洗盘={self.wash_trading_type}>")


def calculate_advanced_features(
    metrics: PriceLevelMetrics
) -> AdvancedFeatures:
    """
    计算高级特征

    参数:
        metrics: 价格水平统计指标对象

    返回:
        AdvancedFeatures 对象

    示例:
        from stock_market_api import get_history
        from stock_statistics import calculate_price_level
        from stock_advanced_features import calculate_advanced_features

        # 获取数据并计算基础指标
        data = get_history("000001.SZ", limit=60)
        metrics = calculate_price_level(data)

        # 计算高级特征
        features = calculate_advanced_features(metrics)

        # 获取躁动程度
        print(f"躁动程度: {features.agitation_score}")
        print(f"躁动级别: {features.agitation_level:.4f}")

        # 判断洗盘
        if features.is_wash_trading:
            print(f"洗盘类型: {features.wash_trading_type}")
            print(f"洗盘强度: {features.wash_trading_intensity:.2f}")
    """
    return AdvancedFeatures(metrics=metrics)
