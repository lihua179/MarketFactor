# -*- coding: utf-8 -*-
"""
@author: Zed
@file: stock_market_api.py
@time: 2026/1/2 14:53
@describe:自定义描述
"""
from datetime import datetime
import requests
from typing import Optional, Union, List, Dict, Any
from datetime import datetime, date
from dataclasses import dataclass
import json


class StockClientError(Exception):
    """股票客户端基础异常类"""

    def __init__(self, message: str, status_code: int = None, response_body: str = None):
        self.message = message
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(self.message)


class ConnectionError(StockClientError):
    """连接异常"""
    pass


class ResourceNotFoundError(StockClientError):
    """资源不存在异常（股票代码无效）"""
    pass


class BadRequestError(StockClientError):
    """请求参数异常"""
    pass


class ServerError(StockClientError):
    """服务器异常"""
    pass


@dataclass
class StockRecord:
    """股票单条记录数据类"""
    timestamp: int
    open: float
    close: float
    high: float
    low: float
    volume: int
    amount: float
    yd_close: float

    @property
    def datetime(self) -> datetime:
        """将13位时间戳转换为datetime对象"""
        return datetime.fromtimestamp(self.timestamp / 1000)

    @property
    def date_str(self) -> str:
        """获取日期字符串 YYYY-MM-DD"""
        return self.datetime.strftime('%Y-%m-%d')

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'timestamp': self.timestamp,
            'open': self.open,
            'close': self.close,
            'high': self.high,
            'low': self.low,
            'volume': self.volume,
            'amount': self.amount,
            'yd_close': self.yd_close
        }

    def __repr__(self):
        return f"<StockRecord date={self.date_str} close={self.close}>"


class StockClient:
    """
    股票历史数据客户端

    提供简洁的Python接口调用Flask股票历史数据API

    使用示例:
        client = StockClient(base_url="http://localhost:5000")

        # 方式1: 使用日期范围
        data = client.get_history("000001.SZ", start_date="2024-01-01", end_date="2024-01-10")

        # 方式2: 使用开始日期+长度
        data = client.get_history("000001.SZ", start_date="2024-01-01", limit=5)

        # 方式3: 使用结束日期+长度
        data = client.get_history("000001.SZ", end_date="2024-01-10", limit=5)

        # 方式4: 仅使用长度
        data = client.get_history("000001.SZ", limit=10)
    """

    def __init__(
            self,
            base_url: str = "http://localhost:5000",
            timeout: int = 10,
            user_agent: str = "StockClient/1.0"
    ):
        """
        初始化股票客户端

        参数:
            base_url: API服务器地址，默认 http://localhost:5000
            timeout: 请求超时时间（秒），默认10秒
            user_agent: 客户端标识
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent,
            'Content-Type': 'application/json'
        })

    def _format_date(self, date_value: Union[str, datetime, date]) -> str:
        """
        格式化日期为API所需的字符串格式

        参数:
            date_value: 日期值，可以是字符串、datetime或date对象

        返回:
            格式化的日期字符串 YYYY-MM-DD
        """
        if isinstance(date_value, (datetime, date)):
            return date_value.strftime('%Y-%m-%d')
        return str(date_value)

    def _build_params(
            self,
            start_date: Union[str, datetime, date] = None,
            end_date: Union[str, datetime, date] = None,
            limit: int = None
    ) -> Dict[str, Any]:
        """
        构建查询参数

        参数:
            start_date: 开始日期
            end_date: 结束日期
            limit: 数据长度

        返回:
            过滤后的参数字典
        """
        params = {}

        if start_date is not None:
            params['start_date'] = self._format_date(start_date)

        if end_date is not None:
            params['end_date'] = self._format_date(end_date)

        if limit is not None and limit > 0:
            params['limit'] = limit

        return params

    def _handle_error(self, response: requests.Response):
        """
        处理错误响应

        参数:
            response: HTTP响应对象

        异常:
            ResourceNotFoundError: 股票代码不存在
            BadRequestError: 请求参数错误
            ServerError: 服务器错误
        """
        status_code = response.status_code

        if status_code == 404:
            try:
                error_info = response.json()
                message = error_info.get('msg', 'Resource not found')
            except:
                message = 'Resource not found'
            raise ResourceNotFoundError(
                message=message,
                status_code=status_code,
                response_body=response.text
            )

        elif status_code == 400:
            try:
                error_info = response.json()
                message = error_info.get('msg', 'Bad request')
            except:
                message = 'Bad request'
            raise BadRequestError(
                message=message,
                status_code=status_code,
                response_body=response.text
            )

        elif status_code >= 500:
            raise ServerError(
                message='Server error',
                status_code=status_code,
                response_body=response.text
            )

    def get_history(
            self,
            symbol: str,
            start_date: Union[str, datetime, date] = None,
            end_date: Union[str, datetime, date] = None,
            limit: int = None,
            as_records: bool = False,
            as_json: bool = False
    ) -> Union[List[Dict], List[StockRecord], str]:
        """
        获取股票历史数据

        参数:
            symbol: 股票代码，如 "000001.SZ"
            start_date: 开始日期，可选
            end_date: 结束日期，可选
            limit: 数据长度，可选
            as_records: 是否返回StockRecord对象列表，默认False
            as_json: 是否返回原始JSON字符串，默认False

        返回:
            根据参数返回不同类型：
            - as_json=True: 原始JSON字符串
            - as_records=True: List[StockRecord]
            - 默认: List[Dict]

        异常:
            ResourceNotFoundError: 股票代码不存在
            BadRequestError: 请求参数错误
            ServerError: 服务器错误
            ConnectionError: 连接失败

        示例:
            # 返回字典列表
            data = client.get_history("000001.SZ", limit=10)

            # 返回对象列表
            records = client.get_history("000001.SZ", limit=10, as_records=True)
            for record in records:
                print(f"日期: {record.date_str}, 收盘价: {record.close}")
        """
        # 验证股票代码
        if not symbol or not symbol.strip():
            raise BadRequestError(message="Symbol is required")

        endpoint = f"{self.base_url}/api/stock/history"

        # 构建查询参数
        params = self._build_params(start_date, end_date, limit)
        params['symbol'] = symbol.strip()

        try:
            # 发送请求
            response = self.session.get(
                endpoint,
                params=params,
                timeout=self.timeout
            )

            # 处理HTTP错误
            response.raise_for_status()

            # 解析响应
            result = response.json()

            # 检查业务错误
            if result.get('code') != 200:
                error_msg = result.get('msg', 'Unknown error')
                raise StockClientError(message=error_msg)

            data = result.get('data', {})

            # 根据返回类型处理
            if as_json:
                return json.dumps(data, indent=2)

            if as_records:
                return self._convert_to_records(data)

            return data

        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(
                message=f"Failed to connect to {self.base_url}: {str(e)}"
            )

        except requests.exceptions.HTTPError as e:
            self._handle_error(e.response)
            raise StockClientError(message=str(e))

        except requests.exceptions.Timeout as e:
            raise ConnectionError(
                message=f"Request timed out after {self.timeout}s: {str(e)}"
            )

        except requests.exceptions.RequestException as e:
            raise ConnectionError(message=f"Request failed: {str(e)}")

    def _convert_to_records(self, data: Dict[str, List]) -> List[StockRecord]:
        """
        将字典数据转换为StockRecord对象列表

        参数:
            data: API返回的字典数据

        返回:
            StockRecord对象列表
        """
        if not data or not data.get('timestamp'):
            return []

        timestamps = data.get('timestamp', [])

        records = []
        for i, ts in enumerate(timestamps):
            record = StockRecord(
                timestamp=ts,
                open=self._get_value(data, 'open', i),
                close=self._get_value(data, 'close', i),
                high=self._get_value(data, 'high', i),
                low=self._get_value(data, 'low', i),
                volume=self._get_value(data, 'volume', i),
                amount=self._get_value(data, 'amount', i),
                yd_close=self._get_value(data, 'yd_close', i)
            )
            records.append(record)

        return records

    def _get_value(self, data: Dict, key: str, index: int, default=None):
        """安全获取列表中的值"""
        try:
            values = data.get(key, [])
            return values[index] if index < len(values) else default
        except (KeyError, IndexError, TypeError):
            return default

    def get_symbols(self) -> List[str]:
        """
        获取所有可用的股票代码

        返回:
            股票代码列表

        异常:
            ConnectionError: 连接失败
            ServerError: 服务器错误
        """
        try:
            endpoint = f"{self.base_url}/api/stock/symbols"
            response = self.session.get(endpoint, timeout=self.timeout)
            response.raise_for_status()

            result = response.json()
            if result.get('code') == 200:
                return result.get('data', {}).get('symbols', [])
            else:
                raise StockClientError(message=result.get('msg', 'Failed to get symbols'))

        except requests.exceptions.RequestException as e:
            raise ConnectionError(message=f"Failed to get symbols: {str(e)}")

    def health_check(self) -> bool:
        """
        健康检查

        返回:
            True表示服务正常，False表示服务异常
        """
        try:
            endpoint = f"{self.base_url}/health"
            response = self.session.get(endpoint, timeout=self.timeout)
            return response.status_code == 200
        except:
            return False

# 创建客户端实例
client = StockClient(base_url="http://192.168.5.4:1133")
def get_history(
            symbol: str,
            start_date: Union[str, datetime, date] = None,
            end_date: Union[str, datetime, date] = None,
            limit: int = None,
            as_records: bool = False,
            as_json: bool = False
    ) -> Union[List[Dict], List[StockRecord], str]:
    return client.get_history(symbol, start_date,end_date,limit,as_records,as_json)

def get_symbols():
    return client.get_symbols()


if __name__ == '__main__':
    data = get_history("000001.SZ", limit=30)
    print(data)