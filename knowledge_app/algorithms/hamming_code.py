"""
海明码编码解码算法实现

海明码是一种线性纠错码，能够检测并纠正单个比特错误。
本模块提供了完整的海明码编码、解码和错误纠正功能。

作者: CS学习平台
创建时间: 2025
"""

import math


class HammingCode:
    """
    海明码编码解码器

    功能:
    1. 编码: 将原始数据转换为海明码
    2. 解码: 从海明码恢复原始数据
    3. 错误检测与纠正: 自动检测并纠正单比特错误
    4. 详细步骤记录: 记录每个计算步骤便于学习
    """

    def __init__(self):
        self.steps = []  # 存储详细的计算步骤

    def encode(self, data_bits):
        """
        海明码编码

        Args:
            data_bits (str): 原始数据位，如 "1011"

        Returns:
            tuple: (编码结果字符串, 详细步骤列表)
                  如果编码失败返回 (None, 错误信息列表)
        """
        self.steps = []

        # 步骤1: 输入验证
        if not isinstance(data_bits, str):
            return None, ["错误：输入必须是字符串"]

        if not data_bits:
            return None, ["错误：输入不能为空"]

        if not all(bit in '01' for bit in data_bits):
            return None, ["错误：输入只能包含0和1"]

        data_list = [int(bit) for bit in data_bits]
        n = len(data_list)

        self.steps.append(f"步骤1: 原始数据位 = {data_bits} (共{n}位)")

        # 步骤2: 计算需要的校验位数量
        # 公式: 2^r >= n + r + 1
        r = 0
        while (1 << r) < n + r + 1:
            r += 1

        self.steps.append(f"步骤2: 计算校验位数量")
        self.steps.append(f"       需要满足: 2^r ≥ n+r+1")
        self.steps.append(f"       即: 2^r ≥ {n}+r+1")
        self.steps.append(f"       解得: r = {r} (需要{r}个校验位)")

        # 步骤3: 初始化海明码数组
        hamming_size = n + r
        hamming = [0] * (hamming_size + 1)  # 使用1-indexed数组

        self.steps.append(f"步骤3: 初始化海明码")
        self.steps.append(f"       海明码总长度 = {n} + {r} = {hamming_size}")

        # 步骤4: 确定位置映射并放置数据位
        data_index = 0
        position_map = {}

        for i in range(1, hamming_size + 1):
            if self._is_power_of_2(i):
                # 校验位位置 (2的幂次)
                position_map[i] = f"P{int(math.log2(i)) + 1}"
            else:
                # 数据位位置
                hamming[i] = data_list[data_index]
                position_map[i] = f"D{data_index + 1}"
                data_index += 1

        self.steps.append(f"步骤4: 位置分配")
        self.steps.append(f"       校验位位置: {[pos for pos, desc in position_map.items() if desc.startswith('P')]}")
        self.steps.append(f"       数据位位置: {[pos for pos, desc in position_map.items() if desc.startswith('D')]}")

        # 显示当前状态
        current_state = []
        for i in range(1, hamming_size + 1):
            if self._is_power_of_2(i):
                current_state.append('?')
            else:
                current_state.append(str(hamming[i]))
        self.steps.append(f"       当前状态: {''.join(current_state)} (? 表示待计算的校验位)")

        # 步骤5: 计算每个校验位的值
        self.steps.append(f"步骤5: 计算校验位")

        for i in range(r):
            parity_pos = 1 << i  # 2^i
            parity = 0
            positions_checked = []

            # 找出所有需要参与该校验位计算的位置
            for j in range(1, hamming_size + 1):
                if j & parity_pos:  # 位运算检查第i位是否为1
                    parity ^= hamming[j]  # 异或运算
                    positions_checked.append(j)

            hamming[parity_pos] = parity

            self.steps.append(f"       P{i + 1}(位置{parity_pos}): 检查位置 {positions_checked}")

            # 显示异或运算过程
            values = [str(hamming[pos]) for pos in positions_checked]
            calculation = " ⊕ ".join(values) if values else "0"
            self.steps.append(f"       计算: {calculation} = {parity}")

        # 生成最终结果
        result = ''.join(str(hamming[i]) for i in range(1, hamming_size + 1))

        self.steps.append(f"步骤6: 生成最终海明码")
        self.steps.append(f"       最终海明码 = {result}")

        # 添加位置标注
        position_labels = []
        for i in range(1, hamming_size + 1):
            position_labels.append(position_map[i])
        self.steps.append(f"       位置标注: {' '.join(position_labels)}")

        return result, self.steps

    def decode(self, hamming_bits):
        """
        海明码解码

        Args:
            hamming_bits (str): 海明码字符串，如 "1011010"

        Returns:
            tuple: (解码结果, 是否有错误, 详细步骤列表)
                  如果解码失败返回 (None, False, 错误信息列表)
        """
        self.steps = []

        # 输入验证
        if not isinstance(hamming_bits, str):
            return None, False, ["错误：输入必须是字符串"]

        if not hamming_bits:
            return None, False, ["错误：输入不能为空"]

        if not all(bit in '01' for bit in hamming_bits):
            return None, False, ["错误：输入只能包含0和1"]

        hamming_list = [int(bit) for bit in hamming_bits]
        n = len(hamming_list)

        self.steps.append(f"步骤1: 接收海明码")
        self.steps.append(f"       接收到的海明码 = {hamming_bits} (共{n}位)")

        # 计算校验位数量
        r = 0
        while (1 << r) < n + 1:
            r += 1
        r -= 1  # 实际的校验位数量

        self.steps.append(f"步骤2: 分析海明码结构")
        self.steps.append(f"       推断校验位数量 = {r}")
        self.steps.append(f"       数据位数量 = {n - r}")

        # 创建1-indexed数组
        hamming = [0] + hamming_list

        # 步骤3: 重新计算校验位进行错误检测
        error_pos = 0
        error_syndrome = []

        self.steps.append(f"步骤3: 错误检测 - 重新计算校验位")

        for i in range(r):
            parity_pos = 1 << i
            parity = 0
            positions_checked = []

            # 重新计算校验位
            for j in range(1, n + 1):
                if j & parity_pos:
                    parity ^= hamming[j]
                    positions_checked.append(j)

            # 记录错误症状
            syndrome_bit = 1 if parity != 0 else 0
            error_syndrome.append(syndrome_bit)

            if syndrome_bit:
                error_pos += parity_pos

            # 显示详细计算过程
            values = [str(hamming[pos]) for pos in positions_checked]
            calculation = " ⊕ ".join(values) if values else "0"
            self.steps.append(f"       P{i + 1}校验: 位置{positions_checked} = {calculation} = {parity}")
            self.steps.append(f"       校验结果: {'错误' if syndrome_bit else '正确'}")

        # 分析错误症状码
        syndrome_str = ''.join(map(str, reversed(error_syndrome)))  # 反转以匹配二进制位序
        self.steps.append(f"步骤4: 错误定位")
        self.steps.append(f"       错误症状码 = {syndrome_str} (二进制)")
        self.steps.append(f"       错误位置 = {error_pos} (十进制)")

        # 错误纠正
        has_error = error_pos != 0
        if has_error:
            self.steps.append(f"步骤5: 错误纠正")
            self.steps.append(f"       检测到位置{error_pos}有错误")

            original_bit = hamming[error_pos]
            hamming[error_pos] = 1 - hamming[error_pos]  # 翻转错误位

            self.steps.append(f"       纠正: 位置{error_pos}: {original_bit} → {hamming[error_pos]}")
        else:
            self.steps.append(f"步骤5: 未检测到错误，数据完整")

        # 步骤6: 提取原始数据
        data_bits = []
        data_positions = []

        for i in range(1, n + 1):
            if not self._is_power_of_2(i):
                data_bits.append(str(hamming[i]))
                data_positions.append(i)

        result = ''.join(data_bits)

        self.steps.append(f"步骤6: 提取原始数据")
        self.steps.append(f"       数据位位置: {data_positions}")
        self.steps.append(f"       原始数据 = {result}")

        return result, has_error, self.steps

    def _is_power_of_2(self, n):
        """
        检查一个数是否为2的幂

        Args:
            n (int): 要检查的数

        Returns:
            bool: 如果n是2的幂返回True，否则返回False
        """
        return n > 0 and (n & (n - 1)) == 0

    def get_hamming_info(self, data_length):
        """
        获取给定数据长度所需的海明码信息

        Args:
            data_length (int): 原始数据长度

        Returns:
            dict: 包含校验位数量、总长度等信息的字典
        """
        r = 0
        while (1 << r) < data_length + r + 1:
            r += 1

        return {
            'data_length': data_length,
            'parity_bits': r,
            'total_length': data_length + r,
            'efficiency': data_length / (data_length + r),
            'can_detect_errors': 1,  # 能检测的错误比特数
            'can_correct_errors': 1  # 能纠正的错误比特数
        }


def test_hamming_code():
    """
    测试海明码功能的完整示例
    """
    print("🧮 海明码算法测试")
    print("=" * 50)

    hc = HammingCode()

    # 测试用例
    test_cases = ["1011", "1101", "110101", "1010"]

    for data in test_cases:
        print(f"\n📝 测试数据: {data}")
        print("-" * 30)

        # 编码测试
        encoded, encode_steps = hc.encode(data)
        print(f"编码结果: {encoded}")

        if encoded:
            # 解码测试（无错误）
            decoded, has_error, decode_steps = hc.decode(encoded)
            print(f"解码结果: {decoded}")
            print(f"检测到错误: {has_error}")

            # 验证正确性
            if decoded == data and not has_error:
                print("✅ 编码解码正确")
            else:
                print("❌ 编码解码失败")

            # 错误纠正测试
            if len(encoded) > 2:
                # 人为制造错误
                error_code = list(encoded)
                error_pos = len(error_code) // 2
                error_code[error_pos] = '0' if error_code[error_pos] == '1' else '1'
                error_code_str = ''.join(error_code)

                print(f"\n🔧 错误纠正测试:")
                print(f"制造错误: {encoded} → {error_code_str}")

                corrected, had_error, correct_steps = hc.decode(error_code_str)
                print(f"纠正结果: {corrected}")
                print(f"检测到错误: {had_error}")

                if corrected == data and had_error:
                    print("✅ 错误纠正成功")
                else:
                    print("❌ 错误纠正失败")

    print("\n" + "=" * 50)
    print("测试完成")


if __name__ == "__main__":
    test_hamming_code()