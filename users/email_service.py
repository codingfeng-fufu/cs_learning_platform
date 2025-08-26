from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from .models import EmailVerificationToken, PasswordResetToken
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """邮件服务类"""
    
    @staticmethod
    def send_verification_email(user, request):
        """发送邮箱验证邮件"""
        try:
            # 创建验证令牌
            token = EmailVerificationToken.objects.create(user=user)
            
            # 构建验证链接
            verification_url = request.build_absolute_uri(
                reverse('users:verify_email', kwargs={'token': token.token})
            )
            
            # 邮件内容
            subject = '验证您的邮箱 - 计算机科学学习平台'
            html_message = render_to_string('users/emails/verification_email.html', {
                'user': user,
                'verification_url': verification_url,
                'site_name': '计算机科学学习平台'
            })
            plain_message = strip_tags(html_message)
            
            # 发送邮件
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"验证邮件已发送给用户: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"发送验证邮件失败: {user.email}, 错误: {str(e)}")
            return False
    
    @staticmethod
    def send_password_reset_email(user, request):
        """发送密码重置邮件"""
        try:
            # 创建重置令牌
            token = PasswordResetToken.objects.create(user=user)
            
            # 构建重置链接
            reset_url = request.build_absolute_uri(
                reverse('users:password_reset_confirm', kwargs={'token': token.token})
            )
            
            # 邮件内容
            subject = '重置您的密码 - 计算机科学学习平台'
            html_message = render_to_string('users/emails/password_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
                'site_name': '计算机科学学习平台',
                'expires_hours': 1
            })
            plain_message = strip_tags(html_message)
            
            # 发送邮件
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"密码重置邮件已发送给用户: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"发送密码重置邮件失败: {user.email}, 错误: {str(e)}")
            return False
    
    @staticmethod
    def send_welcome_email(user):
        """发送欢迎邮件"""
        try:
            subject = '欢迎加入计算机科学学习平台！'
            html_message = render_to_string('users/emails/welcome_email.html', {
                'user': user,
                'site_name': '计算机科学学习平台'
            })
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"欢迎邮件已发送给用户: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"发送欢迎邮件失败: {user.email}, 错误: {str(e)}")
            return False
    
    @staticmethod
    def send_password_changed_notification(user):
        """发送密码修改通知邮件"""
        try:
            subject = '密码修改通知 - 计算机科学学习平台'
            html_message = render_to_string('users/emails/password_changed_email.html', {
                'user': user,
                'site_name': '计算机科学学习平台',
                'change_time': timezone.now()
            })
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"密码修改通知已发送给用户: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"发送密码修改通知失败: {user.email}, 错误: {str(e)}")
            return False
