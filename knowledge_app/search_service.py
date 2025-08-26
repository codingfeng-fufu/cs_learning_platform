import re
from django.db.models import Q, F
from django.utils import timezone
from datetime import timedelta
from .search_models import (
    SearchHistory, PopularSearch, SearchSuggestion,
    KnowledgePointIndex, SearchFilter
)
import logging

logger = logging.getLogger(__name__)

class SearchService:
    """搜索服务类"""
    
    @staticmethod
    def search_knowledge_points(query, filters=None, sort_by='relevance', limit=20):
        """搜索知识点"""
        try:
            if not query or len(query.strip()) < 1:
                return []

            query = query.strip()

            # 动态导入避免循环导入
            from .views import get_cs_universe_knowledge_points

            # 获取所有知识点数据
            all_points = get_cs_universe_knowledge_points()
            
            # 执行搜索匹配
            results = []
            for point in all_points:
                score = SearchService._calculate_relevance_score(point, query)
                if score > 0:
                    point['search_score'] = score
                    results.append(point)
            
            # 应用过滤器
            if filters:
                results = SearchService._apply_filters(results, filters)
            
            # 排序
            results = SearchService._sort_results(results, sort_by)
            
            # 限制结果数量
            results = results[:limit]
            
            # 记录搜索历史
            SearchService._record_search(query, len(results))
            
            return results
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []
    
    @staticmethod
    def _calculate_relevance_score(point, query):
        """计算相关性得分"""
        score = 0
        query_lower = query.lower()
        
        # 标题匹配（权重最高）
        title_lower = point['title'].lower()
        if query_lower in title_lower:
            score += 100
            if title_lower.startswith(query_lower):
                score += 50
            if title_lower == query_lower:
                score += 100
        
        # 描述匹配
        description_lower = point['description'].lower()
        if query_lower in description_lower:
            score += 60
        
        # 分类匹配
        category_lower = point['category'].lower()
        category_display_lower = point['category_display'].lower()
        if query_lower in category_lower or query_lower in category_display_lower:
            score += 40
        
        # 关键词匹配（模糊匹配）
        keywords = [
            '数据结构', '算法', '网络', '操作系统', '数据库', '软件工程',
            '链表', '栈', '队列', '树', '图', '排序', '查找',
            'tcp', 'ip', 'http', 'sql', 'linux', 'windows'
        ]
        
        for keyword in keywords:
            if query_lower in keyword.lower() or keyword.lower() in query_lower:
                score += 20
        
        # 字符相似度匹配
        if SearchService._fuzzy_match(query_lower, title_lower):
            score += 30
        
        # 考虑实现状态
        if point['is_implemented']:
            score += 10
        
        return score
    
    @staticmethod
    def _fuzzy_match(query, text, threshold=0.6):
        """模糊匹配"""
        if len(query) < 2:
            return False
        
        # 简单的字符包含度计算
        matches = 0
        for char in query:
            if char in text:
                matches += 1
        
        similarity = matches / len(query)
        return similarity >= threshold
    
    @staticmethod
    def _apply_filters(results, filters):
        """应用搜索过滤器"""
        filtered_results = results
        
        for filter_type, filter_value in filters.items():
            if filter_type == 'category' and filter_value:
                filtered_results = [r for r in filtered_results if r['category'] == filter_value]
            elif filter_type == 'difficulty' and filter_value:
                filtered_results = [r for r in filtered_results if r['difficulty'] == filter_value]
            elif filter_type == 'implemented' and filter_value is not None:
                filtered_results = [r for r in filtered_results if r['is_implemented'] == filter_value]
        
        return filtered_results
    
    @staticmethod
    def _sort_results(results, sort_by):
        """排序搜索结果"""
        if sort_by == 'relevance':
            return sorted(results, key=lambda x: x.get('search_score', 0), reverse=True)
        elif sort_by == 'title':
            return sorted(results, key=lambda x: x['title'])
        elif sort_by == 'category':
            return sorted(results, key=lambda x: (x['category'], x['title']))
        elif sort_by == 'difficulty':
            difficulty_order = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
            return sorted(results, key=lambda x: (difficulty_order.get(x['difficulty'], 0), x['title']))
        else:
            return results
    
    @staticmethod
    def _record_search(query, results_count, user=None, request=None):
        """记录搜索历史"""
        try:
            # 记录用户搜索历史
            search_data = {
                'query': query,
                'results_count': results_count,
            }
            
            if user and user.is_authenticated:
                search_data['user'] = user
            
            if request:
                search_data['ip_address'] = SearchService._get_client_ip(request)
                search_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
            
            SearchHistory.objects.create(**search_data)
            
            # 更新热门搜索
            popular_search, created = PopularSearch.objects.get_or_create(
                query=query,
                defaults={'search_count': 1}
            )
            if not created:
                popular_search.search_count = F('search_count') + 1
                popular_search.save()
            
        except Exception as e:
            logger.error(f"记录搜索历史失败: {e}")
    
    @staticmethod
    def _get_client_ip(request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def get_search_suggestions(query, limit=10):
        """获取搜索建议"""
        suggestions = []

        if not query or len(query) < 1:
            return suggestions

        try:
            # 动态导入避免循环导入
            from .views import get_cs_universe_knowledge_points

            # 自动补全建议
            all_points = get_cs_universe_knowledge_points()
            for point in all_points:
                if point['title'].lower().startswith(query.lower()):
                    suggestions.append({
                        'text': point['title'],
                        'type': 'completion',
                        'category': point['category_display']
                    })
                    if len(suggestions) >= limit // 2:
                        break
            
            # 相关搜索建议
            for point in all_points:
                if (query.lower() in point['title'].lower() and 
                    not point['title'].lower().startswith(query.lower())):
                    suggestions.append({
                        'text': point['title'],
                        'type': 'related',
                        'category': point['category_display']
                    })
                    if len(suggestions) >= limit:
                        break
            
            return suggestions[:limit]
            
        except Exception as e:
            logger.error(f"获取搜索建议失败: {e}")
            return []
    
    @staticmethod
    def get_popular_searches(limit=10):
        """获取热门搜索"""
        try:
            # 获取最近7天的热门搜索
            week_ago = timezone.now() - timedelta(days=7)
            popular = PopularSearch.objects.filter(
                last_searched__gte=week_ago
            ).order_by('-search_count')[:limit]
            
            return [{'query': p.query, 'count': p.search_count} for p in popular]
            
        except Exception as e:
            logger.error(f"获取热门搜索失败: {e}")
            return []
    
    @staticmethod
    def get_user_search_history(user, limit=10):
        """获取用户搜索历史"""
        try:
            if not user or not user.is_authenticated:
                return []
            
            history = SearchHistory.objects.filter(
                user=user
            ).values('query', 'search_time').distinct().order_by('-search_time')[:limit]
            
            return list(history)
            
        except Exception as e:
            logger.error(f"获取用户搜索历史失败: {e}")
            return []
    
    @staticmethod
    def get_search_filters():
        """获取搜索过滤器选项"""
        return {
            'categories': [
                {'value': 'data_structures', 'label': '数据结构'},
                {'value': 'algorithm_design', 'label': '算法设计'},
                {'value': 'computer_networks', 'label': '计算机网络'},
                {'value': 'operating_systems', 'label': '操作系统'},
                {'value': 'database_systems', 'label': '数据库系统'},
                {'value': 'software_engineering', 'label': '软件工程'},
            ],
            'difficulties': [
                {'value': 'beginner', 'label': '初级'},
                {'value': 'intermediate', 'label': '中级'},
                {'value': 'advanced', 'label': '高级'},
            ],
            'status': [
                {'value': True, 'label': '已实现'},
                {'value': False, 'label': '开发中'},
            ]
        }
    
    @staticmethod
    def clear_user_search_history(user):
        """清除用户搜索历史"""
        try:
            if user and user.is_authenticated:
                SearchHistory.objects.filter(user=user).delete()
                return True
        except Exception as e:
            logger.error(f"清除搜索历史失败: {e}")
        return False
