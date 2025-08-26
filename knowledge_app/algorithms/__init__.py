"""
算法实现模块

包含各种计算机科学算法的实现：
- hamming_code: 海明码编码解码算法
- crc_check: CRC循环冗余检验算法

每个算法模块都应该包含：
1. 算法的核心实现
2. 详细的步骤记录
3. 完整的错误处理
4. 测试函数
"""

from .hamming_code import HammingCode
from .crc_check import CRCChecker
from .single_linklist import SingleLinkedList
__all__ = ['HammingCode', 'CRCChecker','SingleLinkedList']