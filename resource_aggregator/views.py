"""
学习资源聚合器 - 视图层
独立的API接口，支持REST和GraphQL
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.utils.decorators import method_decorator
from django.views import View
import json
import logging

from .models import LearningResource, ResourceCategory, ResourceSource, UserResourceInteraction
from .services import sync_search_resources, aggregator_service

logger = logging.getLogger(__name__)


class ResourceSearchView(View):
    """资源搜索视图"""
    
    def get(self, request):
        """获取搜索页面"""
        categories = ResourceCategory.objects.all()
        sources = ResourceSource.objects.filter(is_active=True)
        
        context = {
            'categories': categories,
            'sources': sources,
            'page_title': '学习资源搜索'
        }
        return render(request, 'resource_aggregator/search.html', context)
    
    def post(self, request):
        """执行搜索"""
        try:
            data = json.loads(request.body)
            query = data.get('query', '').strip()
            category = data.get('category')
            platforms = data.get('platforms', [])
            limit = min(int(data.get('limit', 20)), 50)  # 限制最大50个结果
            
            if not query:
                return JsonResponse({'error': '搜索关键词不能为空'}, status=400)
            
            # 执行搜索
            results = sync_search_resources(query, category, platforms, limit)
            
            # 记录搜索历史（如果用户已登录）
            if request.user.is_authenticated:
                self._record_search_history(request.user, query, category)
            
            return JsonResponse({
                'success': True,
                'results': results,
                'total': len(results),
                'query': query
            })
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return JsonResponse({'error': '搜索失败，请稍后重试'}, status=500)
    
    def _record_search_history(self, user, query, category):
        """记录搜索历史"""
        # 这里可以添加搜索历史记录逻辑
        pass


@require_http_methods(["GET"])
def resource_list(request):
    """资源列表页面"""
    # 获取筛选参数
    category_slug = request.GET.get('category')
    resource_type = request.GET.get('type')
    difficulty = request.GET.get('difficulty')
    source_id = request.GET.get('source')
    search_query = request.GET.get('q', '').strip()
    
    # 构建查询
    resources = LearningResource.objects.filter(is_active=True)
    
    current_category_obj = None
    if category_slug:
        resources = resources.filter(category__slug=category_slug)
        try:
            current_category_obj = ResourceCategory.objects.get(slug=category_slug)
        except ResourceCategory.DoesNotExist:
            pass
    
    if resource_type:
        resources = resources.filter(resource_type=resource_type)
    
    if difficulty:
        resources = resources.filter(difficulty=difficulty)
    
    if source_id:
        resources = resources.filter(source_id=source_id)
    
    if search_query:
        resources = resources.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(author__icontains=search_query)
        )
    
    # 排序
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'newest':
        resources = resources.order_by('-created_at')
    elif sort_by == 'popular':
        resources = resources.order_by('-view_count', '-like_count')
    elif sort_by == 'name':
        resources = resources.order_by('title')
    
    # 分页
    paginator = Paginator(resources, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 获取筛选选项
    categories = ResourceCategory.objects.all()
    sources = ResourceSource.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'sources': sources,
        'current_category': category_slug,
        'current_category_obj': current_category_obj,
        'current_type': resource_type,
        'current_difficulty': difficulty,
        'current_source': source_id,
        'search_query': search_query,
        'sort_by': sort_by,
        'page_title': '🧰 实用工具箱'
    }
    
    return render(request, 'resource_aggregator/list.html', context)


@require_http_methods(["GET"])
def resource_detail(request, resource_id):
    """资源详情页面"""
    resource = get_object_or_404(LearningResource, id=resource_id, is_active=True)
    
    # 记录查看行为
    if request.user.is_authenticated:
        UserResourceInteraction.objects.get_or_create(
            user=request.user,
            resource=resource,
            action='view'
        )
    
    # 获取相关资源
    related_resources = LearningResource.objects.filter(
        category=resource.category,
        is_active=True
    ).exclude(id=resource.id).order_by('-rating')[:6]
    
    context = {
        'resource': resource,
        'related_resources': related_resources,
        'page_title': resource.title
    }
    
    return render(request, 'resource_aggregator/detail.html', context)


@login_required
@require_http_methods(["POST"])
def resource_interaction(request):
    """资源交互接口"""
    try:
        data = json.loads(request.body)
        resource_id = data.get('resource_id')
        action = data.get('action')
        
        if not resource_id or not action:
            return JsonResponse({'error': '参数不完整'}, status=400)
        
        resource = get_object_or_404(LearningResource, id=resource_id)
        
        # 记录交互
        interaction, created = UserResourceInteraction.objects.get_or_create(
            user=request.user,
            resource=resource,
            action=action
        )
        
        if not created and action in ['like', 'bookmark']:
            # 如果已存在，则删除（取消操作）
            interaction.delete()
            return JsonResponse({'success': True, 'action': f'un{action}'})
        
        return JsonResponse({'success': True, 'action': action})
        
    except Exception as e:
        logger.error(f"Interaction error: {e}")
        return JsonResponse({'error': '操作失败'}, status=500)


@require_http_methods(["GET"])
def api_categories(request):
    """分类API"""
    categories = ResourceCategory.objects.all().values(
        'id', 'name', 'slug', 'description', 'icon', 'color'
    )
    return JsonResponse({'categories': list(categories)})


@require_http_methods(["GET"])
def api_sources(request):
    """来源API"""
    sources = ResourceSource.objects.filter(is_active=True).values(
        'id', 'name', 'platform', 'base_url'
    )
    return JsonResponse({'sources': list(sources)})


@require_http_methods(["GET"])
def api_stats(request):
    """统计API"""
    stats = {
        'total_resources': LearningResource.objects.filter(is_active=True).count(),
        'total_categories': ResourceCategory.objects.count(),
        'total_sources': ResourceSource.objects.filter(is_active=True).count(),
        'resource_types': list(
            LearningResource.objects.filter(is_active=True)
            .values('resource_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        ),
        'top_categories': list(
            ResourceCategory.objects.annotate(
                resource_count=Count('learningresource')
            ).order_by('-resource_count')[:5]
            .values('name', 'resource_count')
        )
    }
    return JsonResponse(stats)


@login_required
@require_http_methods(["GET"])
def user_dashboard(request):
    """用户仪表板"""
    user = request.user
    
    # 用户统计
    user_stats = {
        'viewed_count': UserResourceInteraction.objects.filter(
            user=user, action='view'
        ).count(),
        'liked_count': UserResourceInteraction.objects.filter(
            user=user, action='like'
        ).count(),
        'bookmarked_count': UserResourceInteraction.objects.filter(
            user=user, action='bookmark'
        ).count(),
    }
    
    # 最近查看的资源
    recent_views = UserResourceInteraction.objects.filter(
        user=user, action='view'
    ).select_related('resource').order_by('-created_at')[:10]
    
    # 收藏的资源
    bookmarks = UserResourceInteraction.objects.filter(
        user=user, action='bookmark'
    ).select_related('resource').order_by('-created_at')[:10]
    
    context = {
        'user_stats': user_stats,
        'recent_views': recent_views,
        'bookmarks': bookmarks,
        'page_title': '我的学习资源'
    }
    
    return render(request, 'resource_aggregator/dashboard.html', context)


# 管理员功能
@login_required
@require_http_methods(["POST"])
def admin_sync_resources(request):
    """管理员同步资源"""
    if not request.user.is_staff:
        return JsonResponse({'error': '权限不足'}, status=403)
    
    try:
        data = json.loads(request.body)
        query = data.get('query', 'python programming')
        category_slug = data.get('category')
        limit = min(int(data.get('limit', 20)), 100)
        
        # 搜索并保存资源
        results = sync_search_resources(query, category_slug, None, limit)
        aggregator_service.save_resources_to_db(results, category_slug)
        
        return JsonResponse({
            'success': True,
            'message': f'成功同步 {len(results)} 个资源'
        })
        
    except Exception as e:
        logger.error(f"Sync error: {e}")
        return JsonResponse({'error': '同步失败'}, status=500)
