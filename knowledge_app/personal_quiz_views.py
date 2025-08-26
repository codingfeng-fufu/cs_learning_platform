from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
import json
import random

from .personal_quiz_models import (
    QuizLibrary, QuizQuestion, QuizTag, QuizSession, 
    QuizAnswer, WrongAnswer, StudyStats
)


@login_required
def quiz_dashboard(request):
    """个人题库仪表板"""
    user = request.user
    
    # 获取或创建学习统计
    stats, created = StudyStats.objects.get_or_create(user=user)
    if not created:
        stats.update_stats()
    
    # 获取用户的题库
    libraries = QuizLibrary.objects.filter(owner=user, is_active=True)
    
    # 获取最近的练习会话
    recent_sessions = QuizSession.objects.filter(user=user).order_by('-started_at')[:5]
    
    # 获取错题数量
    wrong_answers_count = WrongAnswer.objects.filter(user=user, is_mastered=False).count()
    
    # 获取今日学习情况
    today = timezone.now().date()
    today_sessions = QuizSession.objects.filter(
        user=user, 
        started_at__date=today,
        status='completed'
    )
    today_study_time = sum(session.duration for session in today_sessions)
    
    context = {
        'stats': stats,
        'libraries': libraries,
        'recent_sessions': recent_sessions,
        'wrong_answers_count': wrong_answers_count,
        'today_study_time': today_study_time,
        'today_sessions_count': today_sessions.count(),
    }
    
    return render(request, 'knowledge_app/quiz/dashboard.html', context)


@login_required
def library_list(request):
    """题库列表"""
    libraries = QuizLibrary.objects.filter(owner=request.user, is_active=True)
    
    # 搜索功能
    search = request.GET.get('search', '')
    if search:
        libraries = libraries.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )
    
    # 分页
    paginator = Paginator(libraries, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
    }
    
    return render(request, 'knowledge_app/quiz/library_list.html', context)


@login_required
def create_library(request):
    """创建题库"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not name:
            messages.error(request, '题库名称不能为空')
            return render(request, 'knowledge_app/quiz/create_library.html')
        
        # 检查名称是否重复
        if QuizLibrary.objects.filter(owner=request.user, name=name).exists():
            messages.error(request, '题库名称已存在，请使用其他名称')
            return render(request, 'knowledge_app/quiz/create_library.html')
        
        # 创建题库
        library = QuizLibrary.objects.create(
            owner=request.user,
            name=name,
            description=description
        )
        
        messages.success(request, f'题库 "{name}" 创建成功！')
        return redirect('knowledge_app:quiz_library_detail', library.id)
    
    return render(request, 'knowledge_app/quiz/create_library.html')


@login_required
def library_detail(request, library_id):
    """题库详情"""
    # 首先尝试获取用户自己的题库
    library = QuizLibrary.objects.filter(id=library_id, owner=request.user).first()

    # 如果不是用户自己的题库，检查是否有分享权限
    if not library:
        from .personal_quiz_models import LibraryShare

        # 检查是否有分享给当前用户的记录
        share = LibraryShare.objects.filter(
            library_id=library_id,
            shared_to=request.user,
            is_active=True
        ).first()

        if share and share.can_access(request.user):
            library = share.library
            # 记录访问
            share.record_access(request.user)
        else:
            # 检查是否是公开分享
            public_share = LibraryShare.objects.filter(
                library_id=library_id,
                share_type='public',
                is_active=True
            ).first()

            if public_share and public_share.can_access(request.user):
                library = public_share.library
                # 记录访问
                public_share.record_access(request.user)
            else:
                # 没有访问权限
                from django.http import Http404
                raise Http404("题库不存在或您没有访问权限")
    
    # 获取题目列表
    questions = library.questions.filter(is_active=True)
    
    # 筛选功能
    question_type = request.GET.get('type', '')
    difficulty = request.GET.get('difficulty', '')
    tag_id = request.GET.get('tag', '')
    
    if question_type:
        questions = questions.filter(question_type=question_type)
    if difficulty:
        questions = questions.filter(difficulty=int(difficulty))
    if tag_id:
        questions = questions.filter(tags__id=tag_id)
    
    # 分页
    paginator = Paginator(questions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 获取所有标签
    tags = QuizTag.objects.all()
    
    # 统计信息
    stats = {
        'total_questions': library.total_questions,
        'by_type': questions.values('question_type').annotate(count=Count('id')),
        'by_difficulty': questions.values('difficulty').annotate(count=Count('id')),
        'avg_accuracy': questions.aggregate(avg=Avg('correct_attempts'))['avg'] or 0,
    }
    
    context = {
        'library': library,
        'page_obj': page_obj,
        'tags': tags,
        'stats': stats,
        'current_filters': {
            'type': question_type,
            'difficulty': difficulty,
            'tag': tag_id,
        }
    }
    
    return render(request, 'knowledge_app/quiz/library_detail.html', context)


@login_required
def create_question(request, library_id):
    """创建题目"""
    library = get_object_or_404(QuizLibrary, id=library_id, owner=request.user)
    
    if request.method == 'POST':
        question_type = request.POST.get('question_type')
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        correct_answer = request.POST.get('correct_answer', '').strip()
        explanation = request.POST.get('explanation', '').strip()
        difficulty = int(request.POST.get('difficulty', 2))
        
        if not all([title, content, correct_answer]):
            messages.error(request, '请填写完整的题目信息')
            return render(request, 'knowledge_app/quiz/create_question.html', {'library': library})
        
        # 处理选项（选择题）
        options = {}
        option_images = {}
        if question_type in ['single_choice', 'multiple_choice']:
            for i in range(1, 7):  # 最多6个选项
                option_key = f'option_{i}'
                option_value = request.POST.get(option_key, '').strip()
                if option_value:
                    letter = chr(64 + i)  # A, B, C, D, E, F
                    options[letter] = option_value

                    # 处理选项图片
                    option_image_key = f'option_image_{i}'
                    if option_image_key in request.FILES:
                        option_images[letter] = request.FILES[option_image_key]
        
        # 创建题目
        question = QuizQuestion.objects.create(
            library=library,
            question_type=question_type,
            title=title,
            content=content,
            options=options,
            correct_answer=correct_answer,
            explanation=explanation,
            difficulty=difficulty
        )

        # 处理题目图片
        if 'question_image' in request.FILES:
            question.question_image = request.FILES['question_image']

        # 处理选项图片
        if option_images:
            # 保存选项图片文件并记录路径
            saved_option_images = {}
            for letter, image_file in option_images.items():
                # 这里需要手动保存图片文件
                import os
                from django.conf import settings
                from django.core.files.storage import default_storage

                # 生成文件名
                file_name = f"quiz_options/{question.id}_{letter}_{image_file.name}"
                file_path = default_storage.save(file_name, image_file)
                saved_option_images[letter] = file_path

            question.option_images = saved_option_images

        question.save()
        
        # 处理标签
        tag_names = request.POST.get('tags', '').split(',')
        for tag_name in tag_names:
            tag_name = tag_name.strip()
            if tag_name:
                tag, created = QuizTag.objects.get_or_create(name=tag_name)
                question.tags.add(tag)
        
        messages.success(request, '题目创建成功！')
        return redirect('knowledge_app:quiz_library_detail', library.id)
    
    # 获取所有标签
    tags = QuizTag.objects.all()
    
    context = {
        'library': library,
        'tags': tags,
    }
    
    return render(request, 'knowledge_app/quiz/create_question.html', context)


@login_required
def start_quiz(request, library_id):
    """开始练习"""
    # 首先尝试获取用户自己的题库
    library = QuizLibrary.objects.filter(id=library_id, owner=request.user).first()

    # 如果不是用户自己的题库，检查是否有分享权限
    if not library:
        from .personal_quiz_models import LibraryShare

        # 检查是否有分享给当前用户的记录
        share = LibraryShare.objects.filter(
            library_id=library_id,
            shared_to=request.user,
            is_active=True
        ).first()

        if share and share.can_access(request.user):
            library = share.library
            # 记录访问
            share.record_access(request.user)
        else:
            # 检查是否是公开分享
            public_share = LibraryShare.objects.filter(
                library_id=library_id,
                share_type='public',
                is_active=True
            ).first()

            if public_share and public_share.can_access(request.user):
                library = public_share.library
                # 记录访问
                public_share.record_access(request.user)
            else:
                # 没有访问权限
                from django.http import Http404
                raise Http404("题库不存在或您没有访问权限")
    
    if request.method == 'POST':
        session_name = request.POST.get('session_name', f'{library.name} - 练习')
        question_count = int(request.POST.get('question_count', 10))
        question_type = request.POST.get('question_type', '')
        difficulty = request.POST.get('difficulty', '')
        
        # 获取题目
        questions = library.questions.filter(is_active=True)
        
        if question_type:
            questions = questions.filter(question_type=question_type)
        if difficulty:
            questions = questions.filter(difficulty=int(difficulty))
        
        if not questions.exists():
            messages.error(request, '没有符合条件的题目')
            return render(request, 'knowledge_app/quiz/start_quiz.html', {'library': library})
        
        # 随机选择题目
        selected_questions = random.sample(list(questions), min(question_count, questions.count()))
        
        # 创建练习会话
        session = QuizSession.objects.create(
            user=request.user,
            library=library,
            session_name=session_name,
            total_questions=len(selected_questions)
        )
        
        # 将选择的题目ID存储在session中
        request.session[f'quiz_questions_{session.id}'] = [q.id for q in selected_questions]
        request.session[f'current_question_{session.id}'] = 0
        
        return redirect('knowledge_app:quiz_session', session.id)
    
    context = {
        'library': library,
    }
    
    return render(request, 'knowledge_app/quiz/start_quiz.html', context)


@login_required
def quiz_session(request, session_id):
    """练习会话"""
    session = get_object_or_404(QuizSession, id=session_id, user=request.user)
    
    # 获取题目列表
    question_ids = request.session.get(f'quiz_questions_{session.id}', [])
    current_index = request.session.get(f'current_question_{session.id}', 0)
    
    if current_index >= len(question_ids):
        # 练习完成
        session.status = 'completed'
        session.completed_at = timezone.now()
        session.save()
        return redirect('knowledge_app:quiz_result', session.id)
    
    # 获取当前题目
    current_question = get_object_or_404(QuizQuestion, id=question_ids[current_index])
    
    # 检查是否已经回答过这道题
    existing_answer = QuizAnswer.objects.filter(session=session, question=current_question).first()
    
    context = {
        'session': session,
        'question': current_question,
        'current_index': current_index + 1,
        'total_questions': len(question_ids),
        'progress': round(((current_index + 1) / len(question_ids)) * 100, 1),
        'existing_answer': existing_answer,
    }
    
    return render(request, 'knowledge_app/quiz/quiz_session.html', context)


@login_required
@require_http_methods(["POST"])
def submit_answer(request, session_id):
    """提交答案"""
    session = get_object_or_404(QuizSession, id=session_id, user=request.user)
    
    question_id = request.POST.get('question_id')
    user_answer = request.POST.get('answer', '').strip()
    time_spent = int(request.POST.get('time_spent', 0))
    
    question = get_object_or_404(QuizQuestion, id=question_id)
    
    # 检查答案是否正确
    is_correct = False
    if question.question_type == 'multiple_choice':
        # 多选题：用户答案和正确答案都按逗号分割后比较
        user_answers = set(user_answer.split(','))
        correct_answers = set(question.correct_answer.split(','))
        is_correct = user_answers == correct_answers
    else:
        # 其他题型：直接比较（忽略大小写和空格）
        is_correct = user_answer.lower().strip() == question.correct_answer.lower().strip()
    
    # 保存答题记录
    answer, created = QuizAnswer.objects.get_or_create(
        session=session,
        question=question,
        defaults={
            'user_answer': user_answer,
            'is_correct': is_correct,
            'time_spent': time_spent,
        }
    )
    
    # 如果答错了，记录到错题本
    if not is_correct:
        wrong_answer, created = WrongAnswer.objects.get_or_create(
            user=request.user,
            question=question,
            defaults={
                'wrong_answer': user_answer,
                'correct_answer': question.correct_answer,
            }
        )
        if not created:
            wrong_answer.wrong_count += 1
            wrong_answer.last_wrong_at = timezone.now()
            wrong_answer.save()
    
    # 移动到下一题
    current_index = request.session.get(f'current_question_{session.id}', 0)
    request.session[f'current_question_{session.id}'] = current_index + 1
    
    return JsonResponse({
        'success': True,
        'is_correct': is_correct,
        'correct_answer': question.correct_answer,
        'explanation': question.explanation,
    })


@login_required
def quiz_result(request, session_id):
    """练习结果"""
    session = get_object_or_404(QuizSession, id=session_id, user=request.user)
    
    # 获取答题记录
    answers = session.answers.all().order_by('answered_at')
    
    # 统计信息
    total_questions = answers.count()
    correct_answers = answers.filter(is_correct=True).count()
    wrong_answers = answers.filter(is_correct=False).count()
    accuracy = round((correct_answers / total_questions) * 100, 1) if total_questions > 0 else 0
    
    # 按题型统计
    type_stats = {}
    for answer in answers:
        q_type = answer.question.get_question_type_display()
        if q_type not in type_stats:
            type_stats[q_type] = {'total': 0, 'correct': 0}
        type_stats[q_type]['total'] += 1
        if answer.is_correct:
            type_stats[q_type]['correct'] += 1
    
    # 计算各题型正确率
    for stats in type_stats.values():
        stats['accuracy'] = round((stats['correct'] / stats['total']) * 100, 1)
    
    context = {
        'session': session,
        'answers': answers,
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'wrong_answers': wrong_answers,
        'accuracy': accuracy,
        'type_stats': type_stats,
    }
    
    return render(request, 'knowledge_app/quiz/quiz_result.html', context)


@login_required
def wrong_answers(request):
    """错题本"""
    wrong_answers = WrongAnswer.objects.filter(user=request.user, is_mastered=False)

    # 筛选功能
    question_type = request.GET.get('type', '')
    difficulty = request.GET.get('difficulty', '')

    if question_type:
        wrong_answers = wrong_answers.filter(question__question_type=question_type)
    if difficulty:
        wrong_answers = wrong_answers.filter(question__difficulty=int(difficulty))

    # 分页
    paginator = Paginator(wrong_answers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'current_filters': {
            'type': question_type,
            'difficulty': difficulty,
        }
    }

    return render(request, 'knowledge_app/quiz/wrong_answers.html', context)


@login_required
def wrong_answer_detail(request, wrong_answer_id):
    """错题详情"""
    wrong_answer = get_object_or_404(WrongAnswer, id=wrong_answer_id, user=request.user)

    context = {
        'wrong_answer': wrong_answer,
    }

    return render(request, 'knowledge_app/quiz/wrong_answer_detail.html', context)


@login_required
@require_http_methods(["POST"])
def mark_mastered(request, wrong_answer_id):
    """标记错题为已掌握"""
    wrong_answer = get_object_or_404(WrongAnswer, id=wrong_answer_id, user=request.user)
    wrong_answer.mark_as_mastered()

    return JsonResponse({'success': True})


@login_required
@require_http_methods(["POST"])
def analyze_wrong_answer(request, wrong_answer_id):
    """AI分析错题"""
    wrong_answer = get_object_or_404(WrongAnswer, id=wrong_answer_id, user=request.user)

    try:
        # 使用专门的题库AI分析服务
        from .services.quiz_ai_service import quiz_ai_analyzer

        # 构建错题数据
        wrong_answer_data = {
            'question': wrong_answer.question.content,
            'user_answer': wrong_answer.wrong_answer,
            'correct_answer': wrong_answer.correct_answer,
            'question_type': wrong_answer.question.question_type,
            'question_title': wrong_answer.question.title,
            'difficulty': wrong_answer.question.get_difficulty_display(),
        }

        # 调用AI分析
        result = quiz_ai_analyzer.analyze_wrong_answer(wrong_answer_data)

        if result['success']:
            # 保存分析结果
            wrong_answer.ai_analysis = result['analysis']
            wrong_answer.study_suggestion = result['suggestion']
            wrong_answer.save()

            return JsonResponse({
                'success': True,
                'analysis': result['analysis'],
                'suggestion': result['suggestion']
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.get('error', 'AI分析服务暂时不可用')
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'分析失败：{str(e)}'
        })


@login_required
def practice_wrong_answers(request):
    """错题练习"""
    wrong_answers = WrongAnswer.objects.filter(user=request.user, is_mastered=False)

    if not wrong_answers.exists():
        messages.info(request, '恭喜！你没有未掌握的错题。')
        return redirect('knowledge_app:quiz_dashboard')

    if request.method == 'POST':
        session_name = '错题练习 - ' + timezone.now().strftime('%Y-%m-%d %H:%M')

        # 创建练习会话
        session = QuizSession.objects.create(
            user=request.user,
            library=None,  # 错题练习不属于特定题库
            session_name=session_name,
            total_questions=wrong_answers.count()
        )

        # 将错题ID存储在session中
        question_ids = [wa.question.id for wa in wrong_answers]
        request.session[f'quiz_questions_{session.id}'] = question_ids
        request.session[f'current_question_{session.id}'] = 0

        return redirect('knowledge_app:quiz_session', session.id)

    context = {
        'wrong_answers_count': wrong_answers.count(),
    }

    return render(request, 'knowledge_app/quiz/practice_wrong_answers.html', context)


@login_required
def study_statistics(request):
    """学习统计"""
    user = request.user

    # 获取或创建学习统计
    stats, created = StudyStats.objects.get_or_create(user=user)
    if not created:
        stats.update_stats()

    # 获取最近30天的学习数据
    from datetime import datetime, timedelta

    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=29)

    daily_stats = []
    current_date = start_date

    while current_date <= end_date:
        day_sessions = QuizSession.objects.filter(
            user=user,
            started_at__date=current_date,
            status='completed'
        )

        day_study_time = sum(session.duration for session in day_sessions)
        day_questions = sum(session.answered_questions for session in day_sessions)

        daily_stats.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'study_time': day_study_time,
            'questions_answered': day_questions,
            'sessions_count': day_sessions.count(),
        })

        current_date += timedelta(days=1)

    # 获取题型统计
    type_stats = {}
    all_answers = QuizAnswer.objects.filter(session__user=user)

    for answer in all_answers:
        q_type = answer.question.get_question_type_display()
        if q_type not in type_stats:
            type_stats[q_type] = {'total': 0, 'correct': 0}
        type_stats[q_type]['total'] += 1
        if answer.is_correct:
            type_stats[q_type]['correct'] += 1

    # 计算各题型正确率
    for stats_data in type_stats.values():
        stats_data['accuracy'] = round((stats_data['correct'] / stats_data['total']) * 100, 1)

    context = {
        'stats': stats,
        'daily_stats': daily_stats,
        'type_stats': type_stats,
    }

    return render(request, 'knowledge_app/quiz/study_statistics.html', context)


@login_required
@require_http_methods(["GET"])
def export_library_pdf(request, library_id):
    """导出题库PDF"""
    library = get_object_or_404(QuizLibrary, id=library_id, owner=request.user)

    import logging
    logger = logging.getLogger(__name__)

    try:
        import io
        from django.http import HttpResponse
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from django.conf import settings
        from reportlab.lib.fonts import addMapping

        logger.info(f"开始导出题库PDF: {library.name} (ID: {library_id})")

        # 获取题目
        questions = library.questions.all().order_by('created_at')
        logger.info(f"找到 {questions.count()} 道题目")

        if not questions.exists():
            messages.warning(request, '该题库没有题目，无法导出PDF')
            return redirect('knowledge_app:quiz_library_detail', library_id=library_id)

        # 创建PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        # 注册中文字体
        try:
            # 尝试注册系统中文字体
            import platform
            if platform.system() == 'Windows':
                # Windows系统字体路径
                font_paths = [
                    'C:/Windows/Fonts/msyh.ttc',  # 微软雅黑
                    'C:/Windows/Fonts/simhei.ttf',  # 黑体
                    'C:/Windows/Fonts/simsun.ttc',  # 宋体
                ]
            else:
                # Linux/Mac系统字体路径
                font_paths = [
                    '/System/Library/Fonts/PingFang.ttc',  # Mac
                    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
                ]

            chinese_font_registered = False
            for font_path in font_paths:
                try:
                    import os
                    if os.path.exists(font_path):
                        pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                        chinese_font_registered = True
                        break
                except:
                    continue

            if not chinese_font_registered:
                # 如果没有找到系统字体，使用ReportLab内置字体
                chinese_font_name = 'Helvetica'
            else:
                chinese_font_name = 'ChineseFont'

        except Exception as e:
            logger.warning(f"字体注册失败，使用默认字体: {e}")
            chinese_font_name = 'Helvetica'

        # 获取样式并创建中文样式
        styles = getSampleStyleSheet()

        # 创建支持中文的样式
        chinese_title_style = ParagraphStyle(
            'ChineseTitle',
            parent=styles['Title'],
            fontName=chinese_font_name,
            fontSize=18,
            spaceAfter=12,
        )

        chinese_normal_style = ParagraphStyle(
            'ChineseNormal',
            parent=styles['Normal'],
            fontName=chinese_font_name,
            fontSize=12,
            spaceAfter=6,
        )

        chinese_heading_style = ParagraphStyle(
            'ChineseHeading',
            parent=styles['Heading2'],
            fontName=chinese_font_name,
            fontSize=14,
            spaceAfter=6,
        )

        story = []

        # 标题
        story.append(Paragraph(f"{library.name} - 题库", chinese_title_style))
        story.append(Spacer(1, 12))

        # 基本信息
        story.append(Paragraph(f"题库名称: {library.name}", chinese_normal_style))
        story.append(Paragraph(f"创建时间: {library.created_at.strftime('%Y-%m-%d %H:%M')}", chinese_normal_style))
        story.append(Paragraph(f"题目数量: {questions.count()} 道", chinese_normal_style))
        story.append(Paragraph(f"生成时间: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}", chinese_normal_style))
        story.append(Spacer(1, 20))

        # 题目列表
        for i, question in enumerate(questions, 1):
            story.append(Paragraph(f"{i}. {question.title}", chinese_heading_style))
            story.append(Paragraph(question.content, chinese_normal_style))
            story.append(Spacer(1, 6))

            # 题目图片
            if question.question_image:
                try:
                    import os
                    # 获取图片的完整路径
                    if hasattr(question.question_image, 'path'):
                        image_path = question.question_image.path
                    else:
                        image_path = os.path.join(settings.MEDIA_ROOT, str(question.question_image))

                    logger.info(f"尝试添加题目图片: {image_path}")

                    if os.path.exists(image_path):
                        img = Image(image_path)
                        # 设置图片大小，保持比例
                        img_width, img_height = img.imageWidth, img.imageHeight
                        max_width = 12*cm  # 最大宽度
                        max_height = 8*cm  # 最大高度

                        # 计算缩放比例
                        width_ratio = max_width / img_width
                        height_ratio = max_height / img_height
                        scale_ratio = min(width_ratio, height_ratio, 1.0)  # 不放大

                        img.drawWidth = img_width * scale_ratio
                        img.drawHeight = img_height * scale_ratio

                        story.append(img)
                        story.append(Spacer(1, 6))
                        logger.info(f"成功添加题目图片，尺寸: {img.drawWidth}x{img.drawHeight}")
                    else:
                        logger.warning(f"题目图片文件不存在: {image_path}")
                except Exception as e:
                    logger.error(f"无法添加题目图片: {e}")
                    import traceback
                    logger.error(f"错误详情: {traceback.format_exc()}")

            # 选项
            if question.question_type in ['single_choice', 'multiple_choice'] and question.options:
                for key, value in question.options.items():
                    story.append(Paragraph(f"{key}. {value}", chinese_normal_style))

                    # 选项图片
                    if question.option_images and key in question.option_images:
                        try:
                            import os
                            option_image_path = question.option_images[key]
                            full_image_path = os.path.join(settings.MEDIA_ROOT, option_image_path)

                            logger.info(f"尝试添加选项{key}图片: {full_image_path}")

                            if os.path.exists(full_image_path):
                                opt_img = Image(full_image_path)
                                # 选项图片较小
                                opt_img_width, opt_img_height = opt_img.imageWidth, opt_img.imageHeight
                                max_opt_width = 6*cm
                                max_opt_height = 4*cm

                                opt_width_ratio = max_opt_width / opt_img_width
                                opt_height_ratio = max_opt_height / opt_img_height
                                opt_scale_ratio = min(opt_width_ratio, opt_height_ratio, 1.0)

                                opt_img.drawWidth = opt_img_width * opt_scale_ratio
                                opt_img.drawHeight = opt_img_height * opt_scale_ratio

                                story.append(opt_img)
                                story.append(Spacer(1, 3))
                                logger.info(f"成功添加选项{key}图片，尺寸: {opt_img.drawWidth}x{opt_img.drawHeight}")
                            else:
                                logger.warning(f"选项{key}图片文件不存在: {full_image_path}")
                        except Exception as e:
                            logger.error(f"无法添加选项{key}图片: {e}")
                            import traceback
                            logger.error(f"错误详情: {traceback.format_exc()}")

            story.append(Spacer(1, 6))
            story.append(Paragraph(f"答案: {question.correct_answer}", chinese_normal_style))

            if question.explanation:
                story.append(Paragraph(f"解析: {question.explanation}", chinese_normal_style))

            story.append(Spacer(1, 15))

        # 构建PDF
        doc.build(story)
        buffer.seek(0)
        pdf_content = buffer.getvalue()
        buffer.close()

        logger.info("PDF内容生成成功")

        # 生成文件名
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        # 保留中文字符，只移除特殊字符
        import re
        safe_name = re.sub(r'[<>:"/\\|?*]', '', library.name)[:30]
        if not safe_name.strip():
            safe_name = '题库'
        filename = f"{safe_name}_题库_{timestamp}.pdf"

        # 创建响应
        response = HttpResponse(pdf_content, content_type='application/pdf')
        # 设置文件名，支持中文文件名
        from urllib.parse import quote
        # 为了更好的兼容性，使用ASCII安全的文件名作为fallback
        ascii_filename = f"Library_{library.id}_{timestamp}.pdf"
        encoded_filename = quote(filename.encode('utf-8'))
        response['Content-Disposition'] = f'inline; filename="{ascii_filename}"; filename*=UTF-8\'\'{encoded_filename}'

        logger.info(f"PDF导出成功: {filename}")
        return response

    except Exception as e:
        import traceback
        logger.error(f"PDF导出失败: {str(e)}")
        logger.error(f"错误详情: {traceback.format_exc()}")
        messages.error(request, f'PDF导出失败：{str(e)}')
        return redirect('knowledge_app:quiz_library_detail', library_id=library_id)


@login_required
@require_http_methods(["GET"])
def export_wrong_answers_pdf(request):
    """导出错题集PDF"""
    import logging
    logger = logging.getLogger(__name__)

    try:
        import io
        from django.http import HttpResponse
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from django.conf import settings

        logger.info(f"开始导出错题集PDF: {request.user.username}")

        # 获取错题
        wrong_answers = WrongAnswer.objects.filter(user=request.user).order_by('-last_wrong_at')

        if not wrong_answers.exists():
            messages.warning(request, '您还没有错题，无法导出PDF')
            return redirect('knowledge_app:quiz_wrong_answers')

        # 创建PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        # 注册中文字体
        try:
            import platform
            if platform.system() == 'Windows':
                font_paths = [
                    'C:/Windows/Fonts/msyh.ttc',  # 微软雅黑
                    'C:/Windows/Fonts/simhei.ttf',  # 黑体
                    'C:/Windows/Fonts/simsun.ttc',  # 宋体
                ]
            else:
                font_paths = [
                    '/System/Library/Fonts/PingFang.ttc',  # Mac
                    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
                ]

            chinese_font_registered = False
            for font_path in font_paths:
                try:
                    import os
                    if os.path.exists(font_path):
                        pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                        chinese_font_registered = True
                        break
                except:
                    continue

            if not chinese_font_registered:
                chinese_font_name = 'Helvetica'
            else:
                chinese_font_name = 'ChineseFont'

        except Exception as e:
            logger.warning(f"字体注册失败，使用默认字体: {e}")
            chinese_font_name = 'Helvetica'

        # 获取样式并创建中文样式
        styles = getSampleStyleSheet()

        chinese_title_style = ParagraphStyle(
            'ChineseTitle',
            parent=styles['Title'],
            fontName=chinese_font_name,
            fontSize=18,
            spaceAfter=12,
        )

        chinese_normal_style = ParagraphStyle(
            'ChineseNormal',
            parent=styles['Normal'],
            fontName=chinese_font_name,
            fontSize=12,
            spaceAfter=6,
        )

        chinese_heading_style = ParagraphStyle(
            'ChineseHeading',
            parent=styles['Heading2'],
            fontName=chinese_font_name,
            fontSize=14,
            spaceAfter=6,
        )

        story = []

        # 标题
        story.append(Paragraph(f"{request.user.username} - 错题集", chinese_title_style))
        story.append(Spacer(1, 12))

        # 基本信息
        story.append(Paragraph(f"用户名: {request.user.username}", chinese_normal_style))
        story.append(Paragraph(f"错题数量: {wrong_answers.count()} 道", chinese_normal_style))
        story.append(Paragraph(f"生成时间: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}", chinese_normal_style))
        story.append(Spacer(1, 20))

        # 错题列表
        for i, wrong_answer in enumerate(wrong_answers, 1):
            question = wrong_answer.question
            story.append(Paragraph(f"{i}. {question.title}", chinese_heading_style))
            story.append(Paragraph(question.content, chinese_normal_style))
            story.append(Spacer(1, 6))

            # 题目图片
            if question.question_image:
                try:
                    import os
                    # 获取图片的完整路径
                    if hasattr(question.question_image, 'path'):
                        image_path = question.question_image.path
                    else:
                        image_path = os.path.join(settings.MEDIA_ROOT, str(question.question_image))

                    logger.info(f"尝试添加错题图片: {image_path}")

                    if os.path.exists(image_path):
                        img = Image(image_path)
                        img_width, img_height = img.imageWidth, img.imageHeight
                        max_width = 12*cm
                        max_height = 8*cm

                        width_ratio = max_width / img_width
                        height_ratio = max_height / img_height
                        scale_ratio = min(width_ratio, height_ratio, 1.0)

                        img.drawWidth = img_width * scale_ratio
                        img.drawHeight = img_height * scale_ratio

                        story.append(img)
                        story.append(Spacer(1, 6))
                        logger.info(f"成功添加错题图片，尺寸: {img.drawWidth}x{img.drawHeight}")
                    else:
                        logger.warning(f"错题图片文件不存在: {image_path}")
                except Exception as e:
                    logger.error(f"无法添加错题图片: {e}")
                    import traceback
                    logger.error(f"错误详情: {traceback.format_exc()}")

            # 选项
            if question.question_type in ['single_choice', 'multiple_choice'] and question.options:
                for key, value in question.options.items():
                    story.append(Paragraph(f"{key}. {value}", chinese_normal_style))

                    # 选项图片
                    if question.option_images and key in question.option_images:
                        try:
                            import os
                            option_image_path = question.option_images[key]
                            full_image_path = os.path.join(settings.MEDIA_ROOT, option_image_path)

                            logger.info(f"尝试添加选项{key}图片: {full_image_path}")

                            if os.path.exists(full_image_path):
                                opt_img = Image(full_image_path)
                                opt_img_width, opt_img_height = opt_img.imageWidth, opt_img.imageHeight
                                max_opt_width = 6*cm
                                max_opt_height = 4*cm

                                opt_width_ratio = max_opt_width / opt_img_width
                                opt_height_ratio = max_opt_height / opt_img_height
                                opt_scale_ratio = min(opt_width_ratio, opt_height_ratio, 1.0)

                                opt_img.drawWidth = opt_img_width * opt_scale_ratio
                                opt_img.drawHeight = opt_img_height * opt_scale_ratio

                                story.append(opt_img)
                                story.append(Spacer(1, 3))
                                logger.info(f"成功添加选项{key}图片，尺寸: {opt_img.drawWidth}x{opt_img.drawHeight}")
                            else:
                                logger.warning(f"选项{key}图片文件不存在: {full_image_path}")
                        except Exception as e:
                            logger.error(f"无法添加选项{key}图片: {e}")
                            import traceback
                            logger.error(f"错误详情: {traceback.format_exc()}")

            story.append(Spacer(1, 6))
            story.append(Paragraph(f"正确答案: {question.correct_answer}", chinese_normal_style))
            story.append(Paragraph(f"您的答案: {wrong_answer.wrong_answer}", chinese_normal_style))
            story.append(Paragraph(f"错误次数: {wrong_answer.wrong_count}", chinese_normal_style))

            if question.explanation:
                story.append(Paragraph(f"解析: {question.explanation}", chinese_normal_style))

            story.append(Spacer(1, 15))

        # 构建PDF
        doc.build(story)
        buffer.seek(0)
        pdf_content = buffer.getvalue()
        buffer.close()

        logger.info("错题集PDF内容生成成功")

        # 生成文件名
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        safe_username = ''.join(c for c in request.user.username if c.isalnum() or c in '-_')[:20]
        if not safe_username.strip():
            safe_username = 'User'
        filename = f"{safe_username}_WrongAnswers_{timestamp}.pdf"

        # 创建响应
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        logger.info(f"错题集PDF导出成功: {filename}")
        return response

    except Exception as e:
        import traceback
        logger.error(f"错题集PDF导出失败: {str(e)}")
        logger.error(f"错误详情: {traceback.format_exc()}")
        messages.error(request, f'PDF导出失败：{str(e)}')
        return redirect('knowledge_app:quiz_wrong_answers')


@require_http_methods(["GET"])
def test_pdf_generation(request):
    """测试PDF生成功能"""
    try:
        import io
        from django.http import HttpResponse
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet

        # 创建PDF缓冲区
        buffer = io.BytesIO()

        # 创建PDF文档
        doc = SimpleDocTemplate(buffer, pagesize=A4)

        # 获取样式
        styles = getSampleStyleSheet()

        # 创建内容
        story = []
        story.append(Paragraph("PDF Test - 测试PDF生成功能", styles['Title']))
        story.append(Paragraph("This is a test PDF to verify PDF generation is working.", styles['Normal']))
        story.append(Paragraph("这是一个测试PDF，用于验证PDF生成功能是否正常工作。", styles['Normal']))
        story.append(Paragraph(f"Generated at: {timezone.now()}", styles['Normal']))

        # 构建PDF
        doc.build(story)

        # 获取PDF内容
        buffer.seek(0)
        pdf_content = buffer.getvalue()
        buffer.close()

        # 创建响应
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="test.pdf"'

        return response

    except Exception as e:
        import traceback
        error_msg = f"PDF测试失败: {str(e)}\n{traceback.format_exc()}"
        return HttpResponse(error_msg, content_type='text/plain')


@login_required
@require_http_methods(["POST"])
def analyze_session_performance(request, session_id):
    """AI分析练习会话表现"""
    session = get_object_or_404(QuizSession, id=session_id, user=request.user)

    try:
        # 使用专门的题库AI分析服务
        from .services.quiz_ai_service import quiz_ai_analyzer

        # 获取会话数据
        answers = session.answers.all()
        wrong_answers = answers.filter(is_correct=False)

        # 构建会话分析数据
        session_data = {
            'total_questions': session.total_questions,
            'correct_answers': session.correct_answers,
            'accuracy': session.accuracy_rate,
            'wrong_answers': [
                {
                    'question_title': answer.question.title,
                    'user_answer': answer.user_answer,
                    'correct_answer': answer.question.correct_answer,
                    'question_type': answer.question.get_question_type_display(),
                }
                for answer in wrong_answers
            ],
            'type_stats': {}
        }

        # 计算题型统计
        type_stats = {}
        for answer in answers:
            q_type = answer.question.get_question_type_display()
            if q_type not in type_stats:
                type_stats[q_type] = {'total': 0, 'correct': 0}
            type_stats[q_type]['total'] += 1
            if answer.is_correct:
                type_stats[q_type]['correct'] += 1

        # 计算各题型正确率
        for stats in type_stats.values():
            stats['accuracy'] = round((stats['correct'] / stats['total']) * 100, 1)

        session_data['type_stats'] = type_stats

        # 调用AI分析
        result = quiz_ai_analyzer.analyze_session_performance(session_data)

        if result['success']:
            return JsonResponse({
                'success': True,
                'overall_analysis': result['overall_analysis'],
                'strengths': result['strengths'],
                'weaknesses': result['weaknesses'],
                'suggestions': result['suggestions'],
                'next_steps': result['next_steps']
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.get('error', 'AI分析服务暂时不可用')
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'分析失败：{str(e)}'
        })
