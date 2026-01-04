# -*- coding: utf-8 -*-
"""
数据验证系统 - 确保 StockFilter 输入数据质量

功能：
1. 检查必需字段（open, high, low, close, volume）
2. 检查数据长度是否满足因子需求
3. 检测缺失值、异常值
4. 提供数据清洗功能
"""
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ValidationLevel(Enum):
    """验证级别"""
    STRICT = "strict"  # 严格模式：验证失败则抛异常
    WARNING = "warning"  # 警告模式：只记录警告，不抛异常
    NONE = "none"  # 不验证


class CleaningMethod(Enum):
    """数据清洗方法"""
    FFILL = "ffill"  # 前向填充
    BFILL = "bfill"  # 后向填充
    DROP = "drop"  # 删除缺失值
    MEAN = "mean"  # 均值填充
    MEDIAN = "median"  # 中位数填充


@dataclass
class ValidationIssue:
    """验证问题"""
    level: str  # ERROR 或 WARNING
    field: str  # 字段名
    message: str  # 问题描述
    location: Optional[int] = None  # 位置索引（如果有）


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool  # 是否有效
    issues: List[ValidationIssue]  # 问题列表
    stats: Dict[str, Any]  # 统计信息

    def get_errors(self) -> List[ValidationIssue]:
        """获取所有错误"""
        return [issue for issue in self.issues if issue.level == "ERROR"]

    def get_warnings(self) -> List[ValidationIssue]:
        """获取所有警告"""
        return [issue for issue in self.issues if issue.level == "WARNING"]

    def print_summary(self):
        """打印摘要"""
        errors = self.get_errors()
        warnings = self.get_warnings()

        print("\n" + "="*70)
        print("数据验证报告")
        print("="*70)
        print(f"验证结果: {'[OK] 通过' if self.is_valid else '[FAIL] 失败'}")
        print(f"错误数: {len(errors)}")
        print(f"警告数: {len(warnings)}")

        if errors:
            print("\n错误详情:")
            for i, error in enumerate(errors, 1):
                loc = f"[位置{error.location}]" if error.location is not None else ""
                print(f"  {i}. {error.field}{loc}: {error.message}")

        if warnings:
            print("\n警告详情:")
            for i, warning in enumerate(warnings, 1):
                loc = f"[位置{warning.location}]" if warning.location is not None else ""
                print(f"  {i}. {warning.field}{loc}: {warning.message}")

        print("\n统计信息:")
        for key, value in self.stats.items():
            print(f"  {key}: {value}")

        print("="*70 + "\n")


class DataValidator:
    """数据验证器"""

    # 必需字段
    REQUIRED_FIELDS = ['open', 'high', 'low', 'close', 'volume']
    # 可选字段
    OPTIONAL_FIELDS = ['yd_close']

    def __init__(self, level: ValidationLevel = ValidationLevel.WARNING):
        """
        初始化验证器

        Args:
            level: 验证级别
        """
        self.level = level

    def validate(self,
                data: Dict[str, List],
                required_length: Optional[int] = None) -> ValidationResult:
        """
        验证数据

        Args:
            data: OHLCV 格式数据
            required_length: 所需的最小数据长度

        Returns:
            ValidationResult 对象
        """
        issues = []
        stats = {}

        # 1. 检查必需字段
        for field in self.REQUIRED_FIELDS:
            if field not in data:
                issues.append(ValidationIssue(
                    level="ERROR",
                    field=field,
                    message=f"缺少必需字段"
                ))

        # 如果缺少必需字段，直接返回
        if any(issue.level == "ERROR" and "缺少必需字段" in issue.message
               for issue in issues):
            return ValidationResult(
                is_valid=False,
                issues=issues,
                stats=stats
            )

        # 2. 检查数据长度
        data_length = len(data.get('close', []))
        stats['data_length'] = data_length

        if required_length and data_length < required_length:
            issues.append(ValidationIssue(
                level="ERROR",
                field="close",
                message=f"数据长度不足: {data_length} < {required_length}"
            ))

        # 3. 检查字段长度一致性
        for field in self.REQUIRED_FIELDS:
            if field in data:
                field_length = len(data[field])
                if field_length != data_length:
                    issues.append(ValidationIssue(
                        level="ERROR",
                        field=field,
                        message=f"字段长度不一致: {field_length} != {data_length}"
                    ))

        # 4. 检查缺失值
        null_counts = {}
        for field in self.REQUIRED_FIELDS:
            if field in data:
                null_count = sum(1 for v in data[field] if v is None)
                null_counts[field] = null_count
                if null_count > 0:
                    null_pct = null_count / len(data[field]) * 100
                    issues.append(ValidationIssue(
                        level="WARNING",
                        field=field,
                        message=f"包含 {null_count} 个缺失值 ({null_pct:.1f}%)"
                    ))

        stats['null_counts'] = null_counts

        # 5. 检查异常值
        for field in ['open', 'high', 'low', 'close']:
            if field in data:
                values = [v for v in data[field] if v is not None]
                if values:
                    # 检查负数
                    neg_count = sum(1 for v in values if v < 0)
                    if neg_count > 0:
                        issues.append(ValidationIssue(
                            level="ERROR",
                            field=field,
                            message=f"包含 {neg_count} 个负数值"
                        ))

                    # 检查零值
                    zero_count = sum(1 for v in values if v == 0)
                    if zero_count > 0:
                        issues.append(ValidationIssue(
                            level="WARNING",
                            field=field,
                            message=f"包含 {zero_count} 个零值"
                        ))

                    # 检查极端异常值（偏离均值10倍）
                    avg = sum(values) / len(values)
                    outliers = [(i, v) for i, v in enumerate(data[field])
                              if v is not None and v != 0 and abs(v - avg) > avg * 10]
                    if outliers:
                        for idx, val in outliers[:5]:  # 只报告前5个
                            issues.append(ValidationIssue(
                                level="WARNING",
                                field=field,
                                message=f"可能的异常值: {val} (偏离均值10倍)",
                                location=idx
                            ))

        # 6. 检查价格逻辑（high >= low, high >= open, close 等）
        if all(f in data for f in ['open', 'high', 'low', 'close']):
            for i in range(min(len(data['high']), len(data['low']))):
                high = data['high'][i]
                low = data['low'][i]

                if high is not None and low is not None:
                    if high < low:
                        issues.append(ValidationIssue(
                            level="ERROR",
                            field="high/low",
                            message=f"最高价 < 最低价: {high} < {low}",
                            location=i
                        ))

        # 7. 统计信息
        if 'close' in data:
            closes = [c for c in data['close'] if c is not None]
            if closes:
                stats['close_mean'] = sum(closes) / len(closes)
                stats['close_min'] = min(closes)
                stats['close_max'] = max(closes)

        # 判断是否有效
        is_valid = len(self.get_errors(issues)) == 0

        # 根据验证级别决定是否抛异常
        if not is_valid and self.level == ValidationLevel.STRICT:
            error_msg = "数据验证失败:\n" + "\n".join(
                f"  - {e.field}: {e.message}" for e in self.get_errors(issues)
            )
            raise ValueError(error_msg)

        return ValidationResult(
            is_valid=is_valid,
            issues=issues,
            stats=stats
        )

    def get_errors(self, issues: List[ValidationIssue]) -> List[ValidationIssue]:
        """获取错误列表"""
        return [issue for issue in issues if issue.level == "ERROR"]

    def clean(self,
             data: Dict[str, List],
             method: CleaningMethod = CleaningMethod.FFILL) -> Dict[str, List]:
        """
        清洗数据

        Args:
            data: 原始数据
            method: 清洗方法

        Returns:
            清洗后的数据
        """
        import copy
        cleaned = copy.deepcopy(data)

        if method == CleaningMethod.FFILL:
            # 前向填充
            for field in ['open', 'high', 'low', 'close', 'volume']:
                if field in cleaned:
                    last_valid = None
                    for i, val in enumerate(cleaned[field]):
                        if val is not None:
                            last_valid = val
                        else:
                            cleaned[field][i] = last_valid

        elif method == CleaningMethod.BFILL:
            # 后向填充
            for field in ['open', 'high', 'low', 'close', 'volume']:
                if field in cleaned:
                    next_valid = None
                    for i in range(len(cleaned[field]) - 1, -1, -1):
                        if cleaned[field][i] is not None:
                            next_valid = cleaned[field][i]
                        else:
                            cleaned[field][i] = next_valid

        elif method == CleaningMethod.MEAN:
            # 均值填充
            for field in ['open', 'high', 'low', 'close', 'volume']:
                if field in cleaned:
                    values = [v for v in cleaned[field] if v is not None]
                    if values:
                        mean_val = sum(values) / len(values)
                        for i, val in enumerate(cleaned[field]):
                            if val is None:
                                cleaned[field][i] = mean_val

        elif method == CleaningMethod.MEDIAN:
            # 中位数填充
            for field in ['open', 'high', 'low', 'close', 'volume']:
                if field in cleaned:
                    values = sorted([v for v in cleaned[field] if v is not None])
                    if values:
                        median_val = values[len(values) // 2]
                        for i, val in enumerate(cleaned[field]):
                            if val is None:
                                cleaned[field][i] = median_val

        elif method == CleaningMethod.DROP:
            # 删除包含缺失值的行
            valid_indices = []
            for i in range(len(cleaned.get('close', []))):
                if all(cleaned.get(f, [None] * len(cleaned['close']))[i] is not None
                       for f in ['open', 'high', 'low', 'close', 'volume']):
                    valid_indices.append(i)

            # 只保留有效索引
            for field in ['open', 'high', 'low', 'close', 'volume']:
                if field in cleaned:
                    cleaned[field] = [cleaned[field][i] for i in valid_indices]

        return cleaned


# ==================== 集成到 StockFilter ====================

def validate_and_clean_data(
    data: Dict[str, List],
    required_length: Optional[int] = None,
    validation_level: ValidationLevel = ValidationLevel.WARNING,
    cleaning_method: Optional[CleaningMethod] = None,
    print_report: bool = True
) -> Tuple[Dict[str, List], ValidationResult]:
    """
    验证和清洗数据

    Args:
        data: 原始数据
        required_length: 所需的最小数据长度
        validation_level: 验证级别
        cleaning_method: 清洗方法（如果为 None，则不清洗）
        print_report: 是否打印报告

    Returns:
        (清洗后的数据, 验证结果)
    """
    validator = DataValidator(level=validation_level)

    # 验证数据
    result = validator.validate(data, required_length)

    if print_report:
        result.print_summary()

    # 清洗数据
    cleaned_data = data
    if cleaning_method is not None and not result.is_valid:
        print(f"\n使用 {cleaning_method.value} 方法清洗数据...")
        cleaned_data = validator.clean(data, method=cleaning_method)

        # 重新验证
        result_after = validator.validate(cleaned_data, required_length)
        if print_report:
            print("\n清洗后的验证结果:")
            result_after.print_summary()

        return cleaned_data, result_after

    return cleaned_data, result


# ==================== 测试 ====================

if __name__ == "__main__":
    """测试数据验证系统"""
    print("测试数据验证系统\n")

    # 测试数据1: 正常数据
    print("="*70)
    print("测试1: 正常数据")
    print("="*70)

    normal_data = {
        'open': [10.0, 10.2, 10.5, 10.3, 10.8],
        'high': [10.5, 10.8, 11.0, 10.9, 11.2],
        'low': [9.5, 9.8, 10.0, 10.1, 10.5],
        'close': [10.0, 10.5, 10.8, 10.6, 11.0],
        'volume': [10000, 11000, 12000, 11500, 13000],
    }

    validator = DataValidator(level=ValidationLevel.WARNING)
    result1 = validator.validate(normal_data, required_length=5)
    result1.print_summary()

    # 测试数据2: 包含缺失值
    print("\n" + "="*70)
    print("测试2: 包含缺失值")
    print("="*70)

    data_with_nulls = {
        'open': [10.0, None, 10.5, 10.3, 10.8],
        'high': [10.5, 10.8, None, 10.9, 11.2],
        'low': [9.5, 9.8, 10.0, None, 10.5],
        'close': [10.0, 10.5, 10.8, 10.6, None],
        'volume': [10000, 11000, 12000, 11500, 13000],
    }

    result2 = validator.validate(data_with_nulls)
    result2.print_summary()

    # 清洗数据
    print("\n清洗数据（前向填充）:")
    cleaned_data = validator.clean(data_with_nulls, method=CleaningMethod.FFILL)
    result2_cleaned = validator.validate(cleaned_data)
    result2_cleaned.print_summary()

    # 测试数据3: 包含异常值
    print("\n" + "="*70)
    print("测试3: 包含异常值")
    print("="*70)

    data_with_outliers = {
        'open': [10.0, 10.2, 10.5, 10.3, 100.0],  # 异常值
        'high': [10.5, 10.8, 11.0, 10.9, 11.2],
        'low': [9.5, 9.8, 10.0, 10.1, 10.5],
        'close': [10.0, 10.5, 10.8, -5.0, 11.0],  # 负数
        'volume': [10000, 11000, 12000, 11500, 13000],
    }

    result3 = validator.validate(data_with_outliers)
    result3.print_summary()

    # 测试数据4: 缺少字段
    print("\n" + "="*70)
    print("测试4: 缺少必需字段")
    print("="*70)

    incomplete_data = {
        'open': [10.0, 10.2, 10.5],
        'high': [10.5, 10.8, 11.0],
        # 缺少 low, close
        'volume': [10000, 11000, 12000],
    }

    try:
        result4 = validator.validate(incomplete_data, required_length=5)
        result4.print_summary()
    except ValueError as e:
        print(f"\n捕获到预期异常:\n{e}")

    print("\n测试完成！")
