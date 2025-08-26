"""
知识图谱服务层
"""

import json
import math
import random
from typing import Dict, List, Tuple, Optional
from django.db.models import Q, Count, Avg
from django.contrib.auth import get_user_model
from ..knowledge_graph_models import (
    ConceptNode, ConceptRelation, LearningPath, 
    PathStep, UserLearningProgress
)

User = get_user_model()


class KnowledgeGraphService:
    """知识图谱服务"""
    
    def __init__(self):
        self.layout_algorithms = {
            'force_directed': self._force_directed_layout,
            'hierarchical': self._hierarchical_layout,
            'circular': self._circular_layout,
        }
    
    def get_graph_data(self, category=None, max_nodes=50, layout='force_directed'):
        """获取图谱数据"""
        # 获取概念节点
        concepts_query = ConceptNode.objects.filter(is_active=True)
        if category:
            concepts_query = concepts_query.filter(category=category)
        
        concepts = concepts_query.order_by('-importance_weight')[:max_nodes]
        
        # 获取关系
        concept_ids = [c.id for c in concepts]
        relations = ConceptRelation.objects.filter(
            source_concept_id__in=concept_ids,
            target_concept_id__in=concept_ids,
            is_active=True
        ).select_related('source_concept', 'target_concept')
        
        # 构建图谱数据
        nodes = []
        edges = []
        
        # 处理节点
        for concept in concepts:
            node_data = {
                'id': concept.id,
                'name': concept.name,
                'category': concept.category,
                'difficulty': concept.difficulty,
                'description': concept.description[:100] + '...' if len(concept.description) > 100 else concept.description,
                'importance': concept.importance_weight,
                'view_count': concept.view_count,
                'learn_count': concept.learn_count,
            }
            nodes.append(node_data)
        
        # 处理边
        for relation in relations:
            edge_data = {
                'source': relation.source_concept.id,
                'target': relation.target_concept.id,
                'type': relation.relation_type,
                'strength': relation.strength,
                'description': relation.description,
            }
            edges.append(edge_data)
        
        # 应用布局算法
        if layout in self.layout_algorithms:
            nodes = self.layout_algorithms[layout](nodes, edges)
        
        return {
            'nodes': nodes,
            'edges': edges,
            'stats': {
                'total_nodes': len(nodes),
                'total_edges': len(edges),
                'categories': list(set(node['category'] for node in nodes)),
            }
        }
    
    def _force_directed_layout(self, nodes, edges):
        """力导向布局算法"""
        # 简化的力导向布局
        node_positions = {}
        
        # 初始化随机位置
        for node in nodes:
            node_positions[node['id']] = {
                'x': random.uniform(-500, 500),
                'y': random.uniform(-500, 500)
            }
        
        # 迭代优化位置
        for iteration in range(50):
            forces = {node_id: {'x': 0, 'y': 0} for node_id in node_positions}
            
            # 计算排斥力
            for i, node1_id in enumerate(node_positions):
                for j, node2_id in enumerate(node_positions):
                    if i >= j:
                        continue
                    
                    pos1 = node_positions[node1_id]
                    pos2 = node_positions[node2_id]
                    
                    dx = pos1['x'] - pos2['x']
                    dy = pos1['y'] - pos2['y']
                    distance = math.sqrt(dx*dx + dy*dy) or 1
                    
                    # 排斥力
                    repulsion = 10000 / (distance * distance)
                    fx = (dx / distance) * repulsion
                    fy = (dy / distance) * repulsion
                    
                    forces[node1_id]['x'] += fx
                    forces[node1_id]['y'] += fy
                    forces[node2_id]['x'] -= fx
                    forces[node2_id]['y'] -= fy
            
            # 计算吸引力（基于边）
            for edge in edges:
                source_id = edge['source']
                target_id = edge['target']
                
                if source_id in node_positions and target_id in node_positions:
                    pos1 = node_positions[source_id]
                    pos2 = node_positions[target_id]
                    
                    dx = pos2['x'] - pos1['x']
                    dy = pos2['y'] - pos1['y']
                    distance = math.sqrt(dx*dx + dy*dy) or 1
                    
                    # 吸引力
                    attraction = distance * 0.01 * edge['strength']
                    fx = (dx / distance) * attraction
                    fy = (dy / distance) * attraction
                    
                    forces[source_id]['x'] += fx
                    forces[source_id]['y'] += fy
                    forces[target_id]['x'] -= fx
                    forces[target_id]['y'] -= fy
            
            # 应用力并更新位置
            for node_id in node_positions:
                node_positions[node_id]['x'] += forces[node_id]['x'] * 0.1
                node_positions[node_id]['y'] += forces[node_id]['y'] * 0.1
        
        # 更新节点位置
        for node in nodes:
            pos = node_positions[node['id']]
            node['x'] = pos['x']
            node['y'] = pos['y']
        
        return nodes
    
    def _hierarchical_layout(self, nodes, edges):
        """层次布局算法"""
        # 根据难度等级分层
        difficulty_levels = ['beginner', 'intermediate', 'advanced', 'expert']
        layers = {level: [] for level in difficulty_levels}
        
        for node in nodes:
            layers[node['difficulty']].append(node)
        
        # 分配位置
        y_positions = {
            'beginner': -300,
            'intermediate': -100,
            'advanced': 100,
            'expert': 300,
        }
        
        for level, level_nodes in layers.items():
            if not level_nodes:
                continue
            
            y = y_positions[level]
            total_width = len(level_nodes) * 150
            start_x = -total_width / 2
            
            for i, node in enumerate(level_nodes):
                node['x'] = start_x + i * 150
                node['y'] = y
        
        return nodes
    
    def _circular_layout(self, nodes, edges):
        """圆形布局算法"""
        center_x, center_y = 0, 0
        radius = 300
        
        for i, node in enumerate(nodes):
            angle = 2 * math.pi * i / len(nodes)
            node['x'] = center_x + radius * math.cos(angle)
            node['y'] = center_y + radius * math.sin(angle)
        
        return nodes
    
    def get_concept_details(self, concept_id, user=None):
        """获取概念详细信息"""
        try:
            concept = ConceptNode.objects.get(id=concept_id, is_active=True)
        except ConceptNode.DoesNotExist:
            return None
        
        # 获取相关概念
        related_concepts = self._get_related_concepts(concept)
        
        # 获取学习路径
        learning_paths = self._get_concept_learning_paths(concept)
        
        # 获取用户进度（如果用户已登录）
        user_progress = None
        if user and user.is_authenticated:
            try:
                progress = UserLearningProgress.objects.get(
                    user=user, concept=concept
                )
                user_progress = {
                    'status': progress.status,
                    'mastery_level': progress.mastery_level,
                    'total_study_time': progress.total_study_time,
                    'study_sessions': progress.study_sessions,
                    'last_studied_at': progress.last_studied_at,
                }
            except UserLearningProgress.DoesNotExist:
                pass
        
        return {
            'concept': {
                'id': concept.id,
                'name': concept.name,
                'name_en': concept.name_en,
                'description': concept.description,
                'category': concept.category,
                'difficulty': concept.difficulty,
                'importance_weight': concept.importance_weight,
                'keywords': concept.keywords,
                'examples': concept.examples,
                'resources': concept.resources,
                'view_count': concept.view_count,
                'learn_count': concept.learn_count,
            },
            'related_concepts': related_concepts,
            'learning_paths': learning_paths,
            'user_progress': user_progress,
        }
    
    def _get_related_concepts(self, concept):
        """获取相关概念"""
        relations = ConceptRelation.objects.filter(
            Q(source_concept=concept) | Q(target_concept=concept),
            is_active=True
        ).select_related('source_concept', 'target_concept')
        
        related = []
        for relation in relations:
            if relation.source_concept == concept:
                related_concept = relation.target_concept
                direction = 'outgoing'
            else:
                related_concept = relation.source_concept
                direction = 'incoming'
            
            related.append({
                'concept': {
                    'id': related_concept.id,
                    'name': related_concept.name,
                    'category': related_concept.category,
                    'difficulty': related_concept.difficulty,
                },
                'relation_type': relation.relation_type,
                'strength': relation.strength,
                'direction': direction,
                'description': relation.description,
            })
        
        return related
    
    def _get_concept_learning_paths(self, concept):
        """获取包含该概念的学习路径"""
        paths = LearningPath.objects.filter(
            concepts=concept,
            is_public=True
        ).annotate(
            step_count=Count('concepts')
        ).order_by('-is_featured', '-follower_count')[:5]
        
        path_data = []
        for path in paths:
            # 获取概念在路径中的位置
            try:
                step = PathStep.objects.get(learning_path=path, concept=concept)
                step_info = {
                    'order': step.order,
                    'is_required': step.is_required,
                    'estimated_time': step.estimated_time,
                }
            except PathStep.DoesNotExist:
                step_info = None
            
            path_data.append({
                'id': path.id,
                'name': path.name,
                'description': path.description,
                'difficulty_level': path.difficulty_level,
                'estimated_hours': path.estimated_hours,
                'follower_count': path.follower_count,
                'step_count': path.step_count,
                'step_info': step_info,
            })
        
        return path_data
    
    def get_learning_recommendations(self, user, limit=10):
        """获取学习推荐"""
        if not user.is_authenticated:
            # 未登录用户返回热门概念
            return self._get_popular_concepts(limit)
        
        # 获取用户已学习的概念
        learned_concepts = UserLearningProgress.objects.filter(
            user=user,
            status__in=['completed', 'mastered']
        ).values_list('concept_id', flat=True)
        
        # 获取推荐概念
        recommendations = []
        
        # 1. 基于已学概念的相关概念
        if learned_concepts:
            related_concepts = ConceptRelation.objects.filter(
                source_concept_id__in=learned_concepts,
                is_active=True
            ).exclude(
                target_concept_id__in=learned_concepts
            ).select_related('target_concept').order_by('-strength')[:limit//2]
            
            for relation in related_concepts:
                recommendations.append({
                    'concept': self._concept_to_dict(relation.target_concept),
                    'reason': f'与已学概念"{relation.source_concept.name}"相关',
                    'score': relation.strength,
                })
        
        # 2. 基于用户兴趣的热门概念
        remaining_slots = limit - len(recommendations)
        if remaining_slots > 0:
            popular = self._get_popular_concepts(remaining_slots, exclude=learned_concepts)
            for concept_data in popular:
                recommendations.append({
                    'concept': concept_data,
                    'reason': '热门推荐',
                    'score': concept_data['importance_weight'],
                })
        
        return recommendations
    
    def _get_popular_concepts(self, limit, exclude=None):
        """获取热门概念"""
        query = ConceptNode.objects.filter(is_active=True)
        if exclude:
            query = query.exclude(id__in=exclude)
        
        concepts = query.order_by('-importance_weight', '-view_count')[:limit]
        return [self._concept_to_dict(concept) for concept in concepts]
    
    def _concept_to_dict(self, concept):
        """将概念对象转换为字典"""
        return {
            'id': concept.id,
            'name': concept.name,
            'name_en': concept.name_en,
            'description': concept.description[:100] + '...' if len(concept.description) > 100 else concept.description,
            'category': concept.category,
            'difficulty': concept.difficulty,
            'importance_weight': concept.importance_weight,
            'view_count': concept.view_count,
            'learn_count': concept.learn_count,
        }
    
    def update_concept_stats(self, concept_id, action='view'):
        """更新概念统计信息"""
        try:
            concept = ConceptNode.objects.get(id=concept_id)
            if action == 'view':
                concept.view_count += 1
            elif action == 'learn':
                concept.learn_count += 1
            concept.save(update_fields=[f'{action}_count'])
        except ConceptNode.DoesNotExist:
            pass
    
    def record_user_learning(self, user, concept_id, study_time_minutes=0):
        """记录用户学习行为"""
        if not user.is_authenticated:
            return None
        
        try:
            concept = ConceptNode.objects.get(id=concept_id, is_active=True)
        except ConceptNode.DoesNotExist:
            return None
        
        # 获取或创建学习进度记录
        progress, created = UserLearningProgress.objects.get_or_create(
            user=user,
            concept=concept,
            defaults={'status': 'not_started'}
        )
        
        # 更新进度
        progress.update_progress(study_time_minutes)
        
        # 更新概念统计
        self.update_concept_stats(concept_id, 'learn')
        
        return {
            'status': progress.status,
            'mastery_level': progress.mastery_level,
            'total_study_time': progress.total_study_time,
            'study_sessions': progress.study_sessions,
        }
