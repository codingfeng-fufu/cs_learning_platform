from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q
from datetime import datetime, timedelta
from .models import (
    User, UserProfile, KnowledgePoint, StudySession, 
    UserKnowledgeProgress, Achievement, UserAchievement
)
import logging

logger = logging.getLogger(__name__)

class ProgressService:
    """学习进度服务类"""
    
    @staticmethod
    def start_study_session(user, knowledge_point_slug):
        """开始学习会话"""
        try:
            # 获取或创建知识点
            knowledge_point, created = KnowledgePoint.objects.get_or_create(
                slug=knowledge_point_slug,
                defaults={
                    'title': knowledge_point_slug.replace('-', ' ').title(),
                    'category': 'Unknown',
                    'subcategory': 'Unknown',
                }
            )
            
            # 创建学习会话
            session = StudySession.objects.create(
                user=user,
                knowledge_point=knowledge_point,
                start_time=timezone.now()
            )
            
            # 更新或创建用户知识点进度
            progress, created = UserKnowledgeProgress.objects.get_or_create(
                user=user,
                knowledge_point=knowledge_point,
                defaults={'status': 'in_progress'}
            )
            
            if progress.status == 'not_started':
                progress.status = 'in_progress'
                progress.save()
            
            logger.info(f"用户 {user.username} 开始学习 {knowledge_point.title}")
            return session
            
        except Exception as e:
            logger.error(f"开始学习会话失败: {e}")
            return None
    
    @staticmethod
    def end_study_session(session_id, progress_percentage=100.0):
        """结束学习会话"""
        try:
            session = StudySession.objects.get(id=session_id)
            session.end_time = timezone.now()
            session.progress_percentage = progress_percentage
            session.is_completed = progress_percentage >= 100.0
            session.save()
            
            # 更新用户知识点进度
            progress = UserKnowledgeProgress.objects.get(
                user=session.user,
                knowledge_point=session.knowledge_point
            )
            
            progress.progress_percentage = max(progress.progress_percentage, progress_percentage)
            progress.total_study_time += session.duration
            
            if progress_percentage >= 100.0:
                progress.status = 'completed'
                progress.completed_at = timezone.now()
            
            progress.save()
            
            # 更新用户总学习时间
            session.user.total_study_time += session.duration // 60  # 转换为分钟
            session.user.save()
            
            # 检查成就
            ProgressService.check_achievements(session.user)
            
            logger.info(f"用户 {session.user.username} 完成学习 {session.knowledge_point.title}")
            return session
            
        except Exception as e:
            logger.error(f"结束学习会话失败: {e}")
            return None
    
    @staticmethod
    def get_user_progress_summary(user):
        """获取用户学习进度摘要"""
        try:
            # 基本统计
            total_knowledge_points = UserKnowledgeProgress.objects.filter(user=user).count()
            completed_points = UserKnowledgeProgress.objects.filter(
                user=user, status='completed'
            ).count()
            in_progress_points = UserKnowledgeProgress.objects.filter(
                user=user, status='in_progress'
            ).count()
            
            # 学习时间统计
            total_study_time = StudySession.objects.filter(user=user).aggregate(
                total=Sum('duration')
            )['total'] or 0
            
            # 最近7天的学习情况
            seven_days_ago = timezone.now() - timedelta(days=7)
            recent_sessions = StudySession.objects.filter(
                user=user,
                start_time__gte=seven_days_ago
            ).count()
            
            # 分类进度
            category_progress = UserKnowledgeProgress.objects.filter(
                user=user
            ).values('knowledge_point__category').annotate(
                total=Count('id'),
                completed=Count('id', filter=Q(status='completed'))
            )
            
            # 连续学习天数
            profile = user.userprofile
            
            return {
                'total_knowledge_points': total_knowledge_points,
                'completed_points': completed_points,
                'in_progress_points': in_progress_points,
                'completion_rate': (completed_points / total_knowledge_points * 100) if total_knowledge_points > 0 else 0,
                'total_study_time_seconds': total_study_time,
                'total_study_time_hours': total_study_time // 3600,
                'recent_sessions': recent_sessions,
                'category_progress': list(category_progress),
                'current_streak': profile.current_streak,
                'longest_streak': profile.longest_streak,
                'level': user.level,
                'points': user.points,
            }
            
        except Exception as e:
            logger.error(f"获取用户进度摘要失败: {e}")
            return {}
    
    @staticmethod
    def get_recent_activity(user, days=7):
        """获取最近的学习活动"""
        try:
            start_date = timezone.now() - timedelta(days=days)
            sessions = StudySession.objects.filter(
                user=user,
                start_time__gte=start_date
            ).select_related('knowledge_point').order_by('-start_time')[:20]
            
            return sessions
            
        except Exception as e:
            logger.error(f"获取最近活动失败: {e}")
            return []
    
    @staticmethod
    def update_daily_streak(user):
        """更新每日连续学习记录"""
        try:
            profile = user.userprofile
            today = timezone.now().date()
            
            # 检查今天是否已经学习
            today_sessions = StudySession.objects.filter(
                user=user,
                start_time__date=today
            ).exists()
            
            if today_sessions:
                if profile.last_study_date == today:
                    # 今天已经更新过了
                    return profile.current_streak
                elif profile.last_study_date == today - timedelta(days=1):
                    # 连续学习
                    profile.current_streak += 1
                else:
                    # 中断了，重新开始
                    profile.current_streak = 1
                
                profile.last_study_date = today
                if profile.current_streak > profile.longest_streak:
                    profile.longest_streak = profile.current_streak
                
                profile.save()
            
            return profile.current_streak
            
        except Exception as e:
            logger.error(f"更新每日连续学习记录失败: {e}")
            return 0
    
    @staticmethod
    def check_achievements(user):
        """检查并授予成就"""
        try:
            # 获取用户统计数据
            summary = ProgressService.get_user_progress_summary(user)
            
            # 检查各种成就条件
            achievements_to_check = Achievement.objects.filter(is_active=True)
            
            for achievement in achievements_to_check:
                # 检查用户是否已经获得此成就
                if UserAchievement.objects.filter(user=user, achievement=achievement).exists():
                    continue
                
                earned = False
                
                if achievement.condition_type == 'knowledge_points':
                    earned = summary['completed_points'] >= achievement.condition_value
                elif achievement.condition_type == 'study_time':
                    earned = summary['total_study_time_hours'] >= achievement.condition_value
                elif achievement.condition_type == 'streak_days':
                    earned = summary['current_streak'] >= achievement.condition_value
                elif achievement.condition_type == 'first_login':
                    earned = True  # 首次登录成就
                
                if earned:
                    # 授予成就
                    UserAchievement.objects.create(user=user, achievement=achievement)
                    
                    # 奖励积分
                    user.points += achievement.points_reward
                    user.save()
                    
                    logger.info(f"用户 {user.username} 获得成就: {achievement.name}")
            
        except Exception as e:
            logger.error(f"检查成就失败: {e}")
    
    @staticmethod
    def get_learning_calendar(user, year=None, month=None):
        """获取学习日历数据"""
        try:
            if not year:
                year = timezone.now().year
            if not month:
                month = timezone.now().month
            
            # 获取指定月份的学习数据
            start_date = datetime(year, month, 1).date()
            if month == 12:
                end_date = datetime(year + 1, 1, 1).date()
            else:
                end_date = datetime(year, month + 1, 1).date()
            
            # 按日期聚合学习时间
            daily_data = StudySession.objects.filter(
                user=user,
                start_time__date__gte=start_date,
                start_time__date__lt=end_date
            ).extra(
                select={'day': 'date(start_time)'}
            ).values('day').annotate(
                total_time=Sum('duration'),
                session_count=Count('id')
            )
            
            # 转换为日历格式
            calendar_data = {}
            for item in daily_data:
                day = item['day'].day
                calendar_data[day] = {
                    'total_time': item['total_time'],
                    'session_count': item['session_count'],
                    'hours': item['total_time'] // 3600,
                    'minutes': (item['total_time'] % 3600) // 60
                }
            
            return calendar_data
            
        except Exception as e:
            logger.error(f"获取学习日历失败: {e}")
            return {}
