# -*- coding: utf-8 -*-
"""
链式调用支持 - 基于 StockFilter 框架

提供优雅的链式调用语法
"""
from typing import Dict, List, Any
from stock_filter import Config

Rule = str
Rules = tuple
FactorConf = tuple


class FactorChain:
    """
    因子链式调用类

    支持通过 .and_() 方法链式添加多个因子
    """

    def __init__(self, *confs: FactorConf):
        """
        初始化因子链

        Args:
            *confs: 一个或多个因子配置元组
        """
        self.chain = list(confs)

    def and_(self, *confs: FactorConf) -> 'FactorChain':
        """
        向链条中添加更多因子

        Args:
            *confs: 一个或多个因子配置元组

        Returns:
            返回自身以支持链式调用

        Example:
            >>> chain = Chain(
            ...     Factor.ma(n=5, rules=("ma > 0",)),
            ...     Factor.return_rate(n=10)
            ... ).and_(
            ...     Factor.volatility(n=20, rules=("volatility < 0.5",))
            ... )
        """
        self.chain.extend(confs)
        return self

    def run(self, data: Dict[str, List]) -> Dict[str, Any]:
        """
        运行因子链

        Args:
            data: OHLCV 格式的行情数据

        Returns:
            包含 pass 和 details 的结果字典
        """
        config = Config(*self.chain)
        return config.run(data)


def Chain(*confs: FactorConf) -> FactorChain:
    """
    创建因子链的便捷函数

    Args:
        *confs: 一个或多个因子配置元组

    Returns:
        FactorChain 实例

    Example:
        >>> chain = Chain(
        ...     Factor.ma(n=5, rules=("ma > 0",)),
        ...     Factor.rsi(n=14, rules=("30 < rsi < 70",))
        ... )
        >>> result = chain.run(data)
    """
    return FactorChain(*confs)
