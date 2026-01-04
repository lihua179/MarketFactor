# -*- coding: utf-8 -*-
"""
规则构建器 - 提供类型安全的规则构建 API

功能：
1. 面向对象的规则构建
2. 支持链式调用
3. 支持 AND/OR/NOT 逻辑组合
4. 编译为高效的函数对象
5. 与字符串规则兼容
"""
from typing import Dict, Any, Callable, List, Union, Optional
from abc import ABC, abstractmethod
import operator


# ==================== 规则基类 ====================

class Rule(ABC):
    """规则基类"""

    @abstractmethod
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """
        评估规则

        Args:
            context: 上下文变量字典

        Returns:
            布尔值
        """
        pass

    def and_(self, other: 'Rule') -> 'AndRule':
        """逻辑与"""
        return AndRule(self, other)

    def or_(self, other: 'Rule') -> 'OrRule':
        """逻辑或"""
        return OrRule(self, other)

    def not_(self) -> 'NotRule':
        """逻辑非"""
        return NotRule(self)

    def __and__(self, other: 'Rule') -> 'AndRule':
        """重载 & 操作符"""
        return AndRule(self, other)

    def __or__(self, other: 'Rule') -> 'OrRule':
        """重载 | 操作符"""
        return OrRule(self, other)

    def __invert__(self) -> 'NotRule':
        """重载 ~ 操作符"""
        return NotRule(self)

    def compile(self) -> Callable[[Dict[str, Any]], bool]:
        """
        编译为函数

        Returns:
            可调用对象
        """
        return lambda ctx: self.evaluate(ctx)

    def to_string_rule(self) -> str:
        """
        转换为字符串规则（用于兼容）

        Returns:
            规则字符串
        """
        return str(self)


# ==================== 比较规则 ====================

class ComparisonRule(Rule):
    """比较规则基类"""

    def __init__(self, field: str, value: Any, op: Callable[[Any, Any], bool], op_name: str):
        self.field = field
        self.value = value
        self.op = op
        self.op_name = op_name

    def evaluate(self, context: Dict[str, Any]) -> bool:
        """评估比较规则"""
        if self.field not in context:
            return False
        return self.op(context[self.field], self.value)

    def __str__(self) -> str:
        """字符串表示"""
        return f"{self.field} {self.op_name} {self._format_value()}"

    def _format_value(self) -> str:
        """格式化值"""
        if isinstance(self.value, str):
            return f"'{self.value}'"
        return str(self.value)


class GreaterThan(ComparisonRule):
    """大于规则"""

    def __init__(self, field: str, value: Any):
        super().__init__(field, value, operator.gt, ">")


class GreaterThanOrEqual(ComparisonRule):
    """大于等于规则"""

    def __init__(self, field: str, value: Any):
        super().__init__(field, value, operator.ge, ">=")


class LessThan(ComparisonRule):
    """小于规则"""

    def __init__(self, field: str, value: Any):
        super().__init__(field, value, operator.lt, "<")


class LessThanOrEqual(ComparisonRule):
    """小于等于规则"""

    def __init__(self, field: str, value: Any):
        super().__init__(field, value, operator.le, "<=")


class Equal(ComparisonRule):
    """等于规则"""

    def __init__(self, field: str, value: Any):
        super().__init__(field, value, operator.eq, "==")


class NotEqual(ComparisonRule):
    """不等于规则"""

    def __init__(self, field: str, value: Any):
        super().__init__(field, value, operator.ne, "!=")


# ==================== 范围规则 ====================

class BetweenRule(Rule):
    """范围规则（值在两个数之间）"""

    def __init__(self, field: str, min_value: Any, max_value: Any, inclusive: bool = True):
        self.field = field
        self.min_value = min_value
        self.max_value = max_value
        self.inclusive = inclusive

    def evaluate(self, context: Dict[str, Any]) -> bool:
        """评估范围规则"""
        if self.field not in context:
            return False
        value = context[self.field]

        if self.inclusive:
            return self.min_value <= value <= self.max_value
        else:
            return self.min_value < value < self.max_value

    def __str__(self) -> str:
        """字符串表示"""
        if self.inclusive:
            return f"{self.min_value} <= {self.field} <= {self.max_value}"
        else:
            return f"{self.min_value} < {self.field} < {self.max_value}"


class InRule(Rule):
    """成员规则（值在列表中）"""

    def __init__(self, field: str, values: List[Any]):
        self.field = field
        self.values = values

    def evaluate(self, context: Dict[str, Any]) -> bool:
        """评估成员规则"""
        if self.field not in context:
            return False
        return context[self.field] in self.values

    def __str__(self) -> str:
        """字符串表示"""
        values_str = ", ".join(repr(v) for v in self.values)
        return f"{self.field} in [{values_str}]"


# ==================== 逻辑组合规则 ====================

class AndRule(Rule):
    """逻辑与规则"""

    def __init__(self, *rules: Rule):
        self.rules = rules

    def evaluate(self, context: Dict[str, Any]) -> bool:
        """评估逻辑与"""
        return all(rule.evaluate(context) for rule in self.rules)

    def __str__(self) -> str:
        """字符串表示"""
        inner = " and ".join(f"({r})" if isinstance(r, (OrRule, NotRule)) else str(r)
                            for r in self.rules)
        return f"({inner})"


class OrRule(Rule):
    """逻辑或规则"""

    def __init__(self, *rules: Rule):
        self.rules = rules

    def evaluate(self, context: Dict[str, Any]) -> bool:
        """评估逻辑或"""
        return any(rule.evaluate(context) for rule in self.rules)

    def __str__(self) -> str:
        """字符串表示"""
        inner = " or ".join(f"({r})" if isinstance(r, AndRule) else str(r)
                            for r in self.rules)
        return f"({inner})"


class NotRule(Rule):
    """逻辑非规则"""

    def __init__(self, rule: Rule):
        self.rule = rule

    def evaluate(self, context: Dict[str, Any]) -> bool:
        """评估逻辑非"""
        return not self.rule.evaluate(context)

    def __str__(self) -> str:
        """字符串表示"""
        return f"(not {self.rule})"


# ==================== 字段引用 ====================

class Field:
    """字段引用类 - 用于构建规则的便捷语法"""

    def __init__(self, name: str):
        self.name = name

    def __gt__(self, value: Any) -> ComparisonRule:
        """大于"""
        return GreaterThan(self.name, value)

    def __ge__(self, value: Any) -> ComparisonRule:
        """大于等于"""
        return GreaterThanOrEqual(self.name, value)

    def __lt__(self, value: Any) -> ComparisonRule:
        """小于"""
        return LessThan(self.name, value)

    def __le__(self, value: Any) -> ComparisonRule:
        """小于等于"""
        return LessThanOrEqual(self.name, value)

    def __eq__(self, value: Any) -> ComparisonRule:
        """等于"""
        return Equal(self.name, value)

    def __ne__(self, value: Any) -> ComparisonRule:
        """不等于"""
        return NotEqual(self.name, value)

    def between(self, min_value: Any, max_value: Any, inclusive: bool = True) -> BetweenRule:
        """在范围内"""
        return BetweenRule(self.name, min_value, max_value, inclusive)

    def in_(self, values: List[Any]) -> InRule:
        """在列表中"""
        return InRule(self.name, values)


# ==================== 便捷函数 ====================

def field(name: str) -> Field:
    """创建字段引用"""
    return Field(name)


# 便捷函数
def greater(field: str, value: Any) -> ComparisonRule:
    """创建大于规则"""
    return GreaterThan(field, value)


def less(field: str, value: Any) -> ComparisonRule:
    """创建小于规则"""
    return LessThan(field, value)


def between(field: str, min_value: Any, max_value: Any) -> BetweenRule:
    """创建范围规则"""
    return BetweenRule(field, min_value, max_value)


def in_range(field: str, values: List[Any]) -> InRule:
    """创建成员规则"""
    return InRule(field, values)


# ==================== 兼容层 ====================

def convert_rules(rules: Union[tuple, Rule, List[Rule]]) -> List[Rule]:
    """
    转换规则为 Rule 对象

    Args:
        rules: 规则（字符串元组、Rule对象或Rule列表）

    Returns:
        Rule对象列表
    """
    if isinstance(rules, tuple):
        # 字符串规则（旧版）
        if all(isinstance(r, str) for r in rules):
            # 保持原样，由系统处理
            return list(rules)  # 返回字符串列表
        # Rule对象元组
        return list(rules)
    elif isinstance(rules, Rule):
        # 单个Rule对象
        return [rules]
    elif isinstance(rules, list):
        return rules
    else:
        raise TypeError(f"不支持的规则类型: {type(rules)}")


def compile_rule(rule: Rule) -> Callable[[Dict[str, Any]], bool]:
    """
    编译规则为函数

    Args:
        rule: Rule对象

    Returns:
        可调用对象
    """
    return rule.compile()


# ==================== 测试 ====================

if __name__ == "__main__":
    """测试规则构建器"""
    print("测试规则构建器\n")

    # 测试上下文
    context = {
        'res': 0.85,
        'price': 100.5,
        'trend': '上涨',
    }

    print("="*70)
    print("测试1: 基本比较规则")
    print("="*70)

    # 创建规则
    rule1 = GreaterThan('res', 0.8)
    rule2 = LessThan('res', 0.9)
    rule3 = Equal('trend', '上涨')

    print(f"规则1: {rule1}")
    print(f"评估结果: {rule1.evaluate(context)}")

    print(f"\n规则2: {rule2}")
    print(f"评估结果: {rule2.evaluate(context)}")

    print(f"\n规则3: {rule3}")
    print(f"评估结果: {rule3.evaluate(context)}")

    print("\n" + "="*70)
    print("测试2: 逻辑组合规则")
    print("="*70)

    # AND 规则
    and_rule = rule1.and_(rule2)
    print(f"AND规则: {and_rule}")
    print(f"评估结果: {and_rule.evaluate(context)}")

    # OR 规则
    or_rule = rule1.or_(rule3)
    print(f"\nOR规则: {or_rule}")
    print(f"评估结果: {or_rule.evaluate(context)}")

    # NOT 规则
    not_rule = rule1.not_()
    print(f"\nNOT规则: {not_rule}")
    print(f"评估结果: {not_rule.evaluate(context)}")

    print("\n" + "="*70)
    print("测试3: 操作符重载")
    print("="*70)

    # 使用操作符
    rule4 = (GreaterThan('res', 0.5) & LessThan('res', 1.0))
    print(f"规则: {rule4}")
    print(f"评估结果: {rule4.evaluate(context)}")

    rule5 = (GreaterThan('res', 0.9) | LessThan('res', 0.1))
    print(f"\n规则: {rule5}")
    print(f"评估结果: {rule5.evaluate(context)}")

    print("\n" + "="*70)
    print("测试4: Field 引用")
    print("="*70)

    # 使用 Field
    res_field = Field('res')
    rule6 = (res_field > 0.8) & (res_field < 0.9)
    print(f"规则: {rule6}")
    print(f"评估结果: {rule6.evaluate(context)}")

    trend_field = Field('trend')
    rule7 = trend_field == '上涨'
    print(f"\n规则: {rule7}")
    print(f"评估结果: {rule7.evaluate(context)}")

    print("\n" + "="*70)
    print("测试5: 范围规则")
    print("="*70)

    # Between 规则
    rule8 = BetweenRule('res', 0.8, 0.9)
    print(f"规则: {rule8}")
    print(f"评估结果: {rule8.evaluate(context)}")

    # In 规则
    rule9 = InRule('trend', ['上涨', '震荡'])
    print(f"\n规则: {rule9}")
    print(f"评估结果: {rule9.evaluate(context)}")

    print("\n" + "="*70)
    print("测试6: 便捷函数")
    print("="*70)

    rule10 = greater('res', 0.8) & less('res', 0.9)
    print(f"规则: {rule10}")
    print(f"评估结果: {rule10.evaluate(context)}")

    print("\n测试完成！")
