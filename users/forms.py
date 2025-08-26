from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import User, UserProfile

class UserRegistrationForm(UserCreationForm):
    """用户注册表单"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入邮箱地址',
            'autocomplete': 'email'
        })
    )
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入用户名',
            'autocomplete': 'username'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入姓名（可选）',
            'autocomplete': 'given-name'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入密码',
            'autocomplete': 'new-password'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '请确认密码',
            'autocomplete': 'new-password'
        })
    )
    
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('该邮箱已被注册')
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('该用户名已被使用')
        return username
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # 创建用户档案
            UserProfile.objects.create(user=user)
        return user


class UserLoginForm(AuthenticationForm):
    """用户登录表单"""
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入邮箱地址',
            'autocomplete': 'email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入密码',
            'autocomplete': 'current-password'
        })
    )
    
    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if email and password:
            self.user_cache = authenticate(
                self.request, 
                username=email, 
                password=password
            )
            if self.user_cache is None:
                raise ValidationError('邮箱或密码错误')
            else:
                self.confirm_login_allowed(self.user_cache)
        
        return self.cleaned_data


class CustomPasswordResetForm(PasswordResetForm):
    """自定义密码重置表单"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入注册邮箱',
            'autocomplete': 'email'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise ValidationError('该邮箱未注册')
        return email


class UserProfileForm(forms.ModelForm):
    """用户资料表单"""
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入姓名'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入姓氏'
        })
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': '介绍一下自己...',
            'rows': 4
        })
    )
    location = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '所在城市'
        })
    )
    website = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://example.com'
        })
    )
    github_username = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'GitHub用户名'
        })
    )
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'bio', 'location', 'website', 'github_username')


class UserPreferencesForm(forms.ModelForm):
    """用户偏好设置表单"""
    preferred_language = forms.ChoiceField(
        choices=[
            ('zh', '中文'),
            ('en', 'English'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    email_notifications = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = User
        fields = ('preferred_language', 'email_notifications')


class StudyGoalForm(forms.ModelForm):
    """学习目标设置表单"""
    study_goal = forms.ChoiceField(
        choices=[
            ('beginner', '入门学习'),
            ('interview', '面试准备'),
            ('advanced', '深入研究'),
            ('review', '复习巩固'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    daily_study_goal = forms.IntegerField(
        min_value=5,
        max_value=480,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '每日学习目标（分钟）'
        })
    )
    
    class Meta:
        model = UserProfile
        fields = ('study_goal', 'daily_study_goal')
