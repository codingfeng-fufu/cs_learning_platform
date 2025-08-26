"""
个人题库分享功能视图
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.utils import timezone
from django.core.paginator import Paginator
from django.urls import reverse
from .personal_quiz_models import QuizLibrary, LibraryShare, LibraryCopy, QuizQuestion
import json
from datetime import datetime, timedelta

User = get_user_model()


@login_required
def share_library(request, library_id):
    """分享题库页面"""
    library = get_object_or_404(QuizLibrary, id=library_id, owner=request.user)
    
    if request.method == 'POST':
        share_type = request.POST.get('share_type')
        permission = request.POST.get('permission', 'view')
        message = request.POST.get('message', '')
        expires_days = request.POST.get('expires_days')
        
        # 计算过期时间
        expires_at = None
        if expires_days and expires_days.isdigit():
            expires_at = timezone.now() + timedelta(days=int(expires_days))
        
        try:
            with transaction.atomic():
                if share_type == 'private':
                    # 私密分享给特定用户
                    shared_to_username = request.POST.get('shared_to_username')
                    if not shared_to_username:
                        messages.error(request, '请输入要分享给的用户名')
                        return redirect('knowledge_app:share_library', library_id=library_id)
                    
                    try:
                        shared_to_user = User.objects.get(username=shared_to_username)
                    except User.DoesNotExist:
                        messages.error(request, f'用户 {shared_to_username} 不存在')
                        return redirect('knowledge_app:share_library', library_id=library_id)
                    
                    if shared_to_user == request.user:
                        messages.error(request, '不能分享给自己')
                        return redirect('knowledge_app:share_library', library_id=library_id)
                    
                    # 检查是否已经分享过
                    existing_share = LibraryShare.objects.filter(
                        library=library,
                        shared_by=request.user,
                        shared_to=shared_to_user,
                        is_active=True
                    ).first()
                    
                    if existing_share:
                        messages.warning(request, f'已经分享给 {shared_to_username} 了')
                        return redirect('knowledge_app:library_shares', library_id=library_id)
                    
                    share = LibraryShare.objects.create(
                        library=library,
                        shared_by=request.user,
                        shared_to=shared_to_user,
                        share_type=share_type,
                        permission=permission,
                        message=message,
                        expires_at=expires_at
                    )
                    
                    messages.success(request, f'成功分享给 {shared_to_username}')
                
                elif share_type in ['public', 'link']:
                    # 公开分享或链接分享
                    share = LibraryShare.objects.create(
                        library=library,
                        shared_by=request.user,
                        share_type=share_type,
                        permission=permission,
                        message=message,
                        expires_at=expires_at
                    )
                    
                    if share_type == 'link':
                        messages.success(request, f'生成分享链接成功，分享码：{share.share_code}')
                    else:
                        messages.success(request, '公开分享成功')
                
                return redirect('knowledge_app:library_shares', library_id=library_id)
                
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'分享创建失败: {str(e)}', exc_info=True)
            messages.error(request, f'分享失败：{str(e)}')
    
    # 获取所有用户（用于私密分享的用户选择）
    users = User.objects.exclude(id=request.user.id).order_by('username')[:50]
    
    context = {
        'library': library,
        'users': users,
    }
    
    return render(request, 'knowledge_app/quiz/share_library.html', context)


@login_required
def library_shares(request, library_id):
    """查看题库的分享记录"""
    library = get_object_or_404(QuizLibrary, id=library_id, owner=request.user)
    
    shares = LibraryShare.objects.filter(
        library=library,
        shared_by=request.user
    ).order_by('-created_at')
    
    context = {
        'library': library,
        'shares': shares,
    }
    
    return render(request, 'knowledge_app/quiz/library_shares.html', context)


@login_required
def received_shares(request):
    """查看收到的分享"""
    shares = LibraryShare.objects.filter(
        shared_to=request.user,
        is_active=True
    ).select_related('library', 'shared_by').order_by('-created_at')
    
    # 分页
    paginator = Paginator(shares, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'knowledge_app/quiz/received_shares.html', context)


def public_libraries(request):
    """查看公开的题库"""
    shares = LibraryShare.objects.filter(
        share_type='public',
        is_active=True
    ).select_related('library', 'shared_by').order_by('-created_at')
    
    # 搜索功能
    search = request.GET.get('search')
    if search:
        shares = shares.filter(library__name__icontains=search)
    
    # 分页
    paginator = Paginator(shares, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
    }
    
    return render(request, 'knowledge_app/quiz/public_libraries.html', context)


def shared_library_detail(request, share_code):
    """通过分享链接访问题库详情"""
    share = get_object_or_404(LibraryShare, share_code=share_code, is_active=True)
    
    # 检查访问权限
    if not share.can_access(request.user if request.user.is_authenticated else None):
        if share.is_expired():
            messages.error(request, '分享链接已过期')
        else:
            messages.error(request, '无权访问此分享')
        return redirect('knowledge_app:quiz_dashboard')
    
    # 记录访问
    share.record_access(request.user if request.user.is_authenticated else None)
    
    library = share.library
    questions = library.questions.filter(is_active=True).order_by('created_at')
    
    context = {
        'library': library,
        'share': share,
        'questions': questions,
        'can_copy': share.permission in ['copy', 'edit'],
        'can_edit': share.permission == 'edit' and request.user.is_authenticated,
    }
    
    return render(request, 'knowledge_app/quiz/shared_library_detail.html', context)


@login_required
@require_http_methods(["POST"])
def copy_shared_library(request, share_id):
    """复制分享的题库"""
    share = get_object_or_404(LibraryShare, id=share_id)
    
    # 检查权限
    if not share.can_access(request.user) or share.permission not in ['copy', 'edit']:
        return JsonResponse({'success': False, 'error': '无权复制此题库'})
    
    try:
        with transaction.atomic():
            original_library = share.library
            
            # 创建新题库
            new_library = QuizLibrary.objects.create(
                owner=request.user,
                name=f"{original_library.name} (副本)",
                description=f"复制自 {share.shared_by.username} 的题库：{original_library.description}",
            )
            
            # 复制题目
            questions = original_library.questions.filter(is_active=True)
            for question in questions:
                new_question = QuizQuestion.objects.create(
                    library=new_library,
                    title=question.title,
                    content=question.content,
                    question_type=question.question_type,
                    options=question.options,
                    correct_answer=question.correct_answer,
                    explanation=question.explanation,
                    difficulty=question.difficulty,
                )
                # 复制标签
                new_question.tags.set(question.tags.all())
            
            # 更新题目数量
            new_library.update_question_count()
            
            # 记录复制
            LibraryCopy.objects.create(
                original_library=original_library,
                copied_library=new_library,
                copied_by=request.user,
                share=share
            )
            
            return JsonResponse({
                'success': True,
                'message': '题库复制成功',
                'library_id': new_library.id,
                'redirect_url': reverse('knowledge_app:quiz_library_detail', args=[new_library.id])
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'复制失败：{str(e)}'})


@login_required
@require_http_methods(["POST"])
def toggle_share_status(request, share_id):
    """切换分享状态（启用/禁用）"""
    share = get_object_or_404(LibraryShare, id=share_id, shared_by=request.user)
    
    share.is_active = not share.is_active
    share.save()
    
    status = '启用' if share.is_active else '禁用'
    return JsonResponse({
        'success': True,
        'message': f'分享已{status}',
        'is_active': share.is_active
    })


@login_required
@require_http_methods(["POST"])
def delete_share(request, share_id):
    """删除分享"""
    share = get_object_or_404(LibraryShare, id=share_id, shared_by=request.user)
    
    share.delete()
    
    return JsonResponse({
        'success': True,
        'message': '分享已删除'
    })
