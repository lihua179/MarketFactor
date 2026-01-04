# -*- coding: utf-8 -*-
"""
批量处理优化系统 - 支持多股票并行处理

功能：
1. 并行处理多只股票（多线程/多进程）
2. 进度条显示
3. 统计信息（通过率、失败率等）
4. 失败重试机制
5. 资源管理和限流
"""
from typing import Dict, List, Any, Callable, Optional, Union
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import time
import os
from stock_filter import Config


@dataclass
class StockResult:
    """单只股票的处理结果"""
    symbol: str  # 股票代码
    passed: bool  # 是否通过
    details: Dict[str, Any] = field(default_factory=dict)  # 详情
    error: Optional[str] = None  # 错误信息
    execution_time: float = 0.0  # 执行时间


@dataclass
class BatchStatistics:
    """批量处理统计"""
    total: int = 0  # 总数
    passed: int = 0  # 通过数
    failed: int = 0  # 失败数
    total_time: float = 0.0  # 总耗时
    avg_time: float = 0.0  # 平均耗时
    min_time: float = float('inf')  # 最小耗时
    max_time: float = 0.0  # 最大耗时

    @property
    def pass_rate(self) -> float:
        """通过率"""
        return self.passed / self.total if self.total > 0 else 0.0

    @property
    def fail_rate(self) -> float:
        """失败率"""
        return self.failed / self.total if self.total > 0 else 0.0

    def update(self, result: StockResult):
        """更新统计"""
        self.total += 1
        if result.passed:
            self.passed += 1
        else:
            self.failed += 1

        self.total_time += result.execution_time
        self.avg_time = self.total_time / self.total

        if result.execution_time < self.min_time:
            self.min_time = result.execution_time
        if result.execution_time > self.max_time:
            self.max_time = result.execution_time


@dataclass
class BatchResult:
    """批量处理结果"""
    results: Dict[str, StockResult]  # 所有结果（symbol -> StockResult）
    statistics: BatchStatistics  # 统计信息
    start_time: float  # 开始时间
    end_time: float  # 结束时间

    @property
    def passed_symbols(self) -> List[str]:
        """通过的股票列表"""
        return [s for s, r in self.results.items() if r.passed]

    @property
    def failed_symbols(self) -> List[str]:
        """失败的股票列表"""
        return [s for s, r in self.results.items() if not r.passed]

    @property
    def total_time(self) -> float:
        """总耗时"""
        return self.end_time - self.start_time

    def print_summary(self):
        """打印摘要"""
        print("\n" + "="*70)
        print("批量处理摘要")
        print("="*70)
        print(f"总数: {self.statistics.total}")
        print(f"通过: {self.statistics.passed} ({self.statistics.pass_rate:.2%})")
        print(f"失败: {self.statistics.failed} ({self.statistics.fail_rate:.2%})")
        print(f"总耗时: {self.total_time:.2f}秒")
        print(f"平均耗时: {self.statistics.avg_time:.4f}秒/股")
        print(f"最慢: {self.statistics.max_time:.4f}秒")
        print(f"最快: {self.statistics.min_time:.4f}秒")

        # 性能估算
        if self.statistics.total > 1:
            print(f"\n性能提升: 相比串行处理，速度提升约 {self._speedup():.1f}x")

        print("="*70 + "\n")

    def _speedup(self) -> float:
        """估算加速比"""
        if self.statistics.total <= 1:
            return 1.0
        # 串行处理时间 = 总耗时（因为是并行）
        # 并行处理时间 = 总耗时 / worker数（理想情况）
        # 实际加速比 = 串行时间 / 并行时间
        serial_time = self.statistics.total_time
        parallel_time = self.total_time
        return serial_time / parallel_time if parallel_time > 0 else 1.0


class BatchProcessor:
    """批量处理器"""

    def __init__(self,
                 config: Config,
                 max_workers: Optional[int] = None,
                 use_processes: bool = False,
                 show_progress: bool = True):
        """
        初始化批量处理器

        Args:
            config: StockFilter 配置
            max_workers: 最大工作线程/进程数（默认 CPU 核心数）
            use_processes: 是否使用多进程（True）还是多线程（False）
            show_progress: 是否显示进度条
        """
        self.config = config
        self.max_workers = max_workers or os.cpu_count() or 4
        self.use_processes = use_processes
        self.show_progress = show_progress

    def run(self,
            symbols: List[str],
            data_provider: Callable[[str], Dict[str, List]],
            retry_count: int = 0) -> BatchResult:
        """
        批量运行

        Args:
            symbols: 股票代码列表
            data_provider: 数据提供函数，接受 symbol，返回 OHLCV 数据
            retry_count: 失败重试次数

        Returns:
            BatchResult 对象
        """
        start_time = time.time()
        statistics = BatchStatistics()
        results = {}

        # 选择执行器
        executor_class = ProcessPoolExecutor if self.use_processes else ThreadPoolExecutor

        with executor_class(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_symbol = {
                executor.submit(self._process_one, symbol, data_provider, retry_count): symbol
                for symbol in symbols
            }

            # 进度条
            if self.show_progress:
                try:
                    from tqdm import tqdm
                    futures = tqdm(as_completed(future_to_symbol),
                                total=len(future_to_symbol),
                                desc="处理股票")
                except ImportError:
                    print("提示: 安装 tqdm 可显示进度条: pip install tqdm")
                    futures = as_completed(future_to_symbol)
            else:
                futures = as_completed(future_to_symbol)

            # 收集结果
            for future in futures:
                symbol = future_to_symbol[future]
                try:
                    result = future.result()
                    results[symbol] = result
                    statistics.update(result)
                except Exception as e:
                    # 捕获未预期的异常
                    error_result = StockResult(
                        symbol=symbol,
                        passed=False,
                        error=f"未捕获的异常: {str(e)}"
                    )
                    results[symbol] = error_result
                    statistics.update(error_result)

        end_time = time.time()

        return BatchResult(
            results=results,
            statistics=statistics,
            start_time=start_time,
            end_time=end_time
        )

    def _process_one(self,
                    symbol: str,
                    data_provider: Callable[[str], Dict[str, List]],
                    retry_count: int) -> StockResult:
        """
        处理单个股票

        Args:
            symbol: 股票代码
            data_provider: 数据提供函数
            retry_count: 重试次数

        Returns:
            StockResult 对象
        """
        start = time.time()
        error_msg = None
        passed = False
        details = {}

        for attempt in range(retry_count + 1):
            try:
                # 获取数据
                data = data_provider(symbol)

                # 运行配置
                result = self.config.run(data)
                passed = result['pass']
                details = result.get('details', {})
                break

            except Exception as e:
                error_msg = str(e)
                if attempt < retry_count:
                    # 重试
                    time.sleep(0.1 * (attempt + 1))  # 指数退避
                    continue
                else:
                    # 最后一次尝试也失败
                    passed = False
                    details = {}

        execution_time = time.time() - start

        return StockResult(
            symbol=symbol,
            passed=passed,
            details=details,
            error=error_msg,
            execution_time=execution_time
        )

    def run_serial(self,
                  symbols: List[str],
                  data_provider: Callable[[str], Dict[str, List]]) -> BatchResult:
        """
        串行运行（用于对比）

        Args:
            symbols: 股票代码列表
            data_provider: 数据提供函数

        Returns:
            BatchResult 对象
        """
        start_time = time.time()
        statistics = BatchStatistics()
        results = {}

        print(f"串行处理 {len(symbols)} 只股票...")

        for i, symbol in enumerate(symbols, 1):
            if self.show_progress:
                print(f"处理进度: {i}/{len(symbols)} - {symbol}")

            result = self._process_one(symbol, data_provider, retry_count=0)
            results[symbol] = result
            statistics.update(result)

        end_time = time.time()

        return BatchResult(
            results=results,
            statistics=statistics,
            start_time=start_time,
            end_time=end_time
        )


# ==================== 便捷函数 ====================

def batch_process(config: Config,
                 symbols: List[str],
                 data_provider: Callable[[str], Dict[str, List]],
                 max_workers: Optional[int] = None,
                 show_progress: bool = True) -> BatchResult:
    """
    批量处理便捷函数

    Args:
        config: StockFilter 配置
        symbols: 股票代码列表
        data_provider: 数据提供函数
        max_workers: 最大工作线程数
        show_progress: 是否显示进度

    Returns:
        BatchResult 对象
    """
    processor = BatchProcessor(
        config=config,
        max_workers=max_workers,
        show_progress=show_progress
    )
    return processor.run(symbols, data_provider)


# ==================== 测试 ====================

if __name__ == "__main__":
    """测试批量处理系统"""
    import random

    print("测试批量处理优化系统\n")

    # 模拟数据提供函数
    def mock_data_provider(symbol: str) -> Dict[str, List]:
        """模拟数据提供"""
        # 随机延迟（模拟网络请求）
        time.sleep(random.uniform(0.01, 0.05))

        # 生成模拟数据
        length = random.randint(30, 60)
        base_price = random.uniform(10, 50)

        return {
            'open': [base_price + random.uniform(-1, 1) for _ in range(length)],
            'high': [base_price + random.uniform(0, 2) for _ in range(length)],
            'low': [base_price + random.uniform(-2, 0) for _ in range(length)],
            'close': [base_price + random.uniform(-1, 1) for _ in range(length)],
            'volume': [random.randint(10000, 50000) for _ in range(length)],
            'yd_close': [base_price + random.uniform(-1, 1) for _ in range(length)],
        }

    from stock_filter import Config
    from basic_statistics_factors import BasicStatistics

    # 创建配置
    config = Config(
        BasicStatistics.level_relative(
            n=20,
            rules=("res > 0.5",),
            name='high_level'
        ),
        BasicStatistics.return_total(
            n=20,
            rules=("res > 0",),
            name='profitable'
        ),
    )

    # 测试股票列表
    test_symbols = [f"00{i:04d}.SZ" for i in range(1, 51)]  # 50只股票

    # 测试1: 并行处理
    print("="*70)
    print("测试1: 并行批量处理（50只股票）")
    print("="*70)

    processor = BatchProcessor(
        config=config,
        max_workers=8,
        show_progress=True
    )

    result_parallel = processor.run(test_symbols, mock_data_provider)
    result_parallel.print_summary()

    # 测试2: 串行处理（对比）
    print("\n" + "="*70)
    print("测试2: 串行处理（对比）")
    print("="*70)

    # 只处理10只进行对比
    test_symbols_small = test_symbols[:10]
    result_serial = processor.run_serial(test_symbols_small, mock_data_provider)
    result_serial.print_summary()

    print("\n性能对比（10只股票）:")
    print(f"  串行: {result_serial.total_time:.2f}秒")
    print(f"  并行: {result_parallel.total_time * (10/50):.2f}秒 (估算)")

    print("\n测试完成！")
