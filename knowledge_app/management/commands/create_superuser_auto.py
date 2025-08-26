"""
自动创建超级用户的Django管理命令

运行方式:
python manage.py create_superuser_auto
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import IntegrityError


class Command(BaseCommand):
    help = '自动创建开发用的超级用户账号'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='超级用户用户名 (默认: admin)',
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@example.com',
            help='超级用户邮箱 (默认: admin@example.com)',
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='超级用户密码 (默认: admin123)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='如果用户已存在，删除后重新创建',
        )

    def handle(self, *args, **options):
        """执行命令的主要逻辑"""

        username = options['username']
        email = options['email']
        password = options['password']
        force = options['force']

        # 检查用户是否已存在
        if User.objects.filter(username=username).exists():
            if force:
                self.stdout.write(
                    self.style.WARNING(f'删除现有用户: {username}')
                )
                User.objects.filter(username=username).delete()
            else:
                self.stdout.write(
                    self.style.WARNING(f'用户 {username} 已存在')
                )
                self.stdout.write(
                    self.style.HTTP_INFO('使用 --force 参数强制重新创建')
                )
                return

        try:
            # 创建超级用户
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )

            self.stdout.write(
                self.style.SUCCESS(f'✅ 超级用户创建成功!')
            )
            self.stdout.write('')
            self.stdout.write('📝 登录信息:')
            self.stdout.write(f'   用户名: {username}')
            self.stdout.write(f'   密码:   {password}')
            self.stdout.write(f'   邮箱:   {email}')
            self.stdout.write('')
            self.stdout.write('🌐 管理后台地址: http://127.0.0.1:8000/admin/')
            self.stdout.write('')
            self.stdout.write(
                self.style.WARNING('⚠️  请在生产环境中修改默认密码!')
            )

        except IntegrityError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ 创建用户失败: {str(e)}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ 意外错误: {str(e)}')
            )