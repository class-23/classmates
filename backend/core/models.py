import uuid
import secrets
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """自定义用户模型 - 以邮箱为登录凭证"""
    email = models.EmailField(unique=True, verbose_name='邮箱')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return self.email


class Notebook(models.Model):
    """同学录模型"""
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='notebooks', verbose_name='创建者'
    )
    title = models.CharField(max_length=100, verbose_name='同学录名称')
    title_slug = models.SlugField(max_length=100, unique=True, null=True, blank=True, verbose_name='名称标识', allow_unicode=True)
    share_code = models.UUIDField(
        unique=True, default=uuid.uuid4, editable=False,
        verbose_name='分享标识'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '同学录'
        verbose_name_plural = '同学录'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title}（{self.owner.email}）'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_title = self.title

    def save(self, *args, **kwargs):
        if not self.title_slug or self.title != self._original_title:
            self.title_slug = self._generate_title_slug()
            self._original_title = self.title
        super().save(*args, **kwargs)

    def _generate_title_slug(self):
        """生成唯一的title_slug"""
        slug = self.title
        counter = 1
        base_slug = slug
        while Notebook.objects.filter(title_slug=slug).exclude(pk=self.pk).exists():
            counter += 1
            slug = f'{base_slug}-{counter}'
        return slug


class Student(models.Model):
    """同学信息模型（核心表）"""
    notebook = models.ForeignKey(
        Notebook, on_delete=models.CASCADE,
        related_name='students', verbose_name='所属同学录'
    )
    edit_code = models.CharField(
        max_length=64, unique=True, null=True, blank=True,
        editable=False, verbose_name='编辑码'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='首次提交时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='最后修改时间')
    edit_deadline = models.DateTimeField(null=True, blank=True, verbose_name='编辑截止时间')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='删除时间')
    restore_deadline = models.DateTimeField(null=True, blank=True, verbose_name='还原截止时间')
    name_slug = models.SlugField(max_length=100, null=True, blank=True, verbose_name='姓名标识', allow_unicode=True)

    # 必填字段（7个）
    name = models.CharField(max_length=50, verbose_name='名字')
    nickname = models.CharField(max_length=50, verbose_name='昵称')
    phone = models.CharField(max_length=20, verbose_name='电话')
    wechat = models.CharField(max_length=50, verbose_name='微信')
    first_impression = models.TextField(verbose_name='对我的第一印象')
    words_to_me = models.TextField(verbose_name='想对我说的话')
    message = models.TextField(verbose_name='留言')

    # 选填字段（20个）
    birthday = models.DateField(null=True, blank=True, verbose_name='生日')
    zodiac_sign = models.CharField(max_length=10, null=True, blank=True, verbose_name='生肖')
    constellation = models.CharField(max_length=10, null=True, blank=True, verbose_name='星座')
    qq = models.CharField(max_length=20, null=True, blank=True, verbose_name='QQ号')
    xiaohongshu = models.CharField(max_length=100, null=True, blank=True, verbose_name='小红书号')
    douyin = models.CharField(max_length=100, null=True, blank=True, verbose_name='抖音号')
    email = models.EmailField(null=True, blank=True, verbose_name='邮箱')
    address = models.TextField(null=True, blank=True, verbose_name='地址')
    hobbies = models.TextField(null=True, blank=True, verbose_name='兴趣爱好')
    motto = models.TextField(null=True, blank=True, verbose_name='座右铭')
    crush = models.TextField(null=True, blank=True, verbose_name='喜欢谁')
    dislike = models.TextField(null=True, blank=True, verbose_name='讨厌谁')
    wish = models.TextField(null=True, blank=True, verbose_name='愿望')
    dream = models.TextField(null=True, blank=True, verbose_name='梦想')
    favorite_food = models.TextField(null=True, blank=True, verbose_name='喜欢吃什么')
    most_want_to_see = models.TextField(null=True, blank=True, verbose_name='最想见的人')
    favorite_movie = models.TextField(null=True, blank=True, verbose_name='喜欢看什么电影')
    favorite_music = models.TextField(null=True, blank=True, verbose_name='喜欢听什么歌')
    most_want_to_go = models.TextField(null=True, blank=True, verbose_name='最想去哪')
    most_unforgettable = models.TextField(null=True, blank=True, verbose_name='最难忘的事')
    hope_10_years = models.TextField(null=True, blank=True, verbose_name='希望10年后的我们')

    class Meta:
        verbose_name = '同学信息'
        verbose_name_plural = '同学信息'
        indexes = [
            models.Index(fields=['notebook', 'name']),
        ]

    def __str__(self):
        return f'{self.name}（{self.notebook.title}）'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_name = self.name

    def save(self, *args, **kwargs):
        if not self.name_slug or self.name != self._original_name:
            self.name_slug = self._generate_name_slug()
            self._original_name = self.name
        super().save(*args, **kwargs)

    def _generate_name_slug(self):
        """生成唯一的name_slug（在同一notebook内唯一）"""
        slug = self.name
        counter = 1
        base_slug = slug
        while Student.objects.filter(
            notebook=self.notebook, name_slug=slug
        ).exclude(pk=self.pk).exists():
            counter += 1
            slug = f'{base_slug}-{counter}'
        return slug

    def generate_edit_code(self):
        self.edit_code = secrets.token_urlsafe(16)
        self.edit_deadline = timezone.now() + timedelta(days=3)
        return self.edit_code

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.restore_deadline = timezone.now() + timedelta(days=10)
        self.save(update_fields=['is_deleted', 'deleted_at', 'restore_deadline'])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.restore_deadline = None
        self.save(update_fields=['is_deleted', 'deleted_at', 'restore_deadline'])

    def can_edit(self):
        if not self.edit_deadline:
            return False
        return timezone.now() <= self.edit_deadline


def student_upload_path(instance, filename):
    ext = filename.split('.')[-1] if '.' in filename else ''
    name = uuid.uuid4().hex
    return f'student_{instance.student_id}/{name}.{ext}'


class MediaFile(models.Model):
    """媒体文件模型"""
    PHOTO = 'photo'
    VIDEO = 'video'
    FILE_TYPE_CHOICES = [(PHOTO, '照片'), (VIDEO, '视频')]

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE,
        related_name='media_files', verbose_name='所属同学'
    )
    file = models.FileField(upload_to=student_upload_path, verbose_name='文件')
    file_type = models.CharField(
        max_length=10, choices=FILE_TYPE_CHOICES, verbose_name='文件类型'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')
    file_size = models.BigIntegerField(null=True, blank=True, verbose_name='文件大小(字节)')

    class Meta:
        verbose_name = '媒体文件'
        verbose_name_plural = '媒体文件'

    def __str__(self):
        return f'{self.get_file_type_display()}-{self.id}'


class VerificationCode(models.Model):
    """邮箱验证码模型"""
    email = models.EmailField(verbose_name='邮箱')
    code = models.CharField(max_length=6, verbose_name='验证码')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    expires_at = models.DateTimeField(verbose_name='过期时间')
    is_used = models.BooleanField(default=False, verbose_name='是否已使用')

    class Meta:
        verbose_name = '验证码'
        verbose_name_plural = '验证码'
        indexes = [
            models.Index(fields=['email', 'code', 'expires_at']),
        ]

    def __str__(self):
        return f'{self.email} - {self.code}'

    def is_valid(self):
        return not self.is_used and timezone.now() <= self.expires_at
