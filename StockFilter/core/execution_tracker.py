# -*- coding: utf-8 -*-
"""
执行追踪系统 - 记录和分析因子执行过程

功能：
1. 记录每个因子的执行时间
2. 记录输入输出
3. 识别性能瓶颈
4. 提供详细的执行报告
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import time


class ExecutionStatus(Enum):
    """执行状态"""
    SUCCESS = "success"
    RULE_FAILED = "rule_failed"
    ERROR = "error"


@dataclass
class FactorExecutionRecord:
    """因子执行记录"""
    factor_name: str  # 因子名称
    custom_name: Optional[str] = None  # 自定义名称
    status: ExecutionStatus = ExecutionStatus.SUCCESS  # 执行状态
    execution_time: float = 0.0  # 执行时间（秒）
    input_params: Dict[str, Any] = field(default_factory=dict)  # 输入参数
    output_result: Optional[Dict[str, Any]] = None  # 输出结果
    error_message: Optional[str] = None  # 错误信息
    failed_rules: List[str] = field(default_factory=list)  # 失败的规则

    @property
    def display_name(self) -> str:
        """显示名称"""
        return self.custom_name or self.factor_name


@dataclass
class ExecutionSummary:
    """执行摘要"""
    total_factors: int = 0  # 总因子数
    successful_factors: int = 0  # 成功因子数
    failed_factors: int = 0  # 失败因子数
    total_time: float = 0.0  # 总耗时
    avg_time: float = 0.0  # 平均耗时
    min_time: float = float('inf')  # 最小耗时
    max_time: float = 0.0  # 最大耗时
    slowest_factor: Optional[str] = None  # 最慢的因子
    fastest_factor: Optional[str] = None  # 最快的因子

    def __str__(self) -> str:
        """字符串表示"""
        lines = [
            "="*70,
            "执行摘要",
            "="*70,
            f"总因子数: {self.total_factors}",
            f"成功: {self.successful_factors}",
            f"失败: {self.failed_factors}",
            f"总耗时: {self.total_time:.4f}秒",
            f"平均耗时: {self.avg_time:.4f}秒",
            f"最慢因子: {self.slowest_factor or 'N/A'} ({self.max_time:.4f}秒)",
            f"最快因子: {self.fastest_factor or 'N/A'} ({self.min_time:.4f}秒)",
        ]
        return "\n".join(lines)


class ExecutionTracker:
    """执行追踪器"""

    def __init__(self):
        self.records: List[FactorExecutionRecord] = []
        self._start_time = time.time()

    def start_factor(self, factor_name: str, custom_name: Optional[str] = None,
                    params: Dict[str, Any] = None) -> None:
        """
        开始追踪一个因子

        Args:
            factor_name: 因子名称
            custom_name: 自定义名称
            params: 输入参数
        """
        record = FactorExecutionRecord(
            factor_name=factor_name,
            custom_name=custom_name,
            input_params=params or {}
        )
        record.execution_time = time.time()  # 记录开始时间
        self.records.append(record)

    def end_factor_success(self, output: Dict[str, Any]) -> None:
        """
        标记因子执行成功

        Args:
            output: 输出结果
        """
        if not self.records:
            return

        record = self.records[-1]
        record.status = ExecutionStatus.SUCCESS
        record.output_result = output
        record.execution_time = time.time() - record.execution_time  # 计算耗时

    def end_factor_rule_failed(self, output: Dict[str, Any],
                              failed_rules: List[str]) -> None:
        """
        标记因子规则验证失败

        Args:
            output: 输出结果
            failed_rules: 失败的规则列表
        """
        if not self.records:
            return

        record = self.records[-1]
        record.status = ExecutionStatus.RULE_FAILED
        record.output_result = output
        record.failed_rules = failed_rules
        record.execution_time = time.time() - record.execution_time

    def end_factor_error(self, error: Exception) -> None:
        """
        标记因子执行异常

        Args:
            error: 异常对象
        """
        if not self.records:
            return

        record = self.records[-1]
        record.status = ExecutionStatus.ERROR
        record.error_message = str(error)
        record.execution_time = time.time() - record.execution_time

    def get_summary(self) -> ExecutionSummary:
        """
        获取执行摘要

        Returns:
            ExecutionSummary 对象
        """
        summary = ExecutionSummary()

        if not self.records:
            return summary

        summary.total_factors = len(self.records)
        summary.successful_factors = sum(1 for r in self.records
                                       if r.status == ExecutionStatus.SUCCESS)
        summary.failed_factors = summary.total_factors - summary.successful_factors

        times = [r.execution_time for r in self.records]
        summary.total_time = sum(times)
        summary.avg_time = summary.total_time / len(times) if times else 0.0
        summary.min_time = min(times) if times else 0.0
        summary.max_time = max(times) if times else 0.0

        # 找出最慢和最快的因子
        if self.records:
            slowest = max(self.records, key=lambda r: r.execution_time)
            fastest = min(self.records, key=lambda r: r.execution_time)
            summary.slowest_factor = slowest.display_name
            summary.fastest_factor = fastest.display_name

        return summary

    def find_slow_factors(self, top_n: int = 5) -> List[FactorExecutionRecord]:
        """
        找出最慢的N个因子

        Args:
            top_n: 返回前N个

        Returns:
            最慢的因子列表
        """
        return sorted(self.records, key=lambda r: r.execution_time, reverse=True)[:top_n]

    def find_failed_factors(self) -> List[FactorExecutionRecord]:
        """
        找出失败的因子

        Returns:
            失败的因子列表
        """
        return [r for r in self.records if r.status != ExecutionStatus.SUCCESS]

    def print_report(self, detailed: bool = True):
        """
        打印执行报告

        Args:
            detailed: 是否打印详细信息
        """
        summary = self.get_summary()
        print("\n" + str(summary))

        if detailed:
            print("\n详细执行记录:")
            print("-"*70)

            for i, record in enumerate(self.records, 1):
                status_icon = {
                    ExecutionStatus.SUCCESS: "[OK]",
                    ExecutionStatus.RULE_FAILED: "[FAIL]",
                    ExecutionStatus.ERROR: "[ERROR]",
                }.get(record.status, "[?]")

                print(f"\n{i}. {record.display_name} {status_icon}")
                print(f"   耗时: {record.execution_time:.6f}秒")

                if record.input_params:
                    # 只显示关键参数
                    key_params = {k: v for k, v in record.input_params.items()
                               if k in ['n', 'segments', 'agitation_threshold'] and v is not None}
                    if key_params:
                        print(f"   参数: {key_params}")

                if record.output_result:
                    # 显示结果值
                    for key, value in record.output_result.items():
                        if isinstance(value, float):
                            print(f"   {key}: {value:.6f}")
                        else:
                            print(f"   {key}: {value}")

                if record.failed_rules:
                    print(f"   失败规则:")
                    for rule in record.failed_rules:
                        print(f"     - {rule}")

                if record.error_message:
                    print(f"   错误: {record.error_message}")

            # 性能分析
            slow_factors = self.find_slow_factors(3)
            if slow_factors and summary.total_time > 0:
                print("\n" + "="*70)
                print("性能分析 - 最慢的3个因子:")
                print("-"*70)
                for i, record in enumerate(slow_factors, 1):
                    pct = record.execution_time / summary.total_time * 100
                    print(f"{i}. {record.display_name}: {record.execution_time:.6f}秒 ({pct:.1f}%)")

        print("\n" + "="*70)


# ==================== 集成到 StockFilter ====================

def run_with_tracking(
    data: Dict[str, List],
    chain: List,
    tracker: Optional[ExecutionTracker] = None,
    print_report: bool = False
) -> Dict[str, Any]:
    """
    带执行追踪的运行函数

    Args:
        data: OHLCV 格式数据
        chain: 因子链
        tracker: 执行追踪器（如果为 None，则创建默认的）
        print_report: 是否打印报告

    Returns:
        包含 pass、details、tracker 的结果字典
    """
    from stock_filter import pass_filter

    if tracker is None:
        tracker = ExecutionTracker()

    details = {}
    ok = True
    func_count = {}

    for item in chain:
        # 解包 FactorConf
        if len(item) == 4:
            func, params, rules, custom_name = item
        else:
            func, params, rules = item
            custom_name = None

        # 获取函数名
        func_name = func.__name__[1:] if func.__name__.startswith('_') else func.__name__

        # 开始追踪
        tracker.start_factor(func_name, custom_name, params)

        try:
            # 执行因子计算
            params['detail'] = details
            result = func(data, **params)

            # 验证规则
            if not pass_filter(result, rules):
                # 规则验证失败
                failed_rules = [r for r in rules if not eval(r, {}, result)]
                tracker.end_factor_rule_failed(result, failed_rules)
                ok = False
                break
            else:
                # 成功
                tracker.end_factor_success(result)

                # 保存结果到 details
                if custom_name is not None:
                    key = custom_name
                else:
                    # 使用自动序号逻辑
                    func_count[func_name] = func_count.get(func_name, 0) + 1
                    count = func_count[func_name]

                    if count == 1:
                        key = func_name
                    else:
                        if count == 2:
                            old_key = func_name
                            new_key = f"{func_name}1"
                            if old_key in details:
                                details[new_key] = details.pop(old_key)
                        key = f"{func_name}{count}"

                details[key] = result

        except Exception as e:
            # 捕获执行异常
            tracker.end_factor_error(e)
            ok = False
            break

    # 打印报告
    if print_report:
        tracker.print_report(detailed=True)

    return {
        "pass": ok,
        "details": details,
        "tracker": tracker
    }


# ==================== 测试 ====================

if __name__ == "__main__":
    """测试执行追踪系统"""
    print("测试执行追踪系统\n")

    from stock_filter import Config
    from basic_statistics_factors import BasicStatistics

    # 创建测试数据
    test_data = {
        'open': [10.0, 10.2, 10.5, 10.3, 10.8, 11.0, 10.9, 11.2, 11.5, 11.3,
                 11.8, 12.0, 11.7, 12.2, 12.5, 12.3, 12.8, 13.0, 12.7, 13.2],
        'high': [10.5, 10.8, 11.0, 10.9, 11.2, 11.5, 11.3, 11.8, 12.0, 11.9,
                 12.2, 12.5, 12.3, 12.8, 13.0, 12.9, 13.2, 13.5, 13.1, 13.8],
        'low': [9.5, 9.8, 10.0, 10.1, 10.5, 10.7, 10.6, 10.9, 11.1, 11.0,
                11.5, 11.6, 11.4, 11.9, 12.1, 12.0, 12.4, 12.6, 12.3, 12.9],
        'close': [10.0, 10.5, 10.8, 10.6, 11.0, 11.2, 11.0, 11.5, 11.8, 11.6,
                  12.0, 12.2, 12.0, 12.5, 12.8, 12.5, 13.0, 13.2, 12.9, 13.5],
        'volume': [10000, 11000, 12000, 11500, 13000, 14000, 12500, 15000, 16000, 14500,
                   17000, 18000, 16500, 19000, 20000, 18500, 21000, 22000, 20500, 23000],
        'yd_close': [9.5, 10.0, 10.5, 10.8, 10.6, 11.0, 11.2, 11.0, 11.5, 11.8,
                     11.6, 12.0, 12.2, 12.0, 12.5, 12.8, 12.5, 13.0, 13.2, 12.9]
    }

    print("="*70)
    print("测试1: 正常执行")
    print("="*70)

    tracker1 = ExecutionTracker()

    result1 = run_with_tracking(
        test_data,
        [
            BasicStatistics.level_relative(n=10, name='level_10'),
            BasicStatistics.level_relative(n=20, name='level_20'),
            BasicStatistics.return_total(n=20, name='return_20'),
            BasicStatistics.trend_direction(name='trend'),
        ],
        tracker=tracker1,
        print_report=True
    )

    print("\n" + "="*70)
    print("测试2: 规则失败")
    print("="*70)

    tracker2 = ExecutionTracker()

    result2 = run_with_tracking(
        test_data,
        [
            BasicStatistics.level_relative(
                n=20,
                rules=("res > 0.95",),  # 这个会失败
                name='high_level'
            ),
            BasicStatistics.return_total(n=20, name='return_20'),
        ],
        tracker=tracker2,
        print_report=True
    )

    print("\n测试完成！")
