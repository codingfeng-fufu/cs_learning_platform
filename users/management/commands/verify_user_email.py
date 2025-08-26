from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):
    help = '手动验证用户邮箱（开发环境使用）'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='要验证的用户邮箱')

    def handle(self, *args, **options):
        email = options['email']
        
        try:
            user = User.objects.get(email=email)
            if user.is_email_verified:
                self.stdout.write(
                    self.style.WARNING(f'用户 {email} 的邮箱已经验证过了')
                )
            else:
                user.is_email_verified = True
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'成功验证用户 {email} 的邮箱')
                )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'用户 {email} 不存在')
            )
