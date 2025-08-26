"""
用户学习进度服务
"""
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import User, StudySession, KnowledgePoint


class ProgressService:
    """学习进度服务类"""
    
    @staticmethod
    def get_user_progress_summary(user):
        """获取用户学习进度摘要"""
        try:
            # 获取所有知识点
            total_points = KnowledgePoint.objects.filter(is_active=True).count()
            
            # 获取已完成的知识点
            completed_sessions = StudySession.objects.filter(
                user=user,
                is_completed=True
            ).values('knowledge_point').distinct()
            completed_points = completed_sessions.count()
            
            # 计算完成率
            completion_rate = (completed_points / total_points * 100) if total_points > 0 else 0
            
            # 获取总学习时间（秒转小时）
            total_study_time = StudySession.objects.filter(
                user=user,
                duration__isnull=False
            ).aggregate(total=Sum('duration'))['total'] or 0
            total_study_time_hours = total_study_time // 3600
            
            # 计算学习连续天数
            current_streak = ProgressService._calculate_current_streak(user)
            longest_streak = ProgressService._calculate_longest_streak(user)
            
            # 获取分类进度
            category_progress = ProgressService._get_category_progress(user)
            
            return {
                'completion_rate': completion_rate,
                'completed_points': completed_points,
                'total_points': total_points,
                'total_study_time_hours': total_study_time_hours,
                'current_streak': current_streak,
                'longest_streak': longest_streak,
                'category_progress': category_progress,
            }
            
        except Exception as e:
            print(f"获取进度摘要时出错: {e}")
            return {
                'completion_rate': 0,
                'completed_points': 0,
                'total_points': 0,
                'total_study_time_hours': 0,
                'current_streak': 0,
                'longest_streak': 0,
                'category_progress': [],
            }
    
    @staticmethod
    def _calculate_current_streak(user):
        """计算当前连续学习天数"""
        try:
            today = timezone.now().date()
            current_date = today
            streak = 0
            
            # 从今天开始往前检查
            while True:
                has_study = StudySession.objects.filter(
                    user=user,
                    start_time__date=current_date
                ).exists()
                
                if has_study:
                    streak += 1
                    current_date -= timedelta(days=1)
                else:
                    # 如果是今天没有学习，不算中断
                    if current_date == today:
                        current_date -= timedelta(days=1)
                        continue
                    else:
                        break
                        
                # 防止无限循环，最多检查100天
                if streak >= 100:
                    break
            
            return streak
            
        except Exception as e:
            print(f"计算连续天数时出错: {e}")
            return 0
    
    @staticmethod
    def _calculate_longest_streak(user):
        """计算最长连续学习天数"""
        try:
            # 获取所有有学习记录的日期
            study_dates = StudySession.objects.filter(
                user=user
            ).values_list('start_time__date', flat=True).distinct().order_by('start_time__date')
            
            if not study_dates:
                return 0
            
            max_streak = 1
            current_streak = 1
            
            for i in range(1, len(study_dates)):
                if study_dates[i] - study_dates[i-1] == timedelta(days=1):
                    current_streak += 1
                    max_streak = max(max_streak, current_streak)
                else:
                    current_streak = 1
            
            return max_streak
            
        except Exception as e:
            print(f"计算最长连续天数时出错: {e}")
            return 0
    
    @staticmethod
    def _get_category_progress(user):
        """获取分类进度"""
        try:
            # 获取所有分类的进度
            categories = KnowledgePoint.objects.values('category').annotate(
                total=Count('id')
            ).filter(is_active=True)
            
            category_progress = []
            for category in categories:
                completed = StudySession.objects.filter(
                    user=user,
                    is_completed=True,
                    knowledge_point__category=category['category']
                ).values('knowledge_point').distinct().count()
                
                category_progress.append({
                    'knowledge_point__category': category['category'],
                    'total': category['total'],
                    'completed': completed
                })
            
            return category_progress
            
        except Exception as e:
            print(f"获取分类进度时出错: {e}")
            return []
    
    @staticmethod
    def get_recent_activity(user, days=30):
        """获取最近的学习活动"""
        try:
            cutoff_date = timezone.now() - timedelta(days=days)
            
            activities = StudySession.objects.filter(
                user=user,
                start_time__gte=cutoff_date
            ).select_related('knowledge_point').order_by('-start_time')[:20]
            
            return activities
            
        except Exception as e:
            print(f"获取最近活动时出错: {e}")
            return []
    
    @staticmethod
    def get_learning_calendar(user, year, month):
        """获取学习日历数据"""
        try:
            from calendar import monthrange
            
            # 获取月份的第一天和最后一天
            first_day = datetime(year, month, 1).date()
            last_day = datetime(year, month, monthrange(year, month)[1]).date()
            
            # 获取该月的所有学习记录
            sessions = StudySession.objects.filter(
                user=user,
                start_time__date__gte=first_day,
                start_time__date__lte=last_day
            ).values('start_time__date').annotate(
                total_time=Sum('duration'),
                session_count=Count('id')
            )
            
            # 转换为字典格式
            calendar_data = []
            for session in sessions:
                calendar_data.append({
                    'day': session['start_time__date'].isoformat(),
                    'total_time': session['total_time'] or 0,
                    'session_count': session['session_count']
                })
            
            return calendar_data
            
        except Exception as e:
            print(f"获取学习日历时出错: {e}")
            return []


class LearningAnalytics:
    """学习分析服务"""
    
    @staticmethod
    def get_weekly_study_pattern(user):
        """获取周学习模式"""
        try:
            # 获取最近4周的数据
            end_date = timezone.now().date()
            start_date = end_date - timedelta(weeks=4)
            
            sessions = StudySession.objects.filter(
                user=user,
                start_time__date__gte=start_date,
                start_time__date__lte=end_date
            )
            
            # 按星期几分组统计
            weekly_pattern = {}
            for i in range(7):  # 0=Monday, 6=Sunday
                day_sessions = sessions.filter(start_time__week_day=i+2)  # Django week_day: 1=Sunday
                total_time = day_sessions.aggregate(total=Sum('duration'))['total'] or 0
                weekly_pattern[i] = total_time // 60  # 转换为分钟
            
            return weekly_pattern
            
        except Exception as e:
            print(f"获取周学习模式时出错: {e}")
            return {i: 0 for i in range(7)}
    
    @staticmethod
    def get_learning_efficiency(user):
        """计算学习效率"""
        try:
            # 获取最近30天的数据
            cutoff_date = timezone.now() - timedelta(days=30)
            
            sessions = StudySession.objects.filter(
                user=user,
                start_time__gte=cutoff_date,
                duration__isnull=False
            )
            
            if not sessions.exists():
                return 0
            
            # 计算平均每次学习完成的知识点数
            completed_sessions = sessions.filter(is_completed=True)
            total_sessions = sessions.count()
            
            efficiency = (completed_sessions.count() / total_sessions * 100) if total_sessions > 0 else 0
            
            return round(efficiency, 1)
            
        except Exception as e:
            print(f"计算学习效率时出错: {e}")
            return 0
