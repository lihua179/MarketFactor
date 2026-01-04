# -*- coding: utf-8 -*-
"""
错误处理增强系统 - 为 StockFilter 提供详细的错误诊断

功能：
1. 详细的执行报告（哪个因子失败、哪个规则失败）
2. 失败诊断（实际值 vs 期望值）
3. 异常捕获和堆栈跟踪
4. 不同日志级别支持
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import traceback


class LogLevel(Enum):
    """日志级别"""
    ERROR = "ERROR"
    WARN = "WARN"
    INFO = "INFO"
    DEBUG = "DEBUG"


@dataclass
class FactorExecutionRecord:
    """因子执行记录"""
    factor_name: str  # 因子名称
    custom_name: Optional[str] = None  # 自定义名称
    passed: bool = True  # 是否通过
    error: Optional[str] = None  # 错误信息
    traceback: Optional[str] = None  # 堆栈跟踪
    failed_rules: List[str] = field(default_factory=list)  # 失败的规则
    result: Optional[Dict[str, Any]] = None  # 计算结果

    @property
    def display_name(self) -> str:
        """显示名称"""
        return self.custom_name or self.factor_name


@dataclass
class ExecutionReport:
    """执行报告"""
    overall_passed: bool  # 总体是否通过
    records: List[FactorExecutionRecord] = field(default_factory=list)  # 执行记录
    total_execution_time: float = 0.0  # 总执行时间

    def add_record(self, record: FactorExecutionRecord):
        """添加记录"""
        self.records.append(record)

    def get_failed_record(self) -> Optional[FactorExecutionRecord]:
        """获取失败的记录（第一个失败的）"""
        for record in self.records:
            if not record.passed:
                return record
        return None

    def get_summary(self) -> str:
        """获取摘要信息"""
        total = len(self.records)
        passed = sum(1 for r in self.records if r.passed)
        failed = total - passed

        lines = [
            "="*70,
            "执行摘要",
            "="*70,
            f"总体结果: {'[OK] 通过' if self.overall_passed else '[FAIL] 失败'}",
            f"执行因子数: {total}",
            f"通过: {passed}",
            f"失败: {failed}",
            f"总耗时: {self.total_execution_time:.4f}秒",
        ]
        return "\n".join(lines)

    def get_detailed_report(self) -> str:
        """获取详细报告"""
        lines = [self.get_summary(), "", "详细执行记录:", "-"*70]

        for i, record in enumerate(self.records, 1):
            lines.append(f"\n{i}. {record.display_name}")

            if record.passed:
                lines.append(f"   状态: [OK] 通过")
                if record.result:
                    # 显示结果值
                    for key, value in record.result.items():
                        if isinstance(value, float):
                            lines.append(f"   {key}: {value:.6f}")
                        else:
                            lines.append(f"   {key}: {value}")
            else:
                lines.append(f"   状态: [FAIL] 失败")

                if record.error:
                    lines.append(f"   错误: {record.error}")

                if record.failed_rules:
                    lines.append(f"   失败规则:")
                    for rule in record.failed_rules:
                        lines.append(f"     - {rule}")

                if record.traceback:
                    lines.append(f"   堆栈跟踪:")
                    for line in record.traceback.split('\n')[:10]:  # 只显示前10行
                        lines.append(f"     {line}")

        lines.append("\n" + "="*70)
        return "\n".join(lines)


class FailureDiagnosis:
    """失败诊断器"""

    @staticmethod
    def diagnose_rule_failure(rule: str, context: Dict[str, Any]) -> str:
        """
        诊断规则失败原因

        Args:
            rule: 失败的规则
            context: 执行上下文（包含变量值）

        Returns:
            诊断信息字符串
        """
        import re

        # 提取字段名
        field = FailureDiagnosis._extract_field(rule)
        actual_value = context.get(field, 'N/A')

        # 提取期望值
        expected = FailureDiagnosis._extract_expected(rule)

        # 构建诊断信息
        lines = [
            f"规则: {rule}",
            f"字段名: {field}",
            f"实际值: {actual_value} ({type(actual_value).__name__})",
            f"期望: {expected}",
        ]

        # 额外的分析
        if isinstance(actual_value, (int, float)):
            if '>' in rule and actual_value is not None:
                threshold = FailureDiagnosis._extract_number(rule)
                if threshold is not None:
                    diff = actual_value - threshold
                    lines.append(f"差值: {diff:.6f} (实际值 - 阈值)")

        return "\n  ".join(lines)

    @staticmethod
    def _extract_field(rule: str) -> str:
        """从规则中提取字段名"""
        import re
        # 匹配变量名（字母开头，包含字母、数字、下划线）
        match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*[<>=!]', rule)
        return match.group(1) if match else 'unknown'

    @staticmethod
    def _extract_expected(rule: str) -> str:
        """从规则中提取期望条件"""
        import re
        # 匹配比较操作符和右边的值
        match = re.search(r'([<>=!]+)\s*(.+)', rule)
        if match:
            op, value = match.groups()
            return f"{op} {value.strip()}"
        return "unknown"

    @staticmethod
    def _extract_number(rule: str) -> Optional[float]:
        """从规则中提取数字"""
        import re
        # 匹配数字（包括小数和负数）
        match = re.search(r'[-+]?\d*\.?\d+', rule)
        if match:
            return float(match.group())
        return None


class ErrorHandler:
    """错误处理器"""

    def __init__(self, log_level: LogLevel = LogLevel.INFO):
        self.log_level = log_level
        self.report = ExecutionReport(overall_passed=True)

    def handle_factor_success(self, factor_name: str, custom_name: Optional[str],
                            result: Dict[str, Any]):
        """处理因子执行成功"""
        record = FactorExecutionRecord(
            factor_name=factor_name,
            custom_name=custom_name,
            passed=True,
            result=result
        )
        self.report.add_record(record)
        self._log(LogLevel.DEBUG, f"因子 {factor_name} 执行成功")

    def handle_factor_failure_by_rule(self, factor_name: str, custom_name: Optional[str],
                                     result: Dict[str, Any], failed_rules: List[str]):
        """处理因子因规则未通过而失败"""
        record = FactorExecutionRecord(
            factor_name=factor_name,
            custom_name=custom_name,
            passed=False,
            failed_rules=failed_rules,
            result=result
        )

        # 生成诊断信息
        diagnoses = []
        for rule in failed_rules:
            diagnosis = FailureDiagnosis.diagnose_rule_failure(rule, result)
            diagnoses.append(diagnosis)

        record.error = "规则验证失败:\n" + "\n".join(diagnoses)
        self.report.add_record(record)
        self.report.overall_passed = False

        self._log(LogLevel.ERROR, f"因子 {factor_name} 规则验证失败")

    def handle_factor_error(self, factor_name: str, custom_name: Optional[str],
                           error: Exception):
        """处理因子执行异常"""
        record = FactorExecutionRecord(
            factor_name=factor_name,
            custom_name=custom_name,
            passed=False,
            error=str(error),
            traceback=traceback.format_exc()
        )
        self.report.add_record(record)
        self.report.overall_passed = False

        self._log(LogLevel.ERROR, f"因子 {factor_name} 执行异常: {error}")

    def set_execution_time(self, time: float):
        """设置总执行时间"""
        self.report.total_execution_time = time

    def get_report(self) -> ExecutionReport:
        """获取执行报告"""
        return self.report

    def print_report(self, detailed: bool = True):
        """打印报告"""
        if detailed:
            print(self.report.get_detailed_report())
        else:
            print(self.report.get_summary())

    def _log(self, level: LogLevel, message: str):
        """记录日志"""
        # 简单的日志级别过滤
        level_order = {
            LogLevel.DEBUG: 0,
            LogLevel.INFO: 1,
            LogLevel.WARN: 2,
            LogLevel.ERROR: 3,
        }

        if level_order[level] >= level_order[self.log_level]:
            prefix = f"[{level.value}]"
            print(f"{prefix} {message}")


# ==================== 增强版运行函数 ====================

def run_one_with_error_handling(
    data: Dict[str, List],
    chain: List,
    error_handler: Optional[ErrorHandler] = None,
    print_report: bool = False
) -> Dict[str, Any]:
    """
    增强版运行函数 - 支持详细的错误处理

    Args:
        data: OHLCV 格式数据
        chain: 因子链
        error_handler: 错误处理器（如果为 None，则创建默认的）
        print_report: 是否打印详细报告

    Returns:
        包含 pass、details 和 report 的结果字典
    """
    import time
    from stock_filter import pass_filter

    if error_handler is None:
        error_handler = ErrorHandler(log_level=LogLevel.INFO)

    details = {}
    ok = True
    func_count = {}
    start_time = time.time()

    try:
        for item in chain:
            # 解包 FactorConf
            if len(item) == 4:
                func, params, rules, custom_name = item
            else:
                func, params, rules = item
                custom_name = None

            # 获取函数名
            func_name = func.__name__[1:] if func.__name__.startswith('_') else func.__name__

            try:
                # 执行因子计算
                params['detail'] = details
                result = func(data, **params)

                # 验证规则
                if not pass_filter(result, rules):
                    # 规则验证失败
                    failed_rules = [r for r in rules if not eval(r, {}, result)]
                    error_handler.handle_factor_failure_by_rule(
                        factor_name=func_name,
                        custom_name=custom_name,
                        result=result,
                        failed_rules=failed_rules
                    )
                    ok = False
                    break
                else:
                    # 成功
                    error_handler.handle_factor_success(
                        factor_name=func_name,
                        custom_name=custom_name,
                        result=result
                    )

                    # 保存结果到 details
                    if custom_name is not None:
                        key = custom_name
                    else:
                        # 使用自动序号逻辑（与原版一致）
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
                error_handler.handle_factor_error(
                    factor_name=func_name,
                    custom_name=custom_name,
                    error=e
                )
                ok = False
                break

    except Exception as e:
        # 捕获全局异常
        error_handler.handle_factor_error(
            factor_name="SYSTEM",
            custom_name=None,
            error=e
        )
        ok = False

    # 设置执行时间
    execution_time = time.time() - start_time
    error_handler.set_execution_time(execution_time)

    # 打印报告
    if print_report:
        error_handler.print_report(detailed=True)

    # 返回结果（包含报告）
    return {
        "pass": ok,
        "details": details,
        "report": error_handler.get_report()
    }


# ==================== 便捷函数 ====================

def create_error_handler(log_level: LogLevel = LogLevel.INFO) -> ErrorHandler:
    """创建错误处理器"""
    return ErrorHandler(log_level=log_level)


def print_diagnostics(report: ExecutionReport):
    """打印诊断信息"""
    failed_record = report.get_failed_record()
    if failed_record:
        print("\n" + "="*70)
        print("失败诊断")
        print("="*70)
        print(f"\n失败的因子: {failed_record.display_name}")

        if failed_record.error:
            print(f"\n错误信息:")
            print(failed_record.error)

        if failed_record.failed_rules:
            print(f"\n失败的规则数: {len(failed_record.failed_rules)}")
            print("\n详细诊断:")
            for i, rule in enumerate(failed_record.failed_rules, 1):
                print(f"\n规则 {i}:")
                diagnosis = FailureDiagnosis.diagnose_rule_failure(
                    rule,
                    failed_record.result or {}
                )
                for line in diagnosis.split('\n'):
                    print(f"  {line}")
    else:
        print("\n所有因子执行成功 [OK]")


if __name__ == "__main__":
    """测试错误处理系统"""
    print("测试错误处理增强系统\n")

    from stock_filter import Config
    from basic_statistics_factors import BasicStatistics

    # 创建测试数据
    test_data = {
        'open': [10.0, 10.2, 10.5, 10.3, 10.8],
        'high': [10.5, 10.8, 11.0, 10.9, 11.2],
        'low': [9.5, 9.8, 10.0, 10.1, 10.5],
        'close': [10.0, 10.5, 10.8, 10.6, 11.0],
        'volume': [10000, 11000, 12000, 11500, 13000],
        'yd_close': [9.5, 10.0, 10.5, 10.8, 10.6]
    }

    # 测试场景1: 规则失败
    print("="*70)
    print("测试场景1: 规则验证失败")
    print("="*70)

    result = run_one_with_error_handling(
        test_data,
        [
            BasicStatistics.level_relative(
                n=5,
                rules=("res > 0.95",),  # 这个规则会失败
                name='high_level'
            ),
        ],
        print_report=True
    )

    print_diagnostics(result['report'])

    # 测试场景2: 成功场景
    print("\n\n" + "="*70)
    print("测试场景2: 执行成功")
    print("="*70)

    result2 = run_one_with_error_handling(
        test_data,
        [
            BasicStatistics.level_relative(
                n=5,
                rules=("res >= 0",),
                name='level'
            ),
        ],
        print_report=True
    )

    print("\n测试完成！")
