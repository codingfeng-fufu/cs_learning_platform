from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.contrib import messages
from .exercise_models import (
    ExerciseCategory, ExerciseDifficulty, Exercise, ExerciseSet,
    UserExerciseAttempt, UserExerciseSetAttempt
)
import json
import random
from datetime import timedelta

def exercise_home(request):
    """练习题首页"""
    # 获取分类
    categories = ExerciseCategory.objects.filter(is_active=True)
    
    # 获取推荐题目
    featured_exercises = Exercise.objects.filter(
        is_featured=True, is_active=True
    ).select_related('category', 'difficulty')[:6]
    
    # 获取热门题集
    popular_sets = ExerciseSet.objects.filter(
        is_active=True, is_public=True
    ).annotate(
        attempt_count=Count('userexercisesetattempt')
    ).order_by('-attempt_count')[:6]
    
    # 用户统计（如果已登录）
    user_stats = None
    global_stats = None

    if request.user.is_authenticated:
        user_attempts = UserExerciseAttempt.objects.filter(user=request.user)
        user_stats = {
            'total_attempts': user_attempts.count(),
            'correct_attempts': user_attempts.filter(is_correct=True).count(),
            'categories_practiced': user_attempts.values('exercise__category').distinct().count(),
        }
        if user_stats['total_attempts'] > 0:
            user_stats['success_rate'] = round(
                (user_stats['correct_attempts'] / user_stats['total_attempts']) * 100, 1
            )
        else:
            user_stats['success_rate'] = 0
    else:
        # 为未登录用户提供全局统计
        total_exercises = Exercise.objects.filter(is_active=True).count()
        total_sets = ExerciseSet.objects.filter(is_active=True, is_public=True).count()
        total_categories = ExerciseCategory.objects.filter(is_active=True).count()
        total_attempts = UserExerciseAttempt.objects.count()

        global_stats = {
            'total_exercises': total_exercises,
            'total_sets': total_sets,
            'total_categories': total_categories,
            'total_attempts': total_attempts,
        }
    
    context = {
        'categories': categories,
        'featured_exercises': featured_exercises,
        'popular_sets': popular_sets,
        'user_stats': user_stats,
        'global_stats': global_stats,
    }
    
    return render(request, 'knowledge_app/exercises/home.html', context)


def exercise_list(request):
    """练习题列表"""
    # 获取筛选参数
    category_slug = request.GET.get('category')
    difficulty_id = request.GET.get('difficulty')
    question_type = request.GET.get('type')
    search_query = request.GET.get('q')
    sort_by = request.GET.get('sort', 'created_at')
    
    # 基础查询
    exercises = Exercise.objects.filter(is_active=True).select_related('category', 'difficulty')
    
    # 应用筛选
    if category_slug:
        exercises = exercises.filter(category__slug=category_slug)
    
    if difficulty_id:
        exercises = exercises.filter(difficulty_id=difficulty_id)
    
    if question_type:
        exercises = exercises.filter(question_type=question_type)
    
    if search_query:
        exercises = exercises.filter(
            Q(title__icontains=search_query) |
            Q(question_text__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    # 排序
    if sort_by == 'difficulty':
        exercises = exercises.order_by('difficulty__level', 'title')
    elif sort_by == 'popularity':
        exercises = exercises.order_by('-view_count', '-created_at')
    elif sort_by == 'success_rate':
        exercises = exercises.order_by('-correct_count', '-attempt_count')
    else:  # created_at
        exercises = exercises.order_by('-created_at')
    
    # 分页
    paginator = Paginator(exercises, 12)
    page = request.GET.get('page', 1)
    exercises_page = paginator.get_page(page)
    
    # 获取筛选选项
    categories = ExerciseCategory.objects.filter(is_active=True)
    difficulties = ExerciseDifficulty.objects.all()
    question_types = Exercise.QUESTION_TYPES
    
    context = {
        'exercises': exercises_page,
        'categories': categories,
        'difficulties': difficulties,
        'question_types': question_types,
        'current_filters': {
            'category': category_slug,
            'difficulty': difficulty_id,
            'type': question_type,
            'q': search_query,
            'sort': sort_by,
        }
    }
    
    return render(request, 'knowledge_app/exercises/list.html', context)


def exercise_detail(request, slug):
    """练习题详情"""
    exercise = get_object_or_404(Exercise, slug=slug, is_active=True)
    
    # 增加浏览次数
    exercise.view_count += 1
    exercise.save(update_fields=['view_count'])
    
    # 获取用户的历史记录（如果已登录）
    user_attempts = []
    if request.user.is_authenticated:
        user_attempts = UserExerciseAttempt.objects.filter(
            user=request.user, exercise=exercise
        ).order_by('-submit_time')[:5]
    
    # 获取相关题目
    related_exercises = Exercise.objects.filter(
        category=exercise.category,
        is_active=True
    ).exclude(id=exercise.id)[:4]
    
    context = {
        'exercise': exercise,
        'user_attempts': user_attempts,
        'related_exercises': related_exercises,
    }
    
    return render(request, 'knowledge_app/exercises/detail.html', context)


@login_required
@require_http_methods(["POST"])
def submit_exercise(request, slug):
    """提交练习题答案"""
    exercise = get_object_or_404(Exercise, slug=slug, is_active=True)
    
    try:
        data = json.loads(request.body)
        user_answer = data.get('answer', '')
        start_time_str = data.get('start_time')
        hints_used = data.get('hints_used', [])
        
        # 解析开始时间
        start_time = timezone.datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
        submit_time = timezone.now()
        time_spent = int((submit_time - start_time).total_seconds())
        
        # 判断答案是否正确
        is_correct = False
        score = 0
        
        if exercise.question_type in ['single_choice', 'multiple_choice']:
            if exercise.question_type == 'single_choice':
                is_correct = user_answer.strip().upper() == exercise.correct_answer.strip().upper()
            else:  # multiple_choice
                user_answers = set(user_answer.strip().upper().split(','))
                correct_answers = set(exercise.correct_answer.strip().upper().split(','))
                is_correct = user_answers == correct_answers
        elif exercise.question_type == 'true_false':
            is_correct = user_answer.strip().lower() == exercise.correct_answer.strip().lower()
        elif exercise.question_type == 'fill_blank':
            # 简单的字符串匹配，可以扩展为更复杂的匹配逻辑
            is_correct = user_answer.strip().lower() == exercise.correct_answer.strip().lower()
        else:  # short_answer, coding
            # 这些类型需要人工评判，暂时标记为正确
            is_correct = True
        
        # 计算分数
        if is_correct:
            score = 100
            # 根据用时和提示使用情况调整分数
            if hints_used:
                score -= len(hints_used) * 10  # 每个提示扣10分
            score = max(score, 60)  # 最低60分
        
        # 保存记录
        attempt = UserExerciseAttempt.objects.create(
            user=request.user,
            exercise=exercise,
            user_answer=user_answer,
            is_correct=is_correct,
            score=score,
            start_time=start_time,
            submit_time=submit_time,
            time_spent=time_spent,
            hints_used=hints_used,
            ip_address=get_client_ip(request)
        )
        
        # 更新练习题统计
        exercise.attempt_count += 1
        if is_correct:
            exercise.correct_count += 1
        exercise.save(update_fields=['attempt_count', 'correct_count'])
        
        return JsonResponse({
            'success': True,
            'is_correct': is_correct,
            'score': score,
            'correct_answer': exercise.correct_answer,
            'explanation': exercise.explanation,
            'time_spent': time_spent,
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def exercise_set_list(request):
    """练习题集列表"""
    category_slug = request.GET.get('category')
    search_query = request.GET.get('q')
    
    # 基础查询
    exercise_sets = ExerciseSet.objects.filter(
        is_active=True, is_public=True
    ).select_related('category').annotate(
        total_exercises=Count('exercises')
    )
    
    # 应用筛选
    if category_slug:
        exercise_sets = exercise_sets.filter(category__slug=category_slug)
    
    if search_query:
        exercise_sets = exercise_sets.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # 分页
    paginator = Paginator(exercise_sets, 9)
    page = request.GET.get('page', 1)
    sets_page = paginator.get_page(page)
    
    # 获取分类
    categories = ExerciseCategory.objects.filter(is_active=True)
    
    context = {
        'exercise_sets': sets_page,
        'categories': categories,
        'current_filters': {
            'category': category_slug,
            'q': search_query,
        }
    }
    
    return render(request, 'knowledge_app/exercises/set_list.html', context)


def exercise_set_detail(request, slug):
    """练习题集详情"""
    exercise_set = get_object_or_404(ExerciseSet, slug=slug, is_active=True, is_public=True)
    
    # 获取题集中的题目
    set_items = exercise_set.exercisesetitem_set.select_related('exercise').order_by('order')
    
    # 用户的历史记录（如果已登录）
    user_attempts = []
    if request.user.is_authenticated:
        user_attempts = UserExerciseSetAttempt.objects.filter(
            user=request.user, exercise_set=exercise_set
        ).order_by('-start_time')[:5]
    
    context = {
        'exercise_set': exercise_set,
        'set_items': set_items,
        'user_attempts': user_attempts,
    }
    
    return render(request, 'knowledge_app/exercises/set_detail.html', context)


@login_required
def start_exercise_set(request, slug):
    """开始练习题集"""
    exercise_set = get_object_or_404(ExerciseSet, slug=slug, is_active=True, is_public=True)
    
    # 创建练习记录
    attempt = UserExerciseSetAttempt.objects.create(
        user=request.user,
        exercise_set=exercise_set,
        start_time=timezone.now(),
        total_count=exercise_set.exercises.count(),
        max_score=sum(item.points for item in exercise_set.exercisesetitem_set.all())
    )
    
    return redirect('knowledge_app:exercise_set_practice', slug=slug, attempt_id=attempt.id)


@require_http_methods(["GET"])
def random_exercise(request):
    """随机练习API"""
    try:
        # 获取所有活跃的练习题
        exercises = Exercise.objects.filter(is_active=True)

        if not exercises.exists():
            return JsonResponse({
                'success': False,
                'message': '暂无可用的练习题目'
            })

        # 如果用户已登录，优先推荐用户较少练习的题目
        if request.user.is_authenticated:
            # 获取用户已经做过的题目
            attempted_exercises = UserExerciseAttempt.objects.filter(
                user=request.user
            ).values_list('exercise_id', flat=True)

            # 优先选择用户没有做过的题目
            unattempted_exercises = exercises.exclude(id__in=attempted_exercises)

            if unattempted_exercises.exists():
                # 从未做过的题目中随机选择
                exercise = random.choice(unattempted_exercises)
            else:
                # 如果都做过了，从正确率较低的题目中选择
                user_attempts = UserExerciseAttempt.objects.filter(
                    user=request.user
                ).values('exercise_id').annotate(
                    correct_count=Count('id', filter=Q(is_correct=True)),
                    total_count=Count('id'),
                    success_rate=Avg('is_correct')
                ).filter(success_rate__lt=0.8)  # 正确率低于80%的题目

                if user_attempts:
                    low_success_exercise_ids = [attempt['exercise_id'] for attempt in user_attempts]
                    candidate_exercises = exercises.filter(id__in=low_success_exercise_ids)
                    exercise = random.choice(candidate_exercises)
                else:
                    # 完全随机选择
                    exercise = random.choice(exercises)
        else:
            # 未登录用户完全随机选择
            exercise = random.choice(exercises)

        return JsonResponse({
            'success': True,
            'exercise_slug': exercise.slug,
            'exercise_title': exercise.title,
            'category': exercise.category.name if exercise.category else None,
            'difficulty': exercise.difficulty.name if exercise.difficulty else None
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': '获取随机题目失败，请稍后重试'
        })


def get_client_ip(request):
    """获取客户端IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
