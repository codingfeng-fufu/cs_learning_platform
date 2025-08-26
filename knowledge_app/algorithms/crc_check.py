"""
CRC循环冗余检验算法实现

CRC是一种根据数据产生简短固定位数校验码的错误检测技术。
通过多项式除法运算来检测数据传输或存储过程中可能出现的错误。

作者: CS学习平台
创建时间: 2025
"""


class CRCChecker:
    """
    CRC循环冗余检验器

    功能:
    1. CRC计算: 根据数据和生成多项式计算CRC校验码
    2. CRC验证: 验证带CRC的数据是否正确
    3. 详细步骤记录: 记录多项式除法的每个步骤
    4. 多种生成多项式支持: 支持常用的CRC多项式
    """

    def __init__(self, polynomial='1011'):
        """
        初始化CRC检验器

        Args:
            polynomial (str): 生成多项式，默认为CRC-3: x³+x+1 = 1011
        """
        self.polynomial = polynomial
        self.steps = []
        self.crc_length = len(polynomial) - 1

    def calculate_crc(self, data):
        """
        计算CRC校验码

        Args:
            data (str): 输入数据（二进制字符串）

        Returns:
            tuple: (CRC校验码, 详细步骤列表)
                  如果计算失败返回 (None, 错误信息列表)
        """
        self.steps = []

        # 输入验证
        if not isinstance(data, str):
            return None, ["错误：输入必须是字符串"]

        if not data:
            return None, ["错误：输入不能为空"]

        if not all(bit in '01' for bit in data):
            return None, ["错误：输入只能包含0和1"]

        if not all(bit in '01' for bit in self.polynomial):
            return None, ["错误：生成多项式只能包含0和1"]

        # 记录初始信息
        self.steps.append(f"步骤1: CRC计算初始化")
        self.steps.append(f"       原始数据: {data}")
        self.steps.append(f"       生成多项式: {self.polynomial}")
        self.steps.append(f"       CRC位数: {self.crc_length}")

        # 步骤1: 数据后补零
        padded_data = data + '0' * self.crc_length
        self.steps.append(f"步骤2: 数据补零")
        self.steps.append(f"       补零后数据: {padded_data}")
        self.steps.append(f"       (在{len(data)}位数据后补{self.crc_length}个0)")

        # 步骤2: 执行多项式除法
        dividend = list(padded_data)
        divisor = list(self.polynomial)

        self.steps.append(f"步骤3: 多项式除法开始")
        self.steps.append(f"       被除数: {padded_data}")
        self.steps.append(f"       除数:   {self.polynomial}")

        division_step = 1

        # 执行除法运算
        for i in range(len(data)):  # 只处理原始数据的位数
            if dividend[i] == '1':
                # 记录除法步骤
                self.steps.append(f"")
                self.steps.append(f"  第{division_step}步除法:")
                self.steps.append(f"    当前位置{i + 1}为1，执行XOR运算")

                # 显示当前状态
                current_state = ''.join(dividend)
                self.steps.append(f"    当前被除数: {current_state}")
                self.steps.append(f"    除数对齐位置: {' ' * i}{self.polynomial}")

                # 执行异或运算
                xor_result = []
                for j in range(len(divisor)):
                    if i + j < len(dividend):
                        old_bit = dividend[i + j]
                        new_bit = str(int(dividend[i + j]) ^ int(divisor[j]))
                        dividend[i + j] = new_bit
                        xor_result.append(f"{old_bit}⊕{divisor[j]}={new_bit}")

                # 显示XOR运算结果
                result_state = ''.join(dividend)
                self.steps.append(f"    XOR运算: {' '.join(xor_result[:len(divisor)])}")
                self.steps.append(f"    运算结果: {result_state}")

                division_step += 1

        # 提取CRC码（最后n位）
        crc_code = ''.join(dividend[-self.crc_length:])

        self.steps.append(f"")
        self.steps.append(f"步骤4: 提取CRC校验码")
        self.steps.append(f"       最终余数: {''.join(dividend)}")
        self.steps.append(f"       CRC校验码: {crc_code} (最后{self.crc_length}位)")

        # 生成完整的传输数据
        complete_data = data + crc_code
        self.steps.append(f"步骤5: 生成传输数据")
        self.steps.append(f"       原始数据 + CRC = {data} + {crc_code} = {complete_data}")

        return crc_code, self.steps

    def verify_crc(self, data_with_crc):
        """
        验证CRC校验码

        Args:
            data_with_crc (str): 包含CRC的完整数据

        Returns:
            tuple: (是否有效, 详细步骤列表)
        """
        self.steps = []

        # 输入验证
        if not isinstance(data_with_crc, str):
            return False, ["错误：输入必须是字符串"]

        if not data_with_crc:
            return False, ["错误：输入不能为空"]

        if not all(bit in '01' for bit in data_with_crc):
            return False, ["错误：输入只能包含0和1"]

        if len(data_with_crc) <= self.crc_length:
            return False, [f"错误：数据长度必须大于{self.crc_length}位"]

        # 记录验证信息
        data_length = len(data_with_crc) - self.crc_length
        received_data = data_with_crc[:data_length]
        received_crc = data_with_crc[data_length:]

        self.steps.append(f"步骤1: CRC验证初始化")
        self.steps.append(f"       接收数据: {data_with_crc}")
        self.steps.append(f"       数据部分: {received_data}")
        self.steps.append(f"       CRC部分:  {received_crc}")
        self.steps.append(f"       生成多项式: {self.polynomial}")

        # 执行多项式除法验证
        dividend = list(data_with_crc)
        divisor = list(self.polynomial)

        self.steps.append(f"步骤2: 验证性多项式除法")
        self.steps.append(f"       被除数: {data_with_crc}")
        self.steps.append(f"       除数:   {self.polynomial}")

        division_step = 1

        # 执行除法运算（处理整个数据长度）
        for i in range(len(data_with_crc) - self.crc_length + 1):
            if dividend[i] == '1':
                # 记录除法步骤
                self.steps.append(f"")
                self.steps.append(f"  第{division_step}步除法:")

                # 显示当前状态
                current_state = ''.join(dividend)
                self.steps.append(f"    当前被除数: {current_state}")
                self.steps.append(f"    除数对齐位置: {' ' * i}{self.polynomial}")

                # 执行异或运算
                xor_result = []
                for j in range(len(divisor)):
                    if i + j < len(dividend):
                        old_bit = dividend[i + j]
                        new_bit = str(int(dividend[i + j]) ^ int(divisor[j]))
                        dividend[i + j] = new_bit
                        xor_result.append(f"{old_bit}⊕{divisor[j]}={new_bit}")

                # 显示运算结果
                result_state = ''.join(dividend)
                self.steps.append(f"    XOR运算: {' '.join(xor_result[:len(divisor)])}")
                self.steps.append(f"    运算结果: {result_state}")

                division_step += 1

        # 检查余数
        remainder = ''.join(dividend[-self.crc_length:])
        is_valid = remainder == '0' * self.crc_length

        self.steps.append(f"")
        self.steps.append(f"步骤3: 验证结果")
        self.steps.append(f"       最终余数: {remainder}")
        self.steps.append(f"       期望余数: {'0' * self.crc_length}")

        if is_valid:
            self.steps.append(f"       验证结果: ✅ 余数为全0，数据有效")
        else:
            self.steps.append(f"       验证结果: ❌ 余数不为全0，数据有错误")

        return is_valid, self.steps

  