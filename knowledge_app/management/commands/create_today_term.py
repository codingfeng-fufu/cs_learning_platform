from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date
from knowledge_app.models import DailyTerm


class Command(BaseCommand):
    help = '创建今天的名词'

    def handle(self, *args, **options):
        # 检查今天是否已有名词
        today = date(2025, 8, 3)
        existing = DailyTerm.objects.filter(display_date=today, status='active').first()
        
        if existing:
            self.stdout.write(f"今天已有名词: {existing.term}")
            return
        
        # 创建今天的名词
        today_term = DailyTerm.objects.create(
            term="机器学习",
            explanation="机器学习是人工智能的一个重要分支，它使计算机系统能够通过经验自动改进性能，而无需明确编程。机器学习的核心思想是让计算机从数据中学习模式和规律，然后利用这些学到的知识对新数据进行预测或决策。主要类型包括：监督学习 - 使用标记数据训练模型进行预测；无监督学习 - 从未标记数据中发现隐藏模式；强化学习 - 通过与环境交互学习最优策略。常见算法有线性回归、决策树、神经网络、支持向量机等。机器学习广泛应用于图像识别、自然语言处理、推荐系统、自动驾驶等领域，是现代AI技术的基础。",
            category="人工智能",
            difficulty_level="intermediate",
            display_date=today,
            status="active",
            extended_info={
                "examples": ["TensorFlow", "PyTorch", "scikit-learn", "Keras"],
                "related_concepts": ["深度学习", "神经网络", "数据挖掘", "模式识别"],
                "applications": ["图像识别", "语音识别", "推荐系统", "自然语言处理"]
            }
        )
        
        self.stdout.write(
            self.style.SUCCESS(f"✅ 成功创建今日名词: {today_term.term}")
        )
