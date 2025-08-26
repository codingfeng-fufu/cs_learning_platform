from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from .models import (
    User, EmailVerificationToken, PasswordResetToken, UserProfile,
    UserAchievement, StudySession
)
from .forms import (
    UserRegistrationForm, UserLoginForm, CustomPasswordResetForm,
    UserProfileForm, UserPreferencesForm, StudyGoalForm
)
from .email_service import EmailService
from .progress_service import ProgressService
import json

def register(request):
    """用户注册"""
    if request.user.is_authenticated:
        return redirect('knowledge_app:index')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # 发送验证邮件
            if EmailService.send_verification_email(user, request):
                messages.success(
                    request,
                    f'注册成功！验证邮件已发送到 {user.email}，请查收并点击验证链接。'
                )
            else:
                messages.warning(
                    request,
                    '注册成功，但验证邮件发送失败。您可以稍后重新发送验证邮件。'
                )

            return redirect('users:login')
    else:
        form = UserRegistrationForm()

    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    """用户登录"""
    if request.user.is_authenticated:
        return redirect('knowledge_app:index')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # 检查邮箱是否已验证
            if not user.is_email_verified:
                messages.warning(
                    request,
                    '您的邮箱尚未验证，部分功能可能受限。请查收验证邮件。'
                )

            messages.success(request, f'欢迎回来，{user.get_display_name()}！')

            # 重定向到原来要访问的页面
            next_url = request.GET.get('next', 'knowledge_app:index')
            return redirect(next_url)
    else:
        form = UserLoginForm()

    return render(request, 'users/login.html', {'form': form})


def user_logout(request):
    """用户登出"""
    if request.user.is_authenticated:
        messages.success(request, '您已成功登出。')
        logout(request)
    return redirect('knowledge_app:index')


def verify_email(request, token):
    """邮箱验证"""
    try:
        verification_token = get_object_or_404(EmailVerificationToken, token=token)

        if verification_token.is_used:
            messages.error(request, '该验证链接已被使用。')
        elif verification_token.is_expired():
            messages.error(request, '验证链接已过期，请重新发送验证邮件。')
        else:
            # 验证成功
            user = verification_token.user
            user.is_email_verified = True
            user.save()

            verification_token.is_used = True
            verification_token.save()

            # 发送欢迎邮件
            EmailService.send_welcome_email(user)

            messages.success(request, '邮箱验证成功！欢迎加入我们的学习平台。')

            # 如果用户未登录，自动登录
            if not request.user.is_authenticated:
                login(request, user)
                return redirect('knowledge_app:index')

    except Exception as e:
        messages.error(request, '验证链接无效或已过期。')

    return redirect('knowledge_app:index')


@login_required
def resend_verification_email(request):
    """重新发送验证邮件"""
    user = request.user

    if user.is_email_verified:
        messages.info(request, '您的邮箱已经验证过了。')
        return redirect('users:profile')

    # 检查是否为开发环境
    from django.conf import settings
    if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
        # 开发环境直接验证邮箱
        user.is_email_verified = True
        user.save()
        messages.success(request, '开发环境：邮箱已自动验证成功！')
        return redirect('users:profile')

    # 生产环境发送邮件
    # 删除旧的未使用的验证令牌
    EmailVerificationToken.objects.filter(user=user, is_used=False).delete()

    if EmailService.send_verification_email(user, request):
        messages.success(request, f'验证邮件已重新发送到 {user.email}')
    else:
        messages.error(request, '发送验证邮件失败，请稍后重试。')

    return redirect('users:profile')


def password_reset_request(request):
    """密码重置请求"""
    if request.user.is_authenticated:
        return redirect('knowledge_app:index')

    if request.method == 'POST':
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)

            # 删除旧的未使用的重置令牌
            PasswordResetToken.objects.filter(user=user, is_used=False).delete()

            if EmailService.send_password_reset_email(user, request):
                messages.success(
                    request,
                    f'密码重置邮件已发送到 {email}，请查收并按照邮件指示重置密码。'
                )
            else:
                messages.error(request, '发送重置邮件失败，请稍后重试。')

            return redirect('users:login')
    else:
        form = CustomPasswordResetForm()

    return render(request, 'users/password_reset.html', {'form': form})


def password_reset_confirm(request, token):
    """密码重置确认"""
    try:
        reset_token = get_object_or_404(PasswordResetToken, token=token)

        if reset_token.is_used:
            messages.error(request, '该重置链接已被使用。')
            return redirect('users:password_reset_request')

        if reset_token.is_expired():
            messages.error(request, '重置链接已过期，请重新申请密码重置。')
            return redirect('users:password_reset_request')

        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')

            if not password1 or not password2:
                messages.error(request, '请填写完整的密码信息。')
            elif password1 != password2:
                messages.error(request, '两次输入的密码不一致。')
            elif len(password1) < 8:
                messages.error(request, '密码长度至少为8位。')
            else:
                # 重置密码
                user = reset_token.user
                user.set_password(password1)
                user.save()

                reset_token.is_used = True
                reset_token.save()

                # 发送密码修改通知
                EmailService.send_password_changed_notification(user)

                messages.success(request, '密码重置成功，请使用新密码登录。')
                return redirect('users:login')

        return render(request, 'users/password_reset_confirm.html', {
            'token': token,
            'user': reset_token.user
        })

    except Exception as e:
        messages.error(request, '重置链接无效或已过期。')
        return redirect('users:password_reset_request')


@login_required
def profile(request):
    """用户资料页面"""
    user = request.user
    try:
        user_profile = user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=user)

    # 获取学习进度摘要
    progress_summary = ProgressService.get_user_progress_summary(user)

    # 获取用户成就
    user_achievements = UserAchievement.objects.filter(user=user).select_related('achievement')[:8]

    # 获取最近学习活动
    recent_activities = ProgressService.get_recent_activity(user, days=7)

    # 更新连续学习天数
    ProgressService.update_daily_streak(user)

    # 计算等级进度
    level_progress = (user.points % 100)  # 假设每100积分升一级
    points_to_next_level = 100 - level_progress

    # 计算本周数据
    from datetime import datetime, timedelta
    week_start = datetime.now() - timedelta(days=7)
    weekly_sessions = StudySession.objects.filter(
        user=user,
        start_time__gte=week_start
    )
    weekly_points = sum([10 for session in weekly_sessions if session.is_completed])  # 假设每完成一个知识点10积分
    weekly_hours = sum([session.duration for session in weekly_sessions]) // 3600

    # 获取总成就数
    from .models import Achievement
    total_achievements = Achievement.objects.filter(is_active=True).count()

    # 获取下一个可获得的成就
    next_achievement = None
    all_achievements = Achievement.objects.filter(is_active=True)
    user_achievement_ids = user_achievements.values_list('achievement_id', flat=True)

    for achievement in all_achievements:
        if achievement.id not in user_achievement_ids:
            # 计算进度
            progress = 0
            if achievement.condition_type == 'knowledge_points':
                progress = min(100, (progress_summary['completed_points'] / achievement.condition_value) * 100)
            elif achievement.condition_type == 'study_time':
                progress = min(100, (progress_summary['total_study_time_hours'] / achievement.condition_value) * 100)
            elif achievement.condition_type == 'streak_days':
                progress = min(100, (progress_summary['current_streak'] / achievement.condition_value) * 100)

            if progress > 0:
                next_achievement = {
                    'name': achievement.name,
                    'description': achievement.description,
                    'progress': int(progress)
                }
                break

    context = {
        'user': user,
        'user_profile': user_profile,
        'progress_summary': progress_summary,
        'user_achievements': user_achievements,
        'recent_activities': recent_activities,
        'level_progress': level_progress,
        'points_to_next_level': points_to_next_level,
        'weekly_points': weekly_points,
        'weekly_hours': weekly_hours,
        'total_achievements': total_achievements,
        'next_achievement': next_achievement,
    }
    return render(request, 'users/profile.html', context)


@login_required
def edit_profile(request):
    """编辑用户资料"""
    user = request.user

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, '资料更新成功！')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=user)

    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def preferences(request):
    """用户偏好设置"""
    user = request.user

    if request.method == 'POST':
        user_form = UserPreferencesForm(request.POST, instance=user)

        try:
            profile = user.userprofile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=user)

        profile_form = StudyGoalForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, '偏好设置更新成功！')
            return redirect('users:profile')
    else:
        user_form = UserPreferencesForm(instance=user)
        try:
            profile = user.userprofile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=user)
        profile_form = StudyGoalForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'users/preferences.html', context)


@login_required
@require_http_methods(["POST"])
def change_password(request):
    """修改密码"""
    current_password = request.POST.get('current_password')
    new_password1 = request.POST.get('new_password1')
    new_password2 = request.POST.get('new_password2')

    if not all([current_password, new_password1, new_password2]):
        messages.error(request, '请填写完整的密码信息。')
        return redirect('users:preferences')

    if not request.user.check_password(current_password):
        messages.error(request, '当前密码错误。')
        return redirect('users:preferences')

    if new_password1 != new_password2:
        messages.error(request, '两次输入的新密码不一致。')
        return redirect('users:preferences')

    if len(new_password1) < 8:
        messages.error(request, '新密码长度至少为8位。')
        return redirect('users:preferences')

    # 修改密码
    request.user.set_password(new_password1)
    request.user.save()

    # 发送通知邮件
    EmailService.send_password_changed_notification(request.user)

    messages.success(request, '密码修改成功，请重新登录。')
    logout(request)
    return redirect('users:login')


@login_required
@require_http_methods(["POST"])
def start_learning(request):
    """开始学习会话API"""
    try:
        data = json.loads(request.body)
        knowledge_point_slug = data.get('knowledge_point_slug')

        if not knowledge_point_slug:
            return JsonResponse({'error': '缺少知识点标识符'}, status=400)

        session = ProgressService.start_study_session(request.user, knowledge_point_slug)

        if session:
            return JsonResponse({
                'success': True,
                'session_id': session.id,
                'message': '学习会话已开始'
            })
        else:
            return JsonResponse({'error': '开始学习会话失败'}, status=500)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def end_learning(request):
    """结束学习会话API"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        progress_percentage = data.get('progress_percentage', 100.0)

        if not session_id:
            return JsonResponse({'error': '缺少会话ID'}, status=400)

        session = ProgressService.end_study_session(session_id, progress_percentage)

        if session:
            return JsonResponse({
                'success': True,
                'duration': session.duration,
                'message': '学习会话已结束'
            })
        else:
            return JsonResponse({'error': '结束学习会话失败'}, status=500)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def learning_stats(request):
    """获取学习统计数据API"""
    try:
        progress_summary = ProgressService.get_user_progress_summary(request.user)
        recent_activities = ProgressService.get_recent_activity(request.user, days=30)

        # 转换为JSON可序列化的格式
        activities_data = []
        for activity in recent_activities:
            activities_data.append({
                'knowledge_point': activity.knowledge_point.title,
                'start_time': activity.start_time.isoformat(),
                'duration': activity.duration,
                'is_completed': activity.is_completed,
            })

        return JsonResponse({
            'progress_summary': progress_summary,
            'recent_activities': activities_data,
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def learning_dashboard(request):
    """学习仪表板页面"""
    user = request.user

    # 获取学习进度摘要
    progress_summary = ProgressService.get_user_progress_summary(user)

    # 获取最近学习活动
    recent_activities = ProgressService.get_recent_activity(user, days=30)

    # 计算本周数据
    from datetime import datetime, timedelta
    week_start = datetime.now() - timedelta(days=7)
    weekly_sessions = StudySession.objects.filter(
        user=user,
        start_time__gte=week_start
    )

    weekly_completed = weekly_sessions.filter(is_completed=True).count()
    weekly_hours = sum([s.duration for s in weekly_sessions if s.duration]) // 3600

    context = {
        'progress_summary': progress_summary,
        'recent_activities': recent_activities,
        'weekly_completed': weekly_completed,
        'weekly_hours': weekly_hours,
    }

    return render(request, 'users/learning_dashboard.html', context)


@login_required
def learning_plan(request):
    """学习计划页面"""
    user = request.user

    # 获取用户学习进度
    progress_summary = ProgressService.get_user_progress_summary(user)

    # 获取知识点数据
    from knowledge_app.models import KnowledgePoint

    # 按分类获取知识点
    categories = {
        '数据结构': KnowledgePoint.objects.filter(category='数据结构').order_by('title'),
        '算法设计': KnowledgePoint.objects.filter(category='算法设计').order_by('title'),
        '计算机网络': KnowledgePoint.objects.filter(category='计算机网络').order_by('title'),
        '操作系统': KnowledgePoint.objects.filter(category='操作系统').order_by('title'),
        '数据库系统': KnowledgePoint.objects.filter(category='数据库系统').order_by('title'),
        '软件工程': KnowledgePoint.objects.filter(category='软件工程').order_by('title'),
    }

    # 获取用户已完成的知识点
    completed_points = set()
    if hasattr(user, 'studysession_set'):
        completed_sessions = user.studysession_set.filter(is_completed=True)
        completed_points = set(session.knowledge_point_slug for session in completed_sessions if session.knowledge_point_slug)

    # 生成学习路径建议
    learning_paths = [
        {
            'title': '数据结构基础路径',
            'description': '从基础数据结构开始，逐步掌握线性结构、树形结构和图结构',
            'icon': '🧠',
            'difficulty': 'beginner',
            'estimated_time': '4-6周',
            'topics': ['单链表', '双链表', '栈', '队列', '二叉树', '图的存储结构'],
            'color': '#667eea'
        },
        {
            'title': '算法设计进阶路径',
            'description': '掌握经典算法设计思想，提升问题解决能力',
            'icon': '⚡',
            'difficulty': 'intermediate',
            'estimated_time': '6-8周',
            'topics': ['分治算法', '动态规划', '贪心算法', '回溯算法'],
            'color': '#4ecdc4'
        },
        {
            'title': '计算机网络系统路径',
            'description': '理解网络协议栈，掌握网络通信原理',
            'icon': '🌐',
            'difficulty': 'intermediate',
            'estimated_time': '5-7周',
            'topics': ['物理层', '数据链路层', '网络层', '传输层', '应用层'],
            'color': '#45b7d1'
        },
        {
            'title': '系统编程路径',
            'description': '深入理解操作系统和数据库系统原理',
            'icon': '💻',
            'difficulty': 'advanced',
            'estimated_time': '8-10周',
            'topics': ['进程管理', '内存管理', '文件系统', '数据库设计', '事务处理'],
            'color': '#96ceb4'
        }
    ]

    # 计算每个路径的完成度
    for path in learning_paths:
        completed_count = sum(1 for topic in path['topics'] if any(topic in point.title for point in KnowledgePoint.objects.all() if point.slug in completed_points))
        path['completion_rate'] = (completed_count / len(path['topics'])) * 100 if path['topics'] else 0
        path['completed_topics'] = completed_count
        path['total_topics'] = len(path['topics'])

    context = {
        'progress_summary': progress_summary,
        'categories': categories,
        'completed_points': completed_points,
        'learning_paths': learning_paths,
    }

    return render(request, 'users/learning_plan.html', context)


@login_required
def learning_calendar_api(request):
    """学习日历数据API"""
    try:
        year = int(request.GET.get('year', timezone.now().year))
        month = int(request.GET.get('month', timezone.now().month))

        calendar_data = ProgressService.get_learning_calendar(request.user, year, month)

        return JsonResponse({
            'calendar_data': list(calendar_data),
            'year': year,
            'month': month,
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def weekly_chart_api(request):
    """每周学习时间图表数据API"""
    try:
        from datetime import datetime, timedelta

        # 获取最近7天的数据
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=6)

        daily_data = []
        for i in range(7):
            current_date = start_date + timedelta(days=i)

            # 获取当天的学习时间
            day_sessions = StudySession.objects.filter(
                user=request.user,
                start_time__date=current_date
            )

            total_minutes = sum([s.duration for s in day_sessions if s.duration]) // 60
            session_count = day_sessions.count()

            daily_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'day_name': current_date.strftime('%A'),
                'day_short': current_date.strftime('%a'),
                'total_minutes': total_minutes,
                'session_count': session_count,
            })

        return JsonResponse({
            'daily_data': daily_data,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
