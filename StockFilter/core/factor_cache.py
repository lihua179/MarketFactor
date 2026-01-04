# -*- coding: utf-8 -*-
"""
因子缓存系统 - 避免重复计算，提升性能

功能：
1. LRU 缓存策略
2. 基于因子+参数+数据的缓存键
3. 跨股票复用（不同股票但相同因子参数）
4. 缓存命中率统计
"""
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from collections import OrderedDict
import hashlib
import json


@dataclass
class CacheKey:
    """缓存键"""
    func_name: str  # 函数名
    params: Tuple[Tuple[str, Any], ...]  # 参数（已排序和转换）
    data_hash: str  # 数据哈希

    def __hash__(self) -> int:
        """计算哈希值"""
        return hash((self.func_name, self.params, self.data_hash))

    def __eq__(self, other) -> bool:
        """相等判断"""
        if not isinstance(other, CacheKey):
            return False
        return (self.func_name == other.func_name and
                self.params == other.params and
                self.data_hash == other.data_hash)


@dataclass
class CacheEntry:
    """缓存条目"""
    key: CacheKey
    value: Any  # 缓存值
    hit_count: int = 0  # 命中次数

    def touch(self):
        """更新命中次数"""
        self.hit_count += 1


@dataclass
class CacheStatistics:
    """缓存统计"""
    hits: int = 0  # 命中次数
    misses: int = 0  # 未命中次数
    evictions: int = 0  # 驱逐次数
    size: int = 0  # 当前缓存大小

    @property
    def total_requests(self) -> int:
        """总请求次数"""
        return self.hits + self.misses

    @property
    def hit_rate(self) -> float:
        """缓存命中率"""
        if self.total_requests == 0:
            return 0.0
        return self.hits / self.total_requests

    def __str__(self) -> str:
        """字符串表示"""
        return (
            f"缓存统计:\n"
            f"  命中: {self.hits}\n"
            f"  未命中: {self.misses}\n"
            f"  命中率: {self.hit_rate:.2%}\n"
            f"  当前大小: {self.size}\n"
            f"  驱逐次数: {self.evictions}"
        )


class LRUCache:
    """LRU (Least Recently Used) 缓存"""

    def __init__(self, max_size: int = 1000):
        """
        初始化 LRU 缓存

        Args:
            max_size: 最大缓存条目数
        """
        self.max_size = max_size
        self.cache: OrderedDict[CacheKey, CacheEntry] = OrderedDict()
        self.stats = CacheStatistics()

    def get(self, key: CacheKey) -> Optional[Any]:
        """
        获取缓存值

        Args:
            key: 缓存键

        Returns:
            缓存值，如果不存在则返回 None
        """
        if key in self.cache:
            # 命中
            entry = self.cache[key]
            entry.touch()

            # LRU: 移到末尾
            self.cache.move_to_end(key)

            self.stats.hits += 1
            return entry.value
        else:
            # 未命中
            self.stats.misses += 1
            return None

    def put(self, key: CacheKey, value: Any) -> None:
        """
        放入缓存

        Args:
            key: 缓存键
            value: 缓存值
        """
        # 如果已存在，更新并移到末尾
        if key in self.cache:
            self.cache[key].value = value
            self.cache.move_to_end(key)
            return

        # 如果缓存已满，删除最旧的条目
        if len(self.cache) >= self.max_size:
            if self.cache:  # 确保缓存不为空
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                self.stats.evictions += 1

        # 添加新条目
        self.cache[key] = CacheEntry(key=key, value=value)
        self.stats.size = len(self.cache)

    def clear(self) -> None:
        """清空缓存"""
        self.cache.clear()
        self.stats.size = 0

    def print_stats(self) -> None:
        """打印统计信息"""
        print("\n" + str(self.stats))


class FactorCache:
    """因子缓存管理器"""

    def __init__(self, max_size: int = 1000):
        """
        初始化因子缓存

        Args:
            max_size: 最大缓存条目数（0 表示禁用缓存）
        """
        self.max_size = max_size
        self.enabled = max_size > 0
        self.cache = LRUCache(max_size=max_size) if self.enabled else None

    @staticmethod
    def hash_data(data: Dict[str, List], sample_size: int = 10) -> str:
        """
        计算数据哈希

        Args:
            data: OHLCV 数据
            sample_size: 采样大小（只取最后N个数据进行哈希）

        Returns:
            哈希字符串
        """
        # 提取关键信息进行哈希
        key_data = {
            'close_len': len(data.get('close', [])),
            'close_sample': data.get('close', [])[-sample_size:] if len(data.get('close', [])) >= sample_size else data.get('close', []),
        }

        # 转换为 JSON 并计算哈希
        data_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(data_str.encode()).hexdigest()

    @staticmethod
    def make_key(func: Callable, params: Dict[str, Any], data_hash: str) -> CacheKey:
        """
        创建缓存键

        Args:
            func: 因子函数
            params: 参数字典
            data_hash: 数据哈希

        Returns:
            CacheKey 对象
        """
        func_name = func.__name__

        # 转换参数为可哈希的元组（排序以保证一致性）
        params_tuple = tuple(sorted(
            (k, FactorCache._make_hashable(v))
            for k, v in params.items()
            if k != 'detail'  # 排除 detail 参数（它包含之前的计算结果）
        ))

        return CacheKey(
            func_name=func_name,
            params=params_tuple,
            data_hash=data_hash
        )

    @staticmethod
    def _make_hashable(value: Any) -> Any:
        """
        将值转换为可哈希的类型

        Args:
            value: 任意值

        Returns:
            可哈希的值
        """
        if isinstance(value, dict):
            return tuple(sorted((k, FactorCache._make_hashable(v)) for k, v in value.items()))
        elif isinstance(value, list):
            return tuple(FactorCache._make_hashable(v) for v in value)
        elif isinstance(value, (str, int, float, bool, type(None))):
            return value
        else:
            return str(value)

    def get(self, func: Callable, params: Dict[str, Any],
            data: Dict[str, List]) -> Optional[Any]:
        """
        获取缓存

        Args:
            func: 因子函数
            params: 参数字典
            data: OHLCV 数据

        Returns:
            缓存值，如果不存在则返回 None
        """
        if not self.enabled:
            return None

        data_hash = self.hash_data(data)
        key = self.make_key(func, params, data_hash)
        return self.cache.get(key)

    def put(self, func: Callable, params: Dict[str, Any],
            data: Dict[str, List], value: Any) -> None:
        """
        放入缓存

        Args:
            func: 因子函数
            params: 参数字典
            data: OHLCV 数据
            value: 缓存值
        """
        if not self.enabled:
            return

        data_hash = self.hash_data(data)
        key = self.make_key(func, params, data_hash)
        self.cache.put(key, value)

    def get_hit_rate(self) -> float:
        """获取缓存命中率"""
        if not self.enabled:
            return 0.0
        return self.cache.stats.hit_rate

    def clear(self) -> None:
        """清空缓存"""
        if self.enabled:
            self.cache.clear()

    def print_stats(self) -> None:
        """打印统计信息"""
        if self.enabled:
            self.cache.print_stats()
        else:
            print("\n缓存已禁用")


# ==================== 集成到 StockFilter ====================

def run_with_cache(
    data: Dict[str, List],
    chain: List,
    cache: Optional[FactorCache] = None,
    print_stats: bool = False
) -> Dict[str, Any]:
    """
    带缓存的运行函数

    Args:
        data: OHLCV 格式数据
        chain: 因子链
        cache: 因子缓存（如果为 None，则不使用缓存）
        print_stats: 是否打印缓存统计

    Returns:
        包含 pass、details 的结果字典
    """
    from stock_filter import pass_filter

    # 如果没有提供缓存，创建一个禁用的缓存
    if cache is None:
        cache = FactorCache(max_size=0)  # max_size=0 表示禁用缓存

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

        # 尝试从缓存获取
        cached_result = cache.get(func, params, data)

        if cached_result is not None:
            # 缓存命中
            result = cached_result
        else:
            # 缓存未命中，执行计算
            params['detail'] = details
            result = func(data, **params)

            # 放入缓存
            cache.put(func, params, data, result)

        # 验证规则
        if not pass_filter(result, rules):
            ok = False
            break

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

    # 打印缓存统计
    if print_stats:
        cache.print_stats()

    return {
        "pass": ok,
        "details": details
    }


# ==================== 测试 ====================

if __name__ == "__main__":
    """测试因子缓存系统"""
    print("测试因子缓存系统\n")

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
    print("测试1: 无缓存（基线）")
    print("="*70)

    import time

    start = time.time()
    for i in range(100):
        result = run_with_cache(
            test_data,
            [
                BasicStatistics.level_relative(n=20, name='level'),
                BasicStatistics.return_total(n=20, name='return'),
            ],
            cache=None,  # 不使用缓存
            print_stats=False
        )
    elapsed_no_cache = time.time() - start

    print(f"100次执行耗时（无缓存）: {elapsed_no_cache:.4f}秒")

    print("\n" + "="*70)
    print("测试2: 使用缓存（重复因子）")
    print("="*70)

    cache = FactorCache(max_size=1000)

    start = time.time()
    for i in range(100):
        result = run_with_cache(
            test_data,
            [
                BasicStatistics.level_relative(n=20, name='level'),
                BasicStatistics.return_total(n=20, name='return'),
            ],
            cache=cache,
            print_stats=False
        )
    elapsed_with_cache = time.time() - start

    print(f"100次执行耗时（有缓存）: {elapsed_with_cache:.4f}秒")
    print(f"性能提升: {elapsed_no_cache / elapsed_with_cache:.1f}x")

    cache.print_stats()

    print("\n" + "="*70)
    print("测试3: 跨股票复用（不同股票，相同因子）")
    print("="*70)

    cache2 = FactorCache(max_size=1000)

    # 模拟10只不同的股票（数据略有不同）
    for i in range(10):
        # 稍微修改数据模拟不同股票
        stock_data = test_data.copy()
        stock_data['close'] = [v + i * 0.1 for v in test_data['close']]

        result = run_with_cache(
            stock_data,
            [
                BasicStatistics.level_relative(n=20, name='level'),
                BasicStatistics.return_total(n=20, name='return'),
            ],
            cache=cache2,
            print_stats=False
        )

    cache2.print_stats()

    print("\n测试完成！")
