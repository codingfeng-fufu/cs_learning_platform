"""
计算机领域调度器
管理每日名词的领域分配，每两周轮换一个领域
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class ComputerDomainScheduler:
    """计算机领域调度器"""
    
    # 计算机科学领域配置（每两周一个领域）
    DOMAINS = [
        {
            'name': '数据结构',
            'english': 'Data Structures',
            'description': '数组、链表、栈、队列、树、图等基础数据结构',
            'keywords': ['数据结构', '算法', '数组', '链表', '栈', '队列', '树', '图', '哈希表', '堆'],
            'examples': ['二叉树', '红黑树', 'B+树', '哈希表', '并查集', '线段树', '字典树']
        },
        {
            'name': '计算机网络',
            'english': 'Computer Networks',
            'description': 'TCP/IP、HTTP、网络协议、网络安全等',
            'keywords': ['网络', '协议', 'TCP', 'UDP', 'HTTP', 'HTTPS', 'IP', '路由', '交换'],
            'examples': ['TCP三次握手', 'HTTP协议', 'DNS解析', 'CDN', '负载均衡', '防火墙']
        },
        {
            'name': '操作系统',
            'english': 'Operating Systems',
            'description': '进程管理、内存管理、文件系统、并发控制等',
            'keywords': ['操作系统', '进程', '线程', '内存', '文件系统', '调度', '同步', '死锁'],
            'examples': ['进程调度', '内存分页', '文件系统', '信号量', '互斥锁', '虚拟内存']
        },
        {
            'name': '数据库系统',
            'english': 'Database Systems',
            'description': '关系数据库、NoSQL、事务处理、查询优化等',
            'keywords': ['数据库', 'SQL', 'NoSQL', '事务', '索引', '查询', '优化', 'ACID'],
            'examples': ['关系模型', 'B+树索引', '事务隔离', '查询优化', 'MapReduce', '分布式数据库']
        },
        {
            'name': '机器学习',
            'english': 'Machine Learning',
            'description': '监督学习、无监督学习、深度学习、神经网络等',
            'keywords': ['机器学习', '深度学习', '神经网络', '算法', '模型', '训练', '预测'],
            'examples': ['线性回归', '决策树', '神经网络', '卷积神经网络', '循环神经网络', '强化学习']
        },
        {
            'name': '计算机视觉',
            'english': 'Computer Vision',
            'description': '图像处理、模式识别、目标检测、图像分析等',
            'keywords': ['计算机视觉', '图像处理', '模式识别', '目标检测', '特征提取', '深度学习'],
            'examples': ['图像分割', '目标检测', '人脸识别', '光学字符识别', '图像增强', '特征匹配']
        },
        {
            'name': '自然语言处理',
            'english': 'Natural Language Processing',
            'description': '文本分析、语言模型、机器翻译、情感分析等',
            'keywords': ['自然语言处理', 'NLP', '文本分析', '语言模型', '机器翻译', '情感分析'],
            'examples': ['词向量', '语言模型', '机器翻译', '情感分析', '命名实体识别', '文本摘要']
        },
        {
            'name': '软件工程',
            'english': 'Software Engineering',
            'description': '软件开发方法、设计模式、项目管理、质量保证等',
            'keywords': ['软件工程', '设计模式', '架构', '测试', '项目管理', '敏捷开发'],
            'examples': ['设计模式', '软件架构', '单元测试', '持续集成', '敏捷开发', '代码重构']
        },
        {
            'name': '信息安全',
            'english': 'Information Security',
            'description': '密码学、网络安全、系统安全、安全协议等',
            'keywords': ['信息安全', '密码学', '加密', '认证', '防护', '漏洞', '攻击'],
            'examples': ['对称加密', '非对称加密', '数字签名', '防火墙', '入侵检测', '漏洞扫描']
        },
        {
            'name': '分布式系统',
            'english': 'Distributed Systems',
            'description': '分布式计算、一致性、容错、微服务等',
            'keywords': ['分布式系统', '一致性', '容错', '负载均衡', '微服务', '集群'],
            'examples': ['分布式一致性', '负载均衡', '微服务架构', '容器化', '服务发现', '分布式锁']
        },
        {
            'name': '人工智能',
            'english': 'Artificial Intelligence',
            'description': '智能算法、专家系统、知识表示、推理等',
            'keywords': ['人工智能', 'AI', '智能算法', '专家系统', '知识表示', '推理', '搜索'],
            'examples': ['搜索算法', '专家系统', '知识图谱', '逻辑推理', '模糊逻辑', '遗传算法']
        },
        {
            'name': '计算机图形学',
            'english': 'Computer Graphics',
            'description': '图形渲染、3D建模、动画、可视化等',
            'keywords': ['计算机图形学', '渲染', '3D建模', '动画', '可视化', '图形处理'],
            'examples': ['光线追踪', '3D渲染', '纹理映射', '动画制作', '虚拟现实', '增强现实']
        },
        {
            'name': '人机交互',
            'english': 'Human-Computer Interaction',
            'description': '用户界面设计、交互设计、用户体验等',
            'keywords': ['人机交互', 'HCI', '用户界面', '交互设计', '用户体验', 'UI', 'UX'],
            'examples': ['用户界面设计', '交互原型', '可用性测试', '用户体验设计', '移动交互', '语音交互']
        },
        {
            'name': '编程语言理论',
            'english': 'Programming Language Theory',
            'description': '编程语言设计、编译原理、类型系统等',
            'keywords': ['编程语言', '编译原理', '类型系统', '语法分析', '语义分析', '代码生成'],
            'examples': ['编译器设计', '语法分析', '类型检查', '代码优化', '虚拟机', '解释器']
        }
    ]
    
    # 基准日期：2025年8月1日开始第一个周期
    BASE_DATE = date(2025, 8, 1)
    CYCLE_DAYS = 14  # 每个领域持续14天
    
    def __init__(self):
        self.domains = self.DOMAINS
        self.total_domains = len(self.domains)
    
    def get_current_domain(self, target_date: date = None) -> Dict:
        """获取指定日期的当前领域 - 每天轮换不同领域"""
        if target_date is None:
            target_date = datetime.now().date()

        # 计算从基准日期开始的天数
        days_since_base = (target_date - self.BASE_DATE).days

        # 如果是基准日期之前，使用第一个领域
        if days_since_base < 0:
            return self.domains[0]

        # 每天轮换一个领域：直接用天数对领域总数取模
        domain_index = days_since_base % self.total_domains

        return self.domains[domain_index]
    
    def get_domain_schedule(self, start_date: date = None, days: int = 30) -> List[Tuple[date, Dict]]:
        """获取指定时间段的领域调度表"""
        if start_date is None:
            start_date = datetime.now().date()
        
        schedule = []
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            domain = self.get_current_domain(current_date)
            schedule.append((current_date, domain))
        
        return schedule
    
    def get_domain_info(self, target_date: date = None) -> Dict:
        """获取详细的领域信息"""
        domain = self.get_current_domain(target_date)

        if target_date is None:
            target_date = datetime.now().date()

        # 计算从基准日期开始的天数
        days_since_base = (target_date - self.BASE_DATE).days

        # 计算当前是第几轮完整的14天周期
        full_cycle_number = days_since_base // self.total_domains

        # 计算在当前14天周期中的位置（第几天）
        day_in_cycle = (days_since_base % self.total_domains) + 1

        # 计算当前14天周期的开始和结束日期
        cycle_start = self.BASE_DATE + timedelta(days=full_cycle_number * self.total_domains)
        cycle_end = cycle_start + timedelta(days=self.total_domains - 1)

        return {
            'domain': domain,
            'cycle_number': full_cycle_number + 1,
            'cycle_start': cycle_start,
            'cycle_end': cycle_end,
            'day_in_cycle': day_in_cycle,
            'days_remaining': self.total_domains - day_in_cycle,
            'target_date': target_date
        }
    
    def build_domain_prompt(self, target_date: date = None) -> str:
        """构建针对当前领域的AI提示词"""
        domain_info = self.get_domain_info(target_date)
        domain = domain_info['domain']
        
        prompt = f"""
请生成一个关于"{domain['name']}"领域的计算机科学专业名词。

领域描述：{domain['description']}

要求：
1. 名词必须属于{domain['name']}领域
2. 适合计算机科学专业学生学习
3. 具有实际应用价值
4. 不要选择过于基础或过于高深的概念

参考关键词：{', '.join(domain['keywords'][:5])}
参考示例：{', '.join(domain['examples'][:3])}

请选择一个在该领域中重要且有代表性的专业名词。
"""
        return prompt.strip()
    
    def get_next_domain_change(self, target_date: date = None) -> Tuple[date, Dict]:
        """获取下一次领域变更的日期和新领域（每天都会变更）"""
        if target_date is None:
            target_date = datetime.now().date()

        # 下一天就是下一次领域变更
        next_change_date = target_date + timedelta(days=1)
        next_domain = self.get_current_domain(next_change_date)

        return next_change_date, next_domain


# 全局实例
domain_scheduler = ComputerDomainScheduler()


def get_current_domain_info(target_date: date = None) -> Dict:
    """获取当前领域信息的便捷函数"""
    return domain_scheduler.get_domain_info(target_date)


def build_domain_specific_prompt(target_date: date = None) -> str:
    """构建领域特定提示词的便捷函数"""
    return domain_scheduler.build_domain_prompt(target_date)
