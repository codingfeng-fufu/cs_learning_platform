"""
单链表数据结构实现 - 增强版

新增功能：
1. 插入操作（在指定节点之前/之后插入）
2. 查找操作
3. 更详细的步骤记录以支持可视化

作者: CS学习平台
创建时间: 2025
"""


class ListNode:
    """
    链表节点类

    Attributes:
        val: 节点存储的数据值
        next: 指向下一个节点的指针
    """

    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

    def __str__(self):
        return f"Node({self.val})"

    def __repr__(self):
        return f"ListNode(val={self.val}, next={self.next})"


class SingleLinkedList:
    """
    单链表类 - 增强版

    新增功能:
    1. 插入: 在指定值之前/之后插入
    2. 查找: 详细的查找过程记录
    3. 可视化支持: 提供详细的操作步骤用于前端动画
    """

    def __init__(self):
        self.head = None  # 头节点指针
        self.size = 0  # 链表长度
        self.steps = []  # 操作步骤记录

    def clear_steps(self):
        """清除步骤记录"""
        self.steps = []

    def add_step(self, step, step_type="info", highlight_nodes=None, highlight_pointers=None):
        """
        添加操作步骤

        Args:
            step: 步骤描述
            step_type: 步骤类型 (info, success, warning, error)
            highlight_nodes: 需要高亮的节点位置列表
            highlight_pointers: 需要高亮的指针操作
        """
        step_info = {
            'description': step,
            'type': step_type,
            'highlight_nodes': highlight_nodes or [],
            'highlight_pointers': highlight_pointers or [],
            'current_state': self.to_list()
        }
        self.steps.append(step_info)

    def get_size(self):
        """获取链表长度"""
        return self.size

    def is_empty(self):
        """检查链表是否为空"""
        return self.head is None

    def to_list(self):
        """将链表转换为Python列表"""
        result = []
        current = self.head
        while current:
            result.append(current.val)
            current = current.next
        return result

    def display(self):
        """以字符串形式展示链表"""
        if self.is_empty():
            return "Empty List"

        values = []
        current = self.head
        while current:
            values.append(str(current.val))
            current = current.next

        return " -> ".join(values) + " -> NULL"

    def add_head(self, val):
        """在链表头部添加节点"""
        self.clear_steps()

        try:
            self.add_step(f"准备在链表头部添加节点，值为 {val}", "info")
            self.add_step(f"创建新节点 Node({val})", "info")

            # 创建新节点
            new_node = ListNode(val)

            if self.is_empty():
                self.add_step(f"链表为空，直接设置新节点为头节点", "info", highlight_nodes=[0])
                self.head = new_node
            else:
                self.add_step(f"将新节点的 next 指针指向当前头节点 (值为 {self.head.val})", "info",
                              highlight_nodes=[0], highlight_pointers=["new->head"])
                new_node.next = self.head
                self.add_step(f"更新头指针指向新节点", "info", highlight_nodes=[0])
                self.head = new_node

            self.size += 1
            self.add_step(f"添加完成，链表长度变为 {self.size}", "success")

            return True, [step['description'] for step in self.steps]

        except Exception as e:
            self.add_step(f"添加失败 - {str(e)}", "error")
            return False, [step['description'] for step in self.steps]

    def add_tail(self, val):
        """在链表尾部添加节点"""
        self.clear_steps()

        try:
            self.add_step(f"准备在链表尾部添加节点，值为 {val}", "info")
            self.add_step(f"创建新节点 Node({val})", "info")

            # 创建新节点
            new_node = ListNode(val)

            if self.is_empty():
                self.add_step(f"链表为空，直接设置新节点为头节点", "info", highlight_nodes=[0])
                self.head = new_node
            else:
                self.add_step(f"遍历链表寻找尾节点", "info")
                current = self.head
                position = 0

                # 找到尾节点
                while current.next is not None:
                    self.add_step(f"访问位置 {position} 的节点 (值为 {current.val})，继续向下遍历",
                                  "info", highlight_nodes=[position])
                    current = current.next
                    position += 1

                self.add_step(f"找到尾节点 (值为 {current.val}) 在位置 {position}",
                              "info", highlight_nodes=[position])
                self.add_step(f"将尾节点的 next 指针指向新节点", "info",
                              highlight_nodes=[position, position + 1], highlight_pointers=["tail->new"])
                current.next = new_node

            self.size += 1
            self.add_step(f"添加完成，链表长度变为 {self.size}", "success")

            return True, [step['description'] for step in self.steps]

        except Exception as e:
            self.add_step(f"添加失败 - {str(e)}", "error")
            return False, [step['description'] for step in self.steps]

    def add_at_position(self, position, val):
        """在指定位置添加节点"""
        self.clear_steps()

        try:
            self.add_step(f"准备在位置 {position} 插入节点，值为 {val}", "info")

            # 验证位置有效性
            if position < 0 or position > self.size:
                raise ValueError(f"位置 {position} 超出有效范围 [0, {self.size}]")

            self.add_step(f"位置验证通过，当前链表长度为 {self.size}", "info")

            # 特殊情况：在头部插入
            if position == 0:
                self.add_step(f"位置为0，转为头部插入操作", "info")
                return self.add_head(val)

            self.add_step(f"创建新节点 Node({val})", "info")
            new_node = ListNode(val)

            self.add_step(f"遍历到位置 {position - 1}", "info")
            current = self.head

            # 遍历到插入位置的前一个节点
            for i in range(position - 1):
                self.add_step(f"访问位置 {i} 的节点 (值为 {current.val})",
                              "info", highlight_nodes=[i])
                current = current.next

            self.add_step(f"到达位置 {position - 1}，节点值为 {current.val}",
                          "info", highlight_nodes=[position - 1])
            self.add_step(f"调整指针连接：新节点指向位置 {position} 的原节点",
                          "info", highlight_nodes=[position - 1, position],
                          highlight_pointers=["new->next"])

            # 调整指针
            new_node.next = current.next
            current.next = new_node

            self.add_step(f"将位置 {position - 1} 节点的 next 指向新节点",
                          "info", highlight_nodes=[position - 1, position],
                          highlight_pointers=["prev->new"])

            self.size += 1
            self.add_step(f"插入完成，链表长度变为 {self.size}", "success")

            return True, [step['description'] for step in self.steps]

        except Exception as e:
            self.add_step(f"插入失败 - {str(e)}", "error")
            return False, [step['description'] for step in self.steps]

    def insert_before_value(self, target_val, new_val):
        """
        在指定值之前插入新节点

        Args:
            target_val: 目标节点值
            new_val: 新节点值

        Returns:
            tuple: (操作是否成功, 详细步骤列表)
        """
        self.clear_steps()

        try:
            if self.is_empty():
                raise ValueError("链表为空，无法执行插入操作")

            self.add_step(f"准备在值为 {target_val} 的节点之前插入 {new_val}", "info")

            # 特殊情况：在头节点之前插入
            if self.head.val == target_val:
                self.add_step(f"目标节点是头节点，转为头部插入操作", "info", highlight_nodes=[0])
                return self.add_head(new_val)

            self.add_step(f"遍历链表查找值为 {target_val} 的节点", "info")
            current = self.head
            position = 0

            # 查找目标节点的前一个节点
            while current.next is not None:
                self.add_step(f"检查位置 {position + 1} 的节点 (值为 {current.next.val})",
                              "info", highlight_nodes=[position, position + 1])

                if current.next.val == target_val:
                    self.add_step(f"找到目标节点在位置 {position + 1}", "info",
                                  highlight_nodes=[position + 1])

                    # 在此位置插入
                    new_node = ListNode(new_val)
                    self.add_step(f"创建新节点 Node({new_val})", "info")

                    self.add_step(f"调整指针：新节点指向目标节点", "info",
                                  highlight_nodes=[position, position + 1, position + 2],
                                  highlight_pointers=["new->target"])
                    new_node.next = current.next

                    self.add_step(f"前一个节点指向新节点", "info",
                                  highlight_nodes=[position, position + 1],
                                  highlight_pointers=["prev->new"])
                    current.next = new_node

                    self.size += 1
                    self.add_step(f"插入完成，链表长度变为 {self.size}", "success")

                    return True, [step['description'] for step in self.steps]

                current = current.next
                position += 1

            # 未找到目标节点
            raise ValueError(f"未找到值为 {target_val} 的节点")

        except Exception as e:
            self.add_step(f"插入失败 - {str(e)}", "error")
            return False, [step['description'] for step in self.steps]

    def insert_after_value(self, target_val, new_val):
        """
        在指定值之后插入新节点

        Args:
            target_val: 目标节点值
            new_val: 新节点值

        Returns:
            tuple: (操作是否成功, 详细步骤列表)
        """
        self.clear_steps()

        try:
            if self.is_empty():
                raise ValueError("链表为空，无法执行插入操作")

            self.add_step(f"准备在值为 {target_val} 的节点之后插入 {new_val}", "info")

            current = self.head
            position = 0

            # 查找目标节点
            while current is not None:
                self.add_step(f"检查位置 {position} 的节点 (值为 {current.val})",
                              "info", highlight_nodes=[position])

                if current.val == target_val:
                    self.add_step(f"找到目标节点在位置 {position}", "info", highlight_nodes=[position])

                    # 创建新节点
                    new_node = ListNode(new_val)
                    self.add_step(f"创建新节点 Node({new_val})", "info")

                    self.add_step(f"调整指针：新节点指向目标节点的下一个节点", "info",
                                  highlight_nodes=[position, position + 1],
                                  highlight_pointers=["new->next"])
                    new_node.next = current.next

                    self.add_step(f"目标节点指向新节点", "info",
                                  highlight_nodes=[position, position + 1],
                                  highlight_pointers=["target->new"])
                    current.next = new_node

                    self.size += 1
                    self.add_step(f"插入完成，链表长度变为 {self.size}", "success")

                    return True, [step['description'] for step in self.steps]

                current = current.next
                position += 1

            # 未找到目标节点
            raise ValueError(f"未找到值为 {target_val} 的节点")

        except Exception as e:
            self.add_step(f"插入失败 - {str(e)}", "error")
            return False, [step['description'] for step in self.steps]

    def search_value(self, val):
        """
        查找指定值的节点

        Args:
            val: 要查找的值

        Returns:
            tuple: (是否找到, 位置, 详细步骤列表)
        """
        self.clear_steps()

        try:
            if self.is_empty():
                self.add_step("链表为空，无法查找", "warning")
                return False, -1, [step['description'] for step in self.steps]

            self.add_step(f"开始查找值为 {val} 的节点", "info")

            current = self.head
            position = 0

            # 遍历查找
            while current is not None:
                self.add_step(f"检查位置 {position} 的节点 (值为 {current.val})",
                              "info", highlight_nodes=[position])

                if current.val == val:
                    self.add_step(f"找到目标节点！位置: {position}, 值: {val}",
                                  "success", highlight_nodes=[position])
                    return True, position, [step['description'] for step in self.steps]

                current = current.next
                position += 1

            self.add_step(f"遍历完成，未找到值为 {val} 的节点", "warning")
            return False, -1, [step['description'] for step in self.steps]

        except Exception as e:
            self.add_step(f"查找失败 - {str(e)}", "error")
            return False, -1, [step['description'] for step in self.steps]

    # 保持原有的删除方法不变，但增加可视化支持
    def delete_head(self):
        """删除头节点"""
        self.clear_steps()

        try:
            if self.is_empty():
                raise ValueError("链表为空，无法删除头节点")

            deleted_val = self.head.val
            self.add_step(f"准备删除头节点，当前头节点值为 {deleted_val}", "info", highlight_nodes=[0])

            if self.head.next is None:
                self.add_step(f"链表只有一个节点，删除后链表将为空", "info")
                self.head = None
            else:
                self.add_step(f"保存头节点的下一个节点 (值为 {self.head.next.val})", "info",
                              highlight_nodes=[0, 1], highlight_pointers=["head->next"])
                self.add_step(f"更新头指针指向下一个节点", "info", highlight_nodes=[1])
                self.head = self.head.next

            self.size -= 1
            self.add_step(f"删除完成，链表长度变为 {self.size}", "success")

            return True, deleted_val, [step['description'] for step in self.steps]

        except Exception as e:
            self.add_step(f"删除失败 - {str(e)}", "error")
            return False, None, [step['description'] for step in self.steps]

    def delete_tail(self):
        """删除尾节点"""
        self.clear_steps()

        try:
            if self.is_empty():
                raise ValueError("链表为空，无法删除尾节点")

            # 特殊情况：只有一个节点
            if self.head.next is None:
                deleted_val = self.head.val
                self.add_step(f"链表只有一个节点 (值为 {deleted_val})", "info", highlight_nodes=[0])
                self.add_step(f"直接删除头节点", "info")
                self.head = None
                self.size -= 1
                self.add_step(f"删除完成，链表现在为空", "success")
                return True, deleted_val, [step['description'] for step in self.steps]

            self.add_step(f"准备删除尾节点", "info")
            self.add_step(f"遍历链表寻找倒数第二个节点", "info")

            current = self.head
            position = 0

            # 找到倒数第二个节点
            while current.next.next is not None:
                self.add_step(f"访问位置 {position} 的节点 (值为 {current.val})",
                              "info", highlight_nodes=[position])
                current = current.next
                position += 1

            deleted_val = current.next.val
            self.add_step(f"找到倒数第二个节点 (值为 {current.val}) 在位置 {position}",
                          "info", highlight_nodes=[position])
            self.add_step(f"尾节点值为 {deleted_val} 在位置 {position + 1}",
                          "info", highlight_nodes=[position, position + 1])
            self.add_step(f"将倒数第二个节点的 next 指针设为 NULL", "info",
                          highlight_nodes=[position], highlight_pointers=["prev->null"])

            current.next = None
            self.size -= 1

            self.add_step(f"删除完成，链表长度变为 {self.size}", "success")

            return True, deleted_val, [step['description'] for step in self.steps]

        except Exception as e:
            self.add_step(f"删除失败 - {str(e)}", "error")
            return False, None, [step['description'] for step in self.steps]

    def delete_by_value(self, val):
        """按值删除节点（删除第一个匹配的节点）"""
        self.clear_steps()

        try:
            if self.is_empty():
                raise ValueError("链表为空，无法删除")

            self.add_step(f"准备删除值为 {val} 的节点", "info")
            self.add_step(f"遍历链表查找目标节点", "info")

            # 特殊情况：删除头节点
            if self.head.val == val:
                self.add_step(f"在位置 0 找到目标节点 (头节点)", "info", highlight_nodes=[0])
                success, deleted_val, steps = self.delete_head()
                return success, 0, steps

            current = self.head
            position = 0

            # 遍历查找目标节点
            while current.next is not None:
                position += 1
                self.add_step(f"检查位置 {position} 的节点 (值为 {current.next.val})",
                              "info", highlight_nodes=[position - 1, position])

                if current.next.val == val:
                    self.add_step(f"在位置 {position} 找到目标节点", "info",
                                  highlight_nodes=[position])
                    self.add_step(f"调整前一个节点的指针跳过目标节点", "info",
                                  highlight_nodes=[position - 1, position, position + 1 if current.next.next else -1],
                                  highlight_pointers=["prev->next"])

                    # 删除节点
                    current.next = current.next.next
                    self.size -= 1

                    self.add_step(f"删除完成，链表长度变为 {self.size}", "success")

                    return True, position, [step['description'] for step in self.steps]

                current = current.next

            # 未找到目标节点
            raise ValueError(f"未找到值为 {val} 的节点")

        except Exception as e:
            self.add_step(f"删除失败 - {str(e)}", "error")
            return False, -1, [step['description'] for step in self.steps]

    def delete_at_position(self, position):
        """按位置删除节点"""
        self.clear_steps()

        try:
            if self.is_empty():
                raise ValueError("链表为空，无法删除")

            # 验证位置有效性
            if position < 0 or position >= self.size:
                raise ValueError(f"位置 {position} 超出有效范围 [0, {self.size - 1}]")

            self.add_step(f"准备删除位置 {position} 的节点", "info")
            self.add_step(f"位置验证通过，当前链表长度为 {self.size}", "info")

            # 特殊情况：删除头节点
            if position == 0:
                self.add_step(f"位置为0，转为删除头节点操作", "info")
                return self.delete_head()

            self.add_step(f"遍历到位置 {position - 1}", "info")
            current = self.head

            # 遍历到目标位置的前一个节点
            for i in range(position - 1):
                self.add_step(f"访问位置 {i} 的节点 (值为 {current.val})",
                              "info", highlight_nodes=[i])
                current = current.next

            deleted_val = current.next.val
            self.add_step(f"到达位置 {position - 1}，目标节点值为 {deleted_val}",
                          "info", highlight_nodes=[position - 1, position])
            self.add_step(f"调整指针跳过目标节点", "info",
                          highlight_nodes=[position - 1, position, position + 1 if current.next.next else -1],
                          highlight_pointers=["prev->next"])

            # 删除节点
            current.next = current.next.next
            self.size -= 1

            self.add_step(f"删除完成，链表长度变为 {self.size}", "success")

            return True, deleted_val, [step['description'] for step in self.steps]

        except Exception as e:
            self.add_step(f"删除失败 - {str(e)}", "error")
            return False, None, [step['description'] for step in self.steps]

    def find_by_value(self, val):
        """按值查找节点"""
        current = self.head
        position = 0

        while current is not None:
            if current.val == val:
                return position
            current = current.next
            position += 1

        return -1

    def get_at_position(self, position):
        """获取指定位置的节点值"""
        if position < 0 or position >= self.size:
            return None

        current = self.head
        for i in range(position):
            current = current.next

        return current.val

    def get_info(self):
        """获取链表的详细信息"""
        return {
            'length': self.size,
            'is_empty': self.is_empty(),
            'head_value': self.head.val if self.head else None,
            'tail_value': self.get_at_position(self.size - 1) if self.size > 0 else None,
            'as_list': self.to_list(),
            'display': self.display()
        }

    def get_steps_with_animation_data(self):
        """获取包含动画数据的步骤信息"""
        return self.steps