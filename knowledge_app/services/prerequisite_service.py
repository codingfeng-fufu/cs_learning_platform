"""
前置知识服务
处理知识点的前置关系和拓扑排序
"""

from collections import defaultdict, deque
from typing import List, Dict, Set, Tuple, Optional
from django.db.models import Q
from ..knowledge_graph_models import ConceptNode, ConceptRelation


class PrerequisiteService:
    """前置知识服务"""
    
    def __init__(self):
        self.graph = defaultdict(list)  # 邻接表
        self.reverse_graph = defaultdict(list)  # 反向邻接表
        self.in_degree = defaultdict(int)  # 入度
        self.concept_map = {}  # ID到概念的映射
    
    def build_prerequisite_graph(self, category=None):
        """构建前置知识图"""
        # 获取概念节点
        concepts_query = ConceptNode.objects.filter(is_active=True)
        if category:
            concepts_query = concepts_query.filter(category=category)
        
        concepts = list(concepts_query)
        
        # 初始化
        self.graph.clear()
        self.reverse_graph.clear()
        self.in_degree.clear()
        self.concept_map.clear()
        
        # 建立概念映射
        for concept in concepts:
            self.concept_map[concept.id] = concept
            self.in_degree[concept.id] = 0
        
        # 获取前置关系
        concept_ids = [c.id for c in concepts]
        relations = ConceptRelation.objects.filter(
            source_concept_id__in=concept_ids,
            target_concept_id__in=concept_ids,
            relation_type='prerequisite',  # 只考虑前置关系
            is_active=True
        )
        
        # 构建图
        for relation in relations:
            source_id = relation.source_concept_id
            target_id = relation.target_concept_id
            
            # source是target的前置条件
            self.graph[source_id].append(target_id)
            self.reverse_graph[target_id].append(source_id)
            self.in_degree[target_id] += 1
    
    def topological_sort(self, category=None) -> List[ConceptNode]:
        """拓扑排序，返回学习顺序"""
        self.build_prerequisite_graph(category)
        
        # Kahn算法进行拓扑排序
        queue = deque()
        result = []
        
        # 找到所有入度为0的节点
        for concept_id in self.in_degree:
            if self.in_degree[concept_id] == 0:
                queue.append(concept_id)
        
        while queue:
            current_id = queue.popleft()
            result.append(self.concept_map[current_id])
            
            # 遍历当前节点的所有后继节点
            for next_id in self.graph[current_id]:
                self.in_degree[next_id] -= 1
                if self.in_degree[next_id] == 0:
                    queue.append(next_id)
        
        # 检查是否有环
        if len(result) != len(self.concept_map):
            # 存在环，返回部分排序结果
            remaining = [concept for concept_id, concept in self.concept_map.items() 
                        if concept not in result]
            result.extend(remaining)
        
        return result
    
    def get_prerequisites(self, concept_id: int) -> List[ConceptNode]:
        """获取指定概念的所有前置知识"""
        if concept_id not in self.concept_map:
            return []
        
        visited = set()
        prerequisites = []
        
        def dfs(node_id):
            if node_id in visited:
                return
            visited.add(node_id)
            
            for prereq_id in self.reverse_graph[node_id]:
                prerequisites.append(self.concept_map[prereq_id])
                dfs(prereq_id)
        
        dfs(concept_id)
        return prerequisites
    
    def get_learning_sequence(self, target_concept_id: int) -> List[ConceptNode]:
        """获取学习指定概念所需的完整学习序列"""
        if target_concept_id not in self.concept_map:
            return []
        
        # 获取所有前置知识
        prerequisites = self.get_prerequisites(target_concept_id)
        prerequisites.append(self.concept_map[target_concept_id])
        
        # 对前置知识进行拓扑排序
        prereq_ids = [concept.id for concept in prerequisites]
        
        # 构建子图
        sub_graph = defaultdict(list)
        sub_in_degree = defaultdict(int)
        
        for concept_id in prereq_ids:
            sub_in_degree[concept_id] = 0
        
        for concept_id in prereq_ids:
            for next_id in self.graph[concept_id]:
                if next_id in prereq_ids:
                    sub_graph[concept_id].append(next_id)
                    sub_in_degree[next_id] += 1
        
        # 拓扑排序子图
        queue = deque()
        result = []
        
        for concept_id in sub_in_degree:
            if sub_in_degree[concept_id] == 0:
                queue.append(concept_id)
        
        while queue:
            current_id = queue.popleft()
            result.append(self.concept_map[current_id])
            
            for next_id in sub_graph[current_id]:
                sub_in_degree[next_id] -= 1
                if sub_in_degree[next_id] == 0:
                    queue.append(next_id)
        
        return result
    
    def get_next_concepts(self, learned_concepts: List[int]) -> List[ConceptNode]:
        """根据已学概念，推荐下一步可以学习的概念"""
        learned_set = set(learned_concepts)
        next_concepts = []
        
        for concept_id in self.concept_map:
            if concept_id in learned_set:
                continue
            
            # 检查是否所有前置条件都已满足
            prerequisites = self.reverse_graph[concept_id]
            if all(prereq_id in learned_set for prereq_id in prerequisites):
                next_concepts.append(self.concept_map[concept_id])
        
        # 按重要性权重排序
        next_concepts.sort(key=lambda x: x.importance_weight, reverse=True)
        return next_concepts
    
    def detect_cycles(self) -> List[List[ConceptNode]]:
        """检测知识图中的环"""
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node_id, path):
            if node_id in rec_stack:
                # 找到环
                cycle_start = path.index(node_id)
                cycle = path[cycle_start:] + [node_id]
                cycles.append([self.concept_map[cid] for cid in cycle])
                return
            
            if node_id in visited:
                return
            
            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)
            
            for next_id in self.graph[node_id]:
                dfs(next_id, path)
            
            rec_stack.remove(node_id)
            path.pop()
        
        for concept_id in self.concept_map:
            if concept_id not in visited:
                dfs(concept_id, [])
        
        return cycles
    
    def get_difficulty_progression(self, category=None) -> Dict[str, List[ConceptNode]]:
        """按难度等级组织学习路径"""
        concepts_query = ConceptNode.objects.filter(is_active=True)
        if category:
            concepts_query = concepts_query.filter(category=category)
        
        concepts = concepts_query.order_by('difficulty', 'importance_weight')
        
        progression = {
            'beginner': [],
            'intermediate': [],
            'advanced': [],
            'expert': []
        }
        
        for concept in concepts:
            progression[concept.difficulty].append(concept)
        
        return progression
    
    def generate_personalized_path(self, user, target_concepts: List[int]) -> Dict:
        """为用户生成个性化学习路径"""
        from ..knowledge_graph_models import UserLearningProgress
        
        # 获取用户已掌握的概念
        if user.is_authenticated:
            mastered_progress = UserLearningProgress.objects.filter(
                user=user,
                status__in=['completed', 'mastered']
            ).values_list('concept_id', flat=True)
            mastered_concepts = list(mastered_progress)
        else:
            mastered_concepts = []
        
        # 为每个目标概念生成学习序列
        all_required = set()
        sequences = {}
        
        for target_id in target_concepts:
            sequence = self.get_learning_sequence(target_id)
            sequences[target_id] = sequence
            all_required.update(concept.id for concept in sequence)
        
        # 移除已掌握的概念
        remaining_concepts = [
            concept_id for concept_id in all_required 
            if concept_id not in mastered_concepts
        ]
        
        # 生成最优学习顺序
        if remaining_concepts:
            # 构建包含所有需要学习概念的子图
            remaining_concept_objects = [
                self.concept_map[cid] for cid in remaining_concepts 
                if cid in self.concept_map
            ]
            
            # 按拓扑顺序排列
            ordered_concepts = []
            for concept in self.topological_sort():
                if concept.id in remaining_concepts:
                    ordered_concepts.append(concept)
        else:
            ordered_concepts = []
        
        # 估算学习时间（使用默认值）
        total_estimated_hours = len(ordered_concepts) * 2  # 假设每个概念2小时
        
        return {
            'path': ordered_concepts,
            'total_concepts': len(ordered_concepts),
            'estimated_hours': total_estimated_hours,
            'mastered_concepts': len(mastered_concepts),
            'target_concepts': target_concepts,
            'sequences': sequences
        }
    
    def get_concept_dependencies(self, concept_id: int) -> Dict:
        """获取概念的完整依赖信息"""
        if concept_id not in self.concept_map:
            return {}
        
        concept = self.concept_map[concept_id]
        
        # 直接前置条件
        direct_prerequisites = [
            self.concept_map[prereq_id] 
            for prereq_id in self.reverse_graph[concept_id]
        ]
        
        # 直接后续概念
        direct_dependents = [
            self.concept_map[dep_id] 
            for dep_id in self.graph[concept_id]
        ]
        
        # 所有前置条件（递归）
        all_prerequisites = self.get_prerequisites(concept_id)
        
        # 学习序列
        learning_sequence = self.get_learning_sequence(concept_id)
        
        return {
            'concept': concept,
            'direct_prerequisites': direct_prerequisites,
            'direct_dependents': direct_dependents,
            'all_prerequisites': all_prerequisites,
            'learning_sequence': learning_sequence,
            'position_in_sequence': len(learning_sequence),
            'difficulty_level': concept.difficulty,
            'estimated_time': 2  # 默认2小时
        }
