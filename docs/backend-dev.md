# 同学录 — 后端开发文档（完整版）

> **项目路径：** `/var/minis/workspace/classmates-book/`
> **技术栈：** Python 3.12 + Django 6.0 + PostgreSQL 16
> **部署方式：** Docker（`docker compose up -d --build`）或 非 Docker（`python main.py`）
> **最后更新：** 2026-07-29

---

## 一、项目目录结构（完整版）

```
classmates-book/                          # 项目根目录
│
├── main.py                               # ★ 非 Docker 统一入口
│                                         #   python main.py → 启动开发服务器
│
├── requirements.txt                      # Python 依赖清单
│
├── docker-compose.yml                    # ★ Docker 编排文件
│                                         #   docker compose up -d --build
│
├── deploy/                               # 部署配置
│   ├── Dockerfile                        #   生产镜像（gunicorn + 4 workers）
│   ├── nginx.conf                        #   （可选）Nginx 反向代理配置
│   └── entrypoint.sh                     #   （可选）Docker 启动脚本
│
├── scripts/                              # 运维脚本
│   ├── cleanup_trash.py                  #   Django 管理命令：清理过期回收站
│   ├── seed_data.py                      #   测试数据填充脚本
│   └── backup_db.sh                      #   数据库备份脚本
│
├── docs/                                 # 项目文档
│   ├── backend-dev.md                    #   本文件：后端开发文档
│   ├── database-design.md                #   数据库设计文档
│   └── frontend-dev.md                   #   前端开发文档
│
├── backend/                              # ★ Django 项目
│   ├── manage.py                         #   Django 管理入口
│   │
│   ├── config/                           #   项目配置（Django project）
│   │   ├── __init__.py
│   │   ├── settings.py                   #   ★ 全局配置（数据库/邮箱/媒体文件/CORS等）
│   │   ├── urls.py                       #   ★ 根路由（URL → 视图）
│   │   ├── wsgi.py                       #   WSGI 生产入口
│   │   └── asgi.py                       #   ASGI 入口（预留）
│   │
│   ├── core/                             #   ★ 同学录主应用
│   │   ├── __init__.py
│   │   ├── admin.py                      #   Admin 后台注册（管理员端预留）
│   │   ├── apps.py                       #   应用配置
│   │   ├── models.py                     #   ★ 数据模型（User/Notebook/Student/MediaFile/VerificationCode）
│   │   ├── views.py                      #   ★ 视图函数（全部业务逻辑）
│   │   ├── forms.py                      #   ★ 表单验证（Django Form）
│   │   ├── utils.py                      #   ★ 工具函数（验证码/编辑码/邮件发送）
│   │   ├── decorators.py                 #   自定义装饰器（如 notebook_owner_required）
│   │   ├── urls.py                       #   ★ 子路由
│   │   ├── management/                   #   自定义管理命令
│   │   │   └── commands/
│   │   │       └── cleanup_trash.py      #   清理回收站命令
│   │   │
│   │   ├── templates/core/               #   ★ 前端模板文件
│   │   │   ├── base.html                 #     基础骨架
│   │   │   ├── home.html                 #     首页落地页
│   │   │   ├── register.html             #     注册页
│   │   │   ├── login.html                #     登录页
│   │   │   ├── dashboard.html            #     我的同学录
│   │   │   ├── notebook_create.html      #     新建同学录
│   │   │   ├── notebook_detail.html      #     同学录详情（搜索+列表+删除）
│   │   │   ├── notebook_trash.html       #     回收站
│   │   │   ├── fill_form.html            #     填写/编辑表单
│   │   │   ├── fill_success.html         #     提交成功
│   │   │   └── student_detail.html       #     同学详情
│   │   │
│   │   ├── static/core/                  #   静态资源
│   │   │   ├── css/
│   │   │   │   └── style.css             #     设计系统 CSS
│   │   │   ├── js/
│   │   │   │   └── main.js               #     （可选）分离的 JS
│   │   │   └── uploads/                  #     ★ 用户上传文件存储
│   │   │       └── .gitkeep
│   │   │
│   │   └── migrations/                   #   数据库迁移文件
│   │       └── __init__.py
│   │
│   ├── templates/                        #   公共模板目录（扩展用）
│   └── static/                           #   公共静态目录（扩展用）
│
└── design-system/                        # UI/UX Pro Max 设计系统
    └── default/
        └── MASTER.md                     #   设计系统主文档
```

---

## 二、URL 路由表（完整版）

### 2.1 `config/urls.py`（根路由）

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [
    # 公开页面
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # API 接口
    path('api/send-verification-code/', views.send_verification_code, name='send_code'),

    # 同学录 CRUD
    path('dashboard/', views.dashboard, name='dashboard'),
    path('notebook/create/', views.notebook_create, name='notebook_create'),
    path('notebook/<int:notebook_id>/', views.notebook_detail, name='notebook_detail'),
    path('notebook/<int:notebook_id>/search/', views.notebook_search, name='notebook_search'),
    path('notebook/<int:notebook_id>/delete/<int:student_id>/', views.delete_student, name='delete_student'),
    path('notebook/<int:notebook_id>/restore/<int:student_id>/', views.restore_student, name='restore_student'),
    path('notebook/<int:notebook_id>/hard-delete/<int:student_id>/', views.hard_delete_student, name='hard_delete_student'),
    path('notebook/<int:notebook_id>/trash/', views.notebook_trash, name='notebook_trash'),
    path('notebook/<int:notebook_id>/empty-trash/', views.empty_trash, name='empty_trash'),

    # 分享与填写
    path('join/<uuid:share_code>/', views.fill_form, name='fill_form'),
    path('join/<uuid:share_code>/success/', views.fill_success, name='fill_success'),

    # 编辑
    path('edit/<str:edit_code>/', views.edit_form, name='edit_form'),

    # 同学详情
    path('student/<int:student_id>/', views.student_detail, name='student_detail'),
]

# 媒体文件路由（开发环境）
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 2.2 路由参数说明

| 参数 | 类型 | 来源 | 说明 |
|------|------|------|------|
| `notebook_id` | `int` | URL 路径 | 同学录 ID，如 `/notebook/3/` |
| `student_id` | `int` | URL 路径 | 同学信息 ID，如 `/student/15/` |
| `share_code` | `uuid` | URL 路径 | 同学录分享 UUID，如 `/join/a1b2c3d4-.../` |
| `edit_code` | `str` | URL 路径 | 编辑码，如 `/edit/abc123.../` |

---

## 三、视图函数完整规格

### 3.1 公开页面

#### `home(request)`
- **方法：** GET
- **权限：** 公开
- **模板：** `core/home.html`
- **上下文：** `{}`（无动态数据）
- **逻辑：** 渲染首页落地页

#### `register(request)`
- **方法：** GET / POST
- **权限：** 仅未登录
- **模板：** `core/register.html`

**POST 处理逻辑：**
```
1. 接收表单：email, verification_code, password, confirm_password
2. 校验：
   a. email 格式是否合法
   b. email 是否已被注册
   c. 验证码是否匹配 & 未过期 & 未使用
   d. password 长度 >= 8
   e. password === confirm_password
3. 若校验失败 → 渲染表单 + 错误信息（messages.error）
4. 若校验通过：
   a. 标记验证码为已使用
   b. 创建 User（email=email, username=email）
   c. 设置密码（user.set_password）
   d. 跳转 /login/ + 成功提示
```

#### `user_login(request)`
- **方法：** GET / POST
- **权限：** 仅未登录
- **模板：** `core/login.html`

**POST 处理逻辑：**
```
1. 接收表单：email, password
2. 用 email 查询 User
3. authenticate(email=email, password=password)
4. 成功 → login(request, user) → 重定向 /dashboard/
5. 失败 → 渲染表单 + 错误提示
```

#### `user_logout(request)`
- **方法：** GET
- **权限：** 已登录
- **逻辑：** `logout(request)` → 重定向 `/login/`

### 3.2 API 接口

#### `send_verification_code(request)`
- **方法：** POST
- **权限：** 公开
- **请求格式：** `{"email": "xxx@example.com"}`
- **响应格式：** `{"code": 200, "message": "验证码已发送"}` 或 `{"code": 400, "message": "..."}`

**处理逻辑：**
```
1. 解析 JSON body，获取 email
2. 校验 email 格式
3. 检查是否已注册（已注册则返回错误）
4. 检查 60 秒内是否已发送（防止刷接口）
5. 生成 6 位随机数字验证码（random.randint(100000, 999999)）
6. 存入 VerificationCode 表（设置 5 分钟过期）
7. 通过 QQ 邮箱 SMTP 发送验证码邮件
8. 返回成功响应
```

**防刷策略：**
- 同一邮箱 60 秒内不允许重复发送
- 使用 `VerificationCode` 表的 `created_at` 字段判断

### 3.3 同学录 CRUD（需登录）

#### `dashboard(request)`
- **方法：** GET
- **权限：** `@login_required`
- **模板：** `core/dashboard.html`

```python
context = {
    'notebooks': Notebook.objects.filter(owner=request.user)
        .annotate(student_count=Count('students', filter=Q(students__is_deleted=False)))
        .order_by('-created_at')
}
```

#### `notebook_create(request)`
- **方法：** GET / POST
- **权限：** `@login_required`
- **模板：** `core/notebook_create.html`

**POST 逻辑：**
```
1. 接收 title
2. title 校验（非空，max_length=100）
3. 创建 Notebook(owner=request.user, title=title)
4. share_code 自动由 default=uuid.uuid4 生成
5. 重定向到 /notebook/<id>/
```

#### `notebook_detail(request, notebook_id)`
- **方法：** GET
- **权限：** `@login_required` + 仅创建者
- **模板：** `core/notebook_detail.html`

```python
# 权限校验
notebook = get_object_or_404(Notebook, id=notebook_id)
if notebook.owner != request.user:
    return redirect('dashboard')

context = {
    'notebook': notebook,
    'students': Student.objects.filter(notebook=notebook, is_deleted=False)
        .order_by('name'),
}
```

#### `delete_student(request, notebook_id, student_id)`
- **方法：** POST
- **权限：** `@login_required` + 仅创建者
- **逻辑：** 软删除 → `student.soft_delete()` → 重定向回详情页
- **注意：** 需要 CSRF token

#### `restore_student(request, notebook_id, student_id)`
- **方法：** POST
- **权限：** `@login_required` + 仅创建者
- **逻辑：** `student.restore()` → 重定向回收站

#### `hard_delete_student(request, notebook_id, student_id)`
- **方法：** POST
- **权限：** `@login_required` + 仅创建者
- **逻辑：**
  ```
  1. 获取 student（需 is_deleted=True 且在还原期内）
  2. 删除关联的 MediaFile 文件
  3. student.delete()（级联删除 MediaFile 记录）
  4. 重定向回收站
  ```

#### `empty_trash(request, notebook_id)`
- **方法：** POST
- **权限：** `@login_required` + 仅创建者
- **逻辑：** 遍历所有 `is_deleted=True` 的记录，删除文件后硬删除

#### `notebook_trash(request, notebook_id)`
- **方法：** GET
- **权限：** `@login_required` + 仅创建者
- **模板：** `core/notebook_trash.html`

```python
context = {
    'notebook': notebook,
    'trash_items': Student.objects.filter(notebook=notebook, is_deleted=True)
        .order_by('-deleted_at'),
}
```

#### `notebook_search(request, notebook_id)`
- **方法：** GET
- **权限：** `@login_required` + 仅创建者
- **参数：** `?q=张三`
- **响应：** 渲染 `notebook_detail.html` 带过滤

```python
students = Student.objects.filter(notebook=notebook, is_deleted=False)
q = request.GET.get('q', '').strip()
if q:
    students = students.filter(name__icontains=q)
```

### 3.4 分享与填写（公开）

#### `fill_form(request, share_code)`
- **方法：** GET / POST
- **权限：** 公开
- **模板：** `core/fill_form.html`

**GET 逻辑：**
```
1. 通过 share_code 查找 Notebook
2. 渲染填写表单（不含 edit_mode）
```

**POST 逻辑：**
```
1. 解析 request.POST + request.FILES
2. 校验必填字段（name, nickname, phone, wechat, first_impression, words_to_me, message）
3. 创建 Student 记录
4. 调用 student.generate_edit_code() 生成编辑码
5. 处理上传文件：
   - photos = request.FILES.getlist('photos')
   - videos = request.FILES.getlist('videos')
   - 遍历创建 MediaFile 记录
6. 跳转 /join/<share_code>/success/?code=<edit_code>
```

#### `fill_success(request, share_code)`
- **方法：** GET
- **权限：** 公开
- **模板：** `core/fill_success.html`

```python
edit_code = request.GET.get('code', '')
context = {
    'notebook': notebook,
    'edit_code': edit_code,
}
```

### 3.5 编辑（公开，需有效编辑码）

#### `edit_form(request, edit_code)`
- **方法：** GET / POST
- **权限：** 公开（需有效编辑码）

**GET 逻辑：**
```
1. 通过 edit_code 查找 Student
2. 校验 edit_deadline > now()（未过期）
3. 渲染 fill_form.html（edit_mode=True）
```

**POST 逻辑：**
```
1. 校验编辑码有效且未过期
2. 更新 Student 字段
3. 删除勾选的旧文件（delete_photos[] / delete_videos[]）
4. 处理新上传的文件
5. 重定向到 /edit/<edit_code>/ + 成功提示
```

### 3.6 同学详情

#### `student_detail(request, student_id)`
- **方法：** GET
- **权限：** `@login_required` + 仅创建者
- **模板：** `core/student_detail.html`

```python
student = get_object_or_404(Student, id=student_id, is_deleted=False)
notebook = student.notebook
# 权限检查：只有 notebook 的创建者可查看
if notebook.owner != request.user:
    return redirect('dashboard')

context = {
    'notebook': notebook,
    'student': student,
    'media_files': MediaFile.objects.filter(student=student).order_by('file_type'),
}
```

---

## 四、表单验证设计

文件路径：`backend/core/forms.py`

### 4.1 `RegisterForm`

```python
class RegisterForm(forms.Form):
    email = forms.EmailField(
        label='邮箱',
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': '请输入邮箱地址'})
    )
    verification_code = forms.CharField(
        label='验证码',
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '6位数字验证码'})
    )
    password = forms.CharField(
        label='密码',
        min_length=8,
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': '至少8位密码'})
    )
    confirm_password = forms.CharField(
        label='确认密码',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': '再次输入密码'})
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱已被注册')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')
        if password and confirm and password != confirm:
            raise forms.ValidationError('两次密码输入不一致')
        return cleaned_data
```

### 4.2 `StudentForm`

```python
class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'name', 'nickname', 'phone', 'wechat',
            'first_impression', 'words_to_me', 'message',
            'birthday', 'zodiac_sign', 'constellation',
            'qq', 'xiaohongshu', 'douyin', 'email', 'address',
            'hobbies', 'motto', 'crush', 'dislike',
            'wish', 'dream', 'favorite_food',
            'most_want_to_see', 'favorite_movie', 'favorite_music',
            'most_want_to_go', 'most_unforgettable', 'hope_10_years',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '你的真实姓名'}),
            'nickname': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '大家怎么叫你？'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '手机号码'}),
            'wechat': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '微信号'}),
            'first_impression': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': '还记得第一次见到我的感觉吗？'}),
            'words_to_me': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': '有什么想对我说的话？'}),
            'message': forms.Textarea(attrs={'class': 'form-textarea tall', 'placeholder': '写下你想对大家说的话…'}),
            'birthday': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'hobbies': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': '平时喜欢做什么？'}),
            'motto': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '你最喜欢的一句话'}),
        }
```

---

## 五、工具函数设计

文件路径：`backend/core/utils.py`

### 5.1 验证码生成

```python
import random
import string

def generate_verification_code(length=6):
    """生成 N 位纯数字验证码"""
    return ''.join(random.choices(string.digits, k=length))
```

### 5.2 编辑码生成

```python
import secrets

def generate_edit_code():
    """生成 URL 安全的随机编辑码（24 字符）"""
    return secrets.token_urlsafe(16)  # 输出长度约 22-24 字符
```

### 5.3 邮件发送

```python
from django.core.mail import send_mail
from django.conf import settings

def send_verification_email(to_email, code):
    """发送验证码邮件"""
    subject = '同窗录 - 邮箱验证码'
    message = f"""
    您好！

    您的同窗录注册验证码为：{code}

    该验证码有效期为 5 分钟，请尽快完成注册。
    如非本人操作，请忽略此邮件。

    —— 同窗录团队
    """
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to_email],
        fail_silently=False,
    )
```

### 5.4 文件路径生成

```python
import uuid
import os

def student_upload_path(instance, filename):
    """生成媒体文件存储路径"""
    ext = filename.split('.')[-1] if '.' in filename else ''
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    return f"student_{instance.student_id}/{unique_name}"
```

---

## 六、Settings 完整配置

文件路径：`backend/config/settings.py`

### 6.1 Django 基础配置

```python
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-dev-key-change-in-production')
DEBUG = os.getenv('DJANGO_DEBUG', 'true').lower() == 'true'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',  # 同学录主应用
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
```

### 6.2 数据库配置

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'classmates'),
        'USER': os.getenv('DB_USER', 'classmates'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'classmates_secret'),
        'HOST': os.getenv('DB_HOST', 'localhost'),  # Docker 部署时为 'db'
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': 60,  # 连接复用
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}
```

### 6.3 邮件配置

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '3450806816@qq.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')  # 用户提供授权码
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

### 6.4 用户模型与认证

```python
AUTH_USER_MODEL = 'core.User'  # 自定义用户模型

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

AUTHENTICATION_BACKENDS = [
    'core.backends.EmailAuthBackend',  # 自定义邮箱认证
    'django.contrib.auth.backends.ModelBackend',
]
```

### 6.5 媒体与静态文件

```python
MEDIA_URL = '/uploads/'
MEDIA_ROOT = BASE_DIR / 'core' / 'static' / 'core' / 'uploads'

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'core' / 'static',
]

# 上传文件大小限制（无限制，但建议前端做提示）
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50MB
```

### 6.6 其他配置

```python
# 默认主键类型
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 语言与时区
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# 会话超时（7天）
SESSION_COOKIE_AGE = 7 * 24 * 60 * 60
```

---

## 七、权限控制设计

### 7.1 权限层级

| 层级 | 权限 | 对象 | 说明 |
|------|------|------|------|
| L0 | 公开 | 所有用户 | 首页、注册、登录、填写表单、编辑表单 |
| L1 | 已登录 | 认证用户 | 仪表盘、创建同学录 |
| L2 | 仅创建者 | Notebook.owner | 同学录详情、回收站、同学详情、删除/还原 |

### 7.2 装饰器 `@notebook_owner_required`

```python
# decorators.py
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from functools import wraps
from .models import Notebook

def notebook_owner_required(view_func):
    @wraps(view_func)
    def wrapper(request, notebook_id, *args, **kwargs):
        notebook = get_object_or_404(Notebook, id=notebook_id)
        if notebook.owner != request.user:
            messages.error(request, '你没有权限访问该同学录')
            return redirect('dashboard')
        return view_func(request, notebook_id, *args, **kwargs)
    return wrapper
```

### 7.3 自定义邮箱认证后端

```python
# core/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailAuthBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
```

---

## 八、文件上传处理规范

### 8.1 上传流程

```
用户选择文件 → 前端预览（FileReader） → 表单提交（multipart/form-data）
  → Django 接收 request.FILES
  → 校验文件类型
  → FileField 保存到 MEDIA_ROOT
  → 创建 MediaFile 记录
  → hard_delete 时删除磁盘文件
```

### 8.2 文件类型校验

```python
ALLOWED_PHOTO_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
ALLOWED_VIDEO_TYPES = ['video/mp4', 'video/quicktime', 'video/x-msvideo']

def validate_file_type(uploaded_file, allowed_types):
    if uploaded_file.content_type not in allowed_types:
        raise ValidationError(f'不支持的文件类型: {uploaded_file.content_type}')
```

### 8.3 文件删除

```python
import os

def delete_media_files(media_files):
    """删除媒体文件记录及磁盘文件"""
    for media in media_files:
        if media.file and os.path.isfile(media.file.path):
            os.remove(media.file.path)
    media_files.delete()
```

---

## 九、定时清理任务

### 9.1 Django 管理命令

文件路径：`backend/core/management/commands/cleanup_trash.py`

```python
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Student
from core.utils import delete_media_files

class Command(BaseCommand):
    help = '清理回收站中超过10天的记录'

    def handle(self, *args, **options):
        expired = Student.objects.filter(
            is_deleted=True,
            restore_deadline__lt=timezone.now()
        )
        count = expired.count()
        for student in expired:
            delete_media_files(student.media_files.all())
        expired.delete()
        self.stdout.write(f'已清理 {count} 条过期回收站记录')
```

### 9.2 定时执行

**方法一：系统 cron（推荐）**
```bash
# 每天凌晨 3 点执行
0 3 * * * cd /path/to/backend && python manage.py cleanup_trash >> /var/log/cleanup_trash.log 2>&1
```

**方法二：启动脚本**
```bash
# cleanup_trash.sh
#!/bin/bash
cd /path/to/classmates-book/backend
python manage.py cleanup_trash
```

---

## 十、错误处理与边界情况

| 场景 | 处理方式 |
|------|----------|
| 无效的 share_code | 404 页面 |
| 无效的 edit_code | 404 页面或提示「编辑链接无效」 |
| 编辑码已过期 | 提示「编辑已过期，已超过3天」 |
| 必填字段缺失 | Django Form 校验失败，字段级错误提示 |
| 文件上传失败 | 捕获异常，记录日志，提示用户重试 |
| 邮箱发送失败 | 记录日志，提示「验证码发送失败，请稍后重试」 |
| 并发提交（同一编辑码） | 最后提交覆盖（乐观锁，不阻塞） |
| 网络断开 | 表单提交超时，显示连接错误 |

---

## 十一、安全注意事项

| 项目 | 说明 |
|------|------|
| CSRF 保护 | 所有 POST 表单包含 `{% csrf_token %}` |
| XSS 防护 | Django 模板默认自动转义 |
| SQL 注入 | 使用 ORM，不拼接 SQL |
| 密码存储 | Django PBKDF2 加密 |
| 文件上传 | 校验 `content_type`，不上传可执行文件 |
| 邮箱验证 | 验证码 5 分钟过期 + 60 秒防刷 |
| 编辑码安全 | 24 字符随机字符串，不可猜测 |
| 权限校验 | 每个视图检查 `notebook.owner == request.user` |

---

## 十二、Django 自定义 User 模型

```python
# core/models.py
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='邮箱')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return self.email
```

**注意：** 自定义 User 模型必须在第一次 `migrate` 之前设置 `AUTH_USER_MODEL`。

---

## 十三、实现顺序建议（细化）

| 步骤 | 内容 | 依赖 | 预估工时 |
|------|------|------|----------|
| 1 | 创建项目，配置 settings（数据库/邮件/媒体） | 无 | 1h |
| 2 | 实现 User 模型 + 邮箱认证后端 | 步骤1 | 0.5h |
| 3 | 实现 Notebook 模型 + 视图（CRUD） | 步骤2 | 1.5h |
| 4 | 实现 Student 模型 + 填写表单 + 提交逻辑 | 步骤3 | 2h |
| 5 | 实现 MediaFile 模型 + 文件上传处理 | 步骤4 | 1.5h |
| 6 | 实现邮箱验证码注册流程 | 步骤2 | 1h |
| 7 | 实现编辑功能（编辑码 + 3天有效期） | 步骤4 | 1h |
| 8 | 实现搜索功能（按名字 ILIKE） | 步骤4 | 0.5h |
| 9 | 实现回收站 + 软删除 + 定时清理 | 步骤4 | 1.5h |
| 10 | 实现同学详情页 + 媒体展示 | 步骤5 | 0.5h |
| 11 | Docker 部署配置 | 步骤1-10 | 0.5h |
| 12 | 前端样式打磨 + 响应式适配 | 全部 | 2h |

**总计预估：** 约 12 小时

---

## 十四、部署指南

### 14.1 Docker 部署

```bash
# 1. 克隆项目
git clone <repo-url> classmates-book
cd classmates-book

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填入数据库密码、邮箱授权码等

# 3. 构建并启动
docker compose up -d --build

# 4. 执行迁移
docker exec classmates-web python manage.py migrate

# 5. 收集静态文件
docker exec classmates-web python manage.py collectstatic --noinput
```

### 14.2 非 Docker 部署

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 确保 PostgreSQL 已启动，创建数据库
createdb classmates

# 3. 配置环境变量
export DB_HOST=localhost
export DB_PASSWORD=your_password
export EMAIL_HOST_PASSWORD=your_auth_code

# 4. 迁移
cd backend
python manage.py migrate

# 5. 启动
python main.py
# 或
python manage.py runserver 0.0.0.0:2323
```

---

## 十五、依赖清单与版本说明

```
# requirements.txt
django>=5.0,<6.1     # 当前安装 6.0.7
psycopg2-binary>=2.9  # PostgreSQL 适配器
python-dotenv>=1.0    # 环境变量管理
gunicorn>=22.0        # 生产 WSGI 服务器（Docker 用）
```

---

*文档版本：v2.0（完整优化版）*
*编写日期：2026-07-29*
