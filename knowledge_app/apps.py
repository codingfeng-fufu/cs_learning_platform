from django.apps import AppConfig
import os
import sys


class KnowledgeAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'knowledge_app'
    verbose_name = '知识点管理'

    def ready(self):
        """应用准备就绪时的回调"""
        # 检查是否应该启动调度器
        should_start = (
            os.environ.get('RUN_MAIN') == 'true' or  # Django开发服务器
            os.environ.get('START_SCHEDULER') == 'true' or  # 明确设置启动
            'runserver' in ' '.join(sys.argv)  # runserver命令
        )

        if should_start:
            self.start_daily_term_scheduler()
        else:
            print("跳过调度器启动")
            print(f"   RUN_MAIN: {os.environ.get('RUN_MAIN')}")
            print(f"   START_SCHEDULER: {os.environ.get('START_SCHEDULER')}")

    def start_daily_term_scheduler(self):
        """启动每日名词调度器"""
        try:
            print("准备启动高级每日名词调度器...")

            # 延迟启动，确保Django完全初始化
            def delayed_start():
                import time
                time.sleep(3)  # 等待3秒

                try:
                    # 优先使用高级调度器
                    from .services.advanced_scheduler import start_advanced_scheduler
                    scheduler = start_advanced_scheduler()
                    print("高级定时调度器已启动（支持精确零点触发）")

                except ImportError as e:
                    print(f"高级调度器不可用，使用基础调度器: {e}")
                    # 回退到基础调度器
                    try:
                        from .management.commands.start_daily_term_scheduler import DailyTermScheduler
                        scheduler = DailyTermScheduler()

                        # 立即检查一次
                        print("立即检查是否需要生成今日名词...")
                        scheduler.check_and_generate_daily_term()

                        # 启动定时检查
                        print("启动定时检查...")
                        scheduler.start_scheduler()

                        print("基础调度器已启动")

                    except Exception as e2:
                        print(f"基础调度器也启动失败: {e2}")
                        import traceback
                        traceback.print_exc()

                except Exception as e:
                    print(f"调度器启动失败: {e}")
                    import traceback
                    traceback.print_exc()

            # 在后台线程中启动
            import threading
            scheduler_thread = threading.Thread(target=delayed_start, daemon=True)
            scheduler_thread.start()

        except Exception as e:
            print(f"启动每日名词调度器失败: {e}")
            import traceback
            traceback.print_exc()
