from django.core.management.base import BaseCommand
from users.models import Achievement

class Command(BaseCommand):
    help = '创建初始成就数据'

    def handle(self, *args, **options):
        achievements = [
            # 学习成就
            {
                'name': '初学者',
                'description': '完成第一个知识点的学习',
                'icon': '🌱',
                'category': 'learning',
                'condition_type': 'knowledge_points',
                'condition_value': 1,
                'points_reward': 10,
            },
            {
                'name': '勤奋学习者',
                'description': '完成10个知识点的学习',
                'icon': '📚',
                'category': 'learning',
                'condition_type': 'knowledge_points',
                'condition_value': 10,
                'points_reward': 50,
            },
            {
                'name': '知识探索者',
                'description': '完成50个知识点的学习',
                'icon': '🔍',
                'category': 'learning',
                'condition_type': 'knowledge_points',
                'condition_value': 50,
                'points_reward': 200,
            },
            {
                'name': '学习大师',
                'description': '完成100个知识点的学习',
                'icon': '🎓',
                'category': 'learning',
                'condition_type': 'knowledge_points',
                'condition_value': 100,
                'points_reward': 500,
            },
            
            # 时间成就
            {
                'name': '时间管理者',
                'description': '累计学习时间达到10小时',
                'icon': '⏰',
                'category': 'time',
                'condition_type': 'study_time',
                'condition_value': 10,
                'points_reward': 30,
            },
            {
                'name': '专注学习者',
                'description': '累计学习时间达到50小时',
                'icon': '🎯',
                'category': 'time',
                'condition_type': 'study_time',
                'condition_value': 50,
                'points_reward': 100,
            },
            {
                'name': '学习马拉松',
                'description': '累计学习时间达到100小时',
                'icon': '🏃',
                'category': 'time',
                'condition_type': 'study_time',
                'condition_value': 100,
                'points_reward': 300,
            },
            
            # 连续成就
            {
                'name': '坚持不懈',
                'description': '连续学习3天',
                'icon': '🔥',
                'category': 'streak',
                'condition_type': 'streak_days',
                'condition_value': 3,
                'points_reward': 20,
            },
            {
                'name': '学习习惯',
                'description': '连续学习7天',
                'icon': '💪',
                'category': 'streak',
                'condition_type': 'streak_days',
                'condition_value': 7,
                'points_reward': 50,
            },
            {
                'name': '学习达人',
                'description': '连续学习30天',
                'icon': '🌟',
                'category': 'streak',
                'condition_type': 'streak_days',
                'condition_value': 30,
                'points_reward': 200,
            },
            
            # 特殊成就
            {
                'name': '新手上路',
                'description': '首次登录平台',
                'icon': '🚀',
                'category': 'special',
                'condition_type': 'first_login',
                'condition_value': 1,
                'points_reward': 5,
            },
        ]
        
        created_count = 0
        for achievement_data in achievements:
            achievement, created = Achievement.objects.get_or_create(
                name=achievement_data['name'],
                defaults=achievement_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'创建成就: {achievement.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'成就已存在: {achievement.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'成就创建完成! 新创建了 {created_count} 个成就')
        )
