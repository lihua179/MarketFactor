# -*- coding: utf-8 -*-
"""
@author: Zed
@file: stock_analysis.py
@time: 2026/1/2
@describe: 股票统一分析模块 - 整合所有指标和特征的统一入口
"""
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, field

from stock_market_api import get_history
from stock_statistics import calculate_price_level, PriceLevelMetrics
from stock_advanced_features import calculate_advanced_features, AdvancedFeatures
from explosive_start import find_explosive_start, ExplosiveStartResult


@dataclass
class StockAnalysisResult:
    """股票分析结果（统一数据类）"""
    # 基础信息
    symbol: str = ""
    data_length: int = 0

    # 基础指标对象
    metrics: Optional[PriceLevelMetrics] = None

    # 高级特征对象
    advanced_features: Optional[AdvancedFeatures] = None

    # 异动检测结果
    surge_detection: Optional[ExplosiveStartResult] = None

    def to_dict(self) -> Dict:
        """转换为完整字典"""
        result = {
            'symbol': self.symbol,
            'data_length': self.data_length,
        }

        # 添加基础指标
        if self.metrics is not None:
            result['metrics'] = self.metrics.to_dict()

        # 添加高级特征
        if self.advanced_features is not None:
            result['advanced_features'] = self.advanced_features.to_dict()

        # 添加异动检测
        if self.surge_detection is not None:
            result['surge_detection'] = self.surge_detection.to_dict()

        return result

    def get_summary(self) -> Dict[str, str]:
        """获取摘要信息（用于快速查看）"""
        summary = {
            'symbol': self.symbol,
            'data_length': f"{self.data_length}个交易日",
        }

        # 基础指标摘要
        if self.metrics is not None:
            summary.update({
                '当前价格': f"{self.metrics.current_price:.2f}元",
                '趋势方向': self.metrics.trend_direction,
                '趋势强度': f"{self.metrics.trend_strength_pct:+.2f}%",
                '期间收益率': f"{self.metrics.return_total_pct:+.2f}%",
                '期间波动率': f"{self.metrics.volatility_period_pct:.2f}%",
                '当前价格水平': f"{self.metrics.level_relative:.2%}",
            })

        # 高级特征摘要
        if self.advanced_features is not None:
            summary.update({
                '躁动程度': self.advanced_features.agitation_score,
                '躁动级别': f"{self.advanced_features.agitation_level:.6f}",
                '是否洗盘': "是" if self.advanced_features.is_wash_trading() else "否",
            })

        # 异动检测摘要
        if self.surge_detection is not None:
            if self.surge_detection.has_surge_window:
                summary.update({
                    '异动窗口': f"第{self.surge_detection.window_start_index}-{self.surge_detection.window_end_index}日",
                    '最高价位置': f"第{self.surge_detection.highest_price_index}日",
                    '异动涨幅': f"{self.surge_detection.surge_return_pct:.2f}%",
                })
            else:
                summary['异动窗口'] = "未找到"

        return summary


class StockAnalyzer:
    """股票分析器（统一入口）"""

    def __init__(self, symbol: str = None, limit: int = 60):
        """
        初始化分析器

        参数:
            symbol: 股票代码（如"000001.SZ"）
            limit: 数据长度（默认60个交易日）
        """
        self.symbol = symbol
        self.limit = limit
        self.data = None
        self.metrics = None
        self.result = None

    def analyze(self,
                symbol: str = None,
                limit: int = None,
                enable_advanced: bool = True,
                enable_surge: bool = True,
                surge_window_length: int = 10,
                surge_threshold: float = 0.15) -> StockAnalysisResult:
        """
        执行完整的股票分析

        参数:
            symbol: 股票代码
            limit: 数据长度
            enable_advanced: 是否计算高级特征（躁动、洗盘）
            enable_surge: 是否检测异动涨幅
            surge_window_length: 异动检测窗口长度
            surge_threshold: 异动检测目标阈值

        返回:
            StockAnalysisResult 对象，包含所有分析结果
        """
        # 参数处理
        symbol = symbol or self.symbol
        limit = limit or self.limit

        if not symbol:
            raise ValueError("股票代码不能为空")

        # 1. 获取数据
        self.data = get_history(symbol, limit=limit)

        # 2. 计算基础指标（必须）
        self.metrics = calculate_price_level(self.data)

        # 3. 计算高级特征（可选）
        advanced_features = None
        if enable_advanced:
            advanced_features = calculate_advanced_features(self.metrics)

        # 4. 检测异动涨幅（可选）
        surge_detection = None
        if enable_surge:
            surge_detection = find_explosive_start(
                self.metrics,
                window_length=surge_window_length,
                target_threshold=surge_threshold
            )

        # 5. 组装结果
        self.result = StockAnalysisResult(
            symbol=symbol,
            data_length=limit,
            metrics=self.metrics,
            advanced_features=advanced_features,
            surge_detection=surge_detection
        )

        return self.result

    def quick_analysis(self, symbol: str, limit: int = 60) -> Dict[str, str]:
        """
        快速分析（返回摘要信息）

        参数:
            symbol: 股票代码
            limit: 数据长度

        返回:
            摘要字典，包含关键指标
        """
        result = self.analyze(symbol, limit)

        return result.get_summary()

    def batch_analyze(self,
                     symbols: List[str],
                     limit: int = 60,
                     enable_advanced: bool = True,
                     enable_surge: bool = True,
                     surge_window_length: int = 10,
                     surge_threshold: float = 0.15) -> List[StockAnalysisResult]:
        """
        批量分析多只股票

        参数:
            symbols: 股票代码列表
            limit: 数据长度
            enable_advanced: 是否计算高级特征
            enable_surge: 是否检测异动涨幅
            surge_window_length: 异动检测窗口长度
            surge_threshold: 异动检测目标阈值

        返回:
            分析结果列表
        """
        results = []

        for symbol in symbols:
            try:
                result = self.analyze(
                    symbol=symbol,
                    limit=limit,
                    enable_advanced=enable_advanced,
                    enable_surge=enable_surge,
                    surge_window_length=surge_window_length,
                    surge_threshold=surge_threshold
                )
                results.append(result)
            except Exception as e:
                print(f"警告: {symbol} 分析失败 - {e}")
                # 可以选择创建一个空结果或者跳过
                continue

        return results

    def __repr__(self):
        return f"<StockAnalyzer symbol={self.symbol} limit={self.limit}>"


# ==================== 便捷函数 ====================

def analyze_stock(symbol: str,
                  limit: int = 60,
                  enable_advanced: bool = True,
                  enable_surge: bool = True,
                  surge_window_length: int = 10,
                  surge_threshold: float = 0.15) -> StockAnalysisResult:
    """
    分析单只股票（便捷函数）

    参数:
        symbol: 股票代码
        limit: 数据长度
        enable_advanced: 是否计算高级特征
        enable_surge: 是否检测异动涨幅
        surge_window_length: 异动检测窗口长度
        surge_threshold: 异动检测目标阈值

    返回:
        StockAnalysisResult 对象

    示例:
        >>> from stock_analysis import analyze_stock
        >>>
        >>> # 完整分析
        >>> result = analyze_stock("000001.SZ", limit=60)
        >>>
        >>> # 查看摘要
        >>> summary = result.get_summary()
        >>> for key, value in summary.items():
        >>>     print(f"{key}: {value}")
        >>>
        >>> # 获取完整数据
        >>> full_data = result.to_dict()
        >>>
        >>> # 只计算基础指标（更快）
        >>> result_basic = analyze_stock("000001.SZ", enable_advanced=False, enable_surge=False)
    """
    analyzer = StockAnalyzer()
    return analyzer.analyze(
        symbol=symbol,
        limit=limit,
        enable_advanced=enable_advanced,
        enable_surge=enable_surge,
        surge_window_length=surge_window_length,
        surge_threshold=surge_threshold
    )


def quick_analyze(symbol: str, limit: int = 60) -> Dict[str, str]:
    """
    快速分析单只股票（返回摘要）

    参数:
        symbol: 股票代码
        limit: 数据长度

    返回:
        摘要字典

    示例:
        >>> from stock_analysis import quick_analyze
        >>>
        >>> summary = quick_analyze("000001.SZ")
        >>> for key, value in summary.items():
        >>>     print(f"{key}: {value}")
    """
    analyzer = StockAnalyzer()
    return analyzer.quick_analysis(symbol, limit)


def batch_analyze_stocks(symbols: List[str],
                         limit: int = 60,
                         enable_advanced: bool = True,
                         enable_surge: bool = True,
                         surge_window_length: int = 10,
                         surge_threshold: float = 0.15) -> List[StockAnalysisResult]:
    """
    批量分析多只股票（便捷函数）

    参数:
        symbols: 股票代码列表
        limit: 数据长度
        enable_advanced: 是否计算高级特征
        enable_surge: 是否检测异动涨幅
        surge_window_length: 异动检测窗口长度
        surge_threshold: 异动检测目标阈值

    返回:
        分析结果列表

    示例:
        >>> from stock_analysis import batch_analyze_stocks
        >>>
        >>> symbols = ["000001.SZ", "000002.SZ", "600000.SH"]
        >>> results = batch_analyze_stocks(symbols, limit=60)
        >>>
        >>> for result in results:
        >>>     summary = result.get_summary()
        >>>     print(f"{summary['symbol']}: {summary['期间收益率']}, {summary['躁动程度']}")
    """
    analyzer = StockAnalyzer()
    return analyzer.batch_analyze(
        symbols=symbols,
        limit=limit,
        enable_advanced=enable_advanced,
        enable_surge=enable_surge,
        surge_window_length=surge_window_length,
        surge_threshold=surge_threshold
    )


def filter_stocks_by_conditions(results: List[StockAnalysisResult],
                                  conditions: Dict[str, any]) -> List[StockAnalysisResult]:
    """
    根据条件筛选股票

    参数:
        results: 分析结果列表
        conditions: 筛选条件字典

    支持的条件：
        - min_return: 最小期间收益率
        - max_return: 最大期间收益率
        - trend: 趋势方向（"上涨"/"下跌"/"震荡"）
        - min_agitation: 最小躁动程度
        - max_agitation: 最大躁动程度
        - is_wash: 是否洗盘
        - has_surge: 是否有异动窗口
        - min_surge_return: 最小异动涨幅

    返回:
        筛选后的结果列表

    示例:
        >>> from stock_analysis import batch_analyze_stocks, filter_stocks_by_conditions
        >>>
        >>> # 批量分析
        >>> results = batch_analyze_stocks(symbols, limit=60)
        >>>
        >>> # 筛选条件：上涨趋势，躁动程度<0.3，有异动窗口
        >>> conditions = {
        >>>     'trend': '上涨',
        >>>     'max_agitation': 0.3,
        >>>     'has_surge': True
        >>> }
        >>>
        >>> filtered = filter_stocks_by_conditions(results, conditions)
        >>>
        >>> print(f"符合条件的股票: {len(filtered)}只")
        >>> for result in filtered:
        >>>     summary = result.get_summary()
        >>>     print(f"{summary['symbol']}: {summary['期间收益率']}")
    """
    filtered = []

    for result in results:
        try:
            # 检查基础指标条件
            if result.metrics is not None:
                # 期间收益率条件
                if 'min_return' in conditions:
                    if result.metrics.return_total < conditions['min_return']:
                        continue

                if 'max_return' in conditions:
                    if result.metrics.return_total > conditions['max_return']:
                        continue

                # 趋势方向条件
                if 'trend' in conditions:
                    if result.metrics.trend_direction != conditions['trend']:
                        continue

            # 检查高级特征条件
            if result.advanced_features is not None:
                # 躁动程度条件
                if 'min_agitation' in conditions:
                    if result.advanced_features.agitation_level < conditions['min_agitation']:
                        continue

                if 'max_agitation' in conditions:
                    if result.advanced_features.agitation_level > conditions['max_agitation']:
                        continue

                # 洗盘条件
                if 'is_wash' in conditions:
                    is_wash = result.advanced_features.is_wash_trading()
                    if is_wash != conditions['is_wash']:
                        continue

            # 检查异动检测条件
            if result.surge_detection is not None:
                # 异动窗口条件
                if 'has_surge' in conditions:
                    if result.surge_detection.has_surge_window != conditions['has_surge']:
                        continue

                # 异动涨幅条件
                if 'min_surge_return' in conditions:
                    if result.surge_detection.has_surge_window:
                        if result.surge_detection.surge_return < conditions['min_surge_return']:
                            continue
                    else:
                        continue

            # 所有条件都满足
            filtered.append(result)

        except Exception as e:
            print(f"筛选错误 {result.symbol}: {e}")
            continue

    return filtered


def export_to_csv(results: List[StockAnalysisResult],
                   filename: str = "stock_analysis.csv"):
    """
    导出分析结果到CSV文件

    参数:
        results: 分析结果列表
        filename: 输出文件名

    示例:
        >>> from stock_analysis import batch_analyze_stocks, export_to_csv
        >>>
        >>> results = batch_analyze_stocks(symbols, limit=60)
        >>> export_to_csv(results, "analysis_results.csv")
    """
    import csv

    if not results:
        print("没有结果可导出")
        return

    # 准备数据
    rows = []
    for result in results:
        summary = result.get_summary()
        rows.append(summary)

    # 写入CSV
    if rows:
        # 收集所有可能的字段名（不同结果可能包含不同字段）
        all_fields = set()
        for row in rows:
            all_fields.update(row.keys())

        # 排序字段名以确保一致性
        sorted_fields = sorted(all_fields)

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=sorted_fields, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(rows)

        print(f"[SUCCESS] 已导出 {len(rows)} 条记录到 {filename}")
        print(f"  包含字段: {len(sorted_fields)}个")
    else:
        print("没有数据可导出")


def print_analysis_table(results: List[StockAnalysisResult],
                       fields: List[str] = None):
    """
    打印分析结果表格

    参数:
        results: 分析结果列表
        fields: 要显示的字段列表（None表示显示默认字段）

    默认字段:
        - symbol: 股票代码
        - 期间收益率
        - 趋势方向
        - 躁动程度
        - 是否洗盘
        - 异动窗口

    示例:
        >>> from stock_analysis import batch_analyze_stocks, print_analysis_table
        >>>
        >>> results = batch_analyze_stocks(symbols, limit=60)
        >>> print_analysis_table(results)
    """
    if not results:
        print("没有结果可显示")
        return

    # 默认字段
    if fields is None:
        fields = ['symbol', '期间收益率', '趋势方向', '躁动程度', '是否洗盘', '异动窗口']

    # 计算每列宽度
    col_widths = {}
    for field in fields:
        col_widths[field] = max(len(field), 12)

    # 收集数据
    rows = []
    for result in results:
        summary = result.get_summary()
        rows.append(summary)

    # 更新宽度
    for row in rows:
        for field in fields:
            value = str(row.get(field, '-'))
            col_widths[field] = max(col_widths[field], len(value))

    # 打印表头
    header = '  '.join([f"{field:^{col_widths[field]}}" for field in fields])
    separator = '-'.join(['-' * col_widths[field] for field in fields])

    print(separator)
    print(header)
    print(separator)

    # 打印数据
    for row in rows:
        line = '  '.join([f"{str(row.get(field, '-')):^{col_widths[field]}}" for field in fields])
        print(line)

    print(separator)
    print(f"总计: {len(results)}只股票")
