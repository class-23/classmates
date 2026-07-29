"""同学录 - 全部视图函数"""
import json
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q, Count
from django.conf import settings

from .models import User, Notebook, Student, MediaFile, VerificationCode
from .utils import generate_verification_code, send_verification_email, delete_media_files


# ===== 公开页面 =====

def home(request):
    """首页"""
    return render(request, 'core/home.html')


def register(request):
    """注册"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        code = request.POST.get('verification_code', '').strip()
        password = request.POST.get('password', '')
        confirm = request.POST.get('confirm_password', '')

        errors = []
        if not email or '@' not in email:
            errors.append('请输入有效的邮箱地址')
        if User.objects.filter(email=email).exists():
            errors.append('该邮箱已被注册')
        if not code or len(code) != 6 or not code.isdigit():
            errors.append('验证码为6位数字')
        if len(password) < 8:
            errors.append('密码至少8位')
        if password != confirm:
            errors.append('两次密码不一致')

        # 校验验证码
        if not errors:
            vc = VerificationCode.objects.filter(
                email=email, code=code,
                is_used=False, expires_at__gt=timezone.now()
            ).last()
            if not vc:
                errors.append('验证码无效或已过期')

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'core/register.html')

        # 创建用户
        vc.is_used = True
        vc.save()
        user = User.objects.create_user(
            username=email, email=email, password=password
        )
        messages.success(request, '注册成功，请登录')
        return redirect('login')

    return render(request, 'core/register.html')


def user_login(request):
    """登录"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, '邮箱或密码错误')

    return render(request, 'core/login.html')


def user_logout(request):
    """退出"""
    logout(request)
    return redirect('login')


# ===== API =====

def send_verification_code(request):
    """发送邮箱验证码（AJAX）"""
    if request.method != 'POST':
        return JsonResponse({'code': 400, 'message': '仅支持POST请求'})

    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'code': 400, 'message': '请求格式错误'})

    if not email or '@' not in email:
        return JsonResponse({'code': 400, 'message': '邮箱格式不正确'})

    if User.objects.filter(email=email).exists():
        return JsonResponse({'code': 400, 'message': '该邮箱已被注册'})

    # 60秒防刷
    last = VerificationCode.objects.filter(email=email).order_by('-created_at').first()
    if last and (timezone.now() - last.created_at).total_seconds() < 60:
        return JsonResponse({'code': 400, 'message': '请60秒后再试'})

    code = generate_verification_code()
    VerificationCode.objects.create(
        email=email, code=code,
        expires_at=timezone.now() + timedelta(minutes=5)
    )

    try:
        send_verification_email(email, code)
    except Exception as e:
        return JsonResponse({'code': 500, 'message': f'邮件发送失败: {str(e)}'})

    return JsonResponse({'code': 200, 'message': '验证码已发送'})


# ===== 同学录 CRUD =====

@login_required
def dashboard(request):
    """仪表盘 - 我的同学录列表"""
    notebooks = Notebook.objects.filter(owner=request.user).annotate(
        student_count=Count('students', filter=Q(students__is_deleted=False))
    ).order_by('-created_at')
    return render(request, 'core/dashboard.html', {'notebooks': notebooks})


@login_required
def notebook_delete(request, notebook_id):
    """删除整本同学录（级联删除所有数据 + 清理磁盘文件）"""
    if request.method != 'POST':
        return redirect('dashboard')

    notebook = get_object_or_404(Notebook, id=notebook_id)
    if notebook.owner != request.user:
        messages.error(request, '你没有权限删除该同学录')
        return redirect('dashboard')

    title = notebook.title

    # 先删除所有同学的媒体文件（物理磁盘清理）
    for student in notebook.students.all():
        delete_media_files(student.media_files.all())

    # 级联删除同学录、所有同学信息、媒体文件记录
    notebook.delete()
    messages.success(request, f'已永久删除「{title}」及其所有同学信息')
    return redirect('dashboard')


@login_required
def notebook_create(request):
    """创建同学录"""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        if not title:
            messages.error(request, '请输入同学录名称')
            return render(request, 'core/notebook_create.html')
        notebook = Notebook.objects.create(owner=request.user, title=title)
        messages.success(request, f'「{title}」创建成功！')
        return redirect('notebook_detail', notebook_id=notebook.id)
    return render(request, 'core/notebook_create.html')


def _check_owner(request, notebook):
    """检查当前用户是否为同学录创建者"""
    if notebook.owner != request.user:
        messages.error(request, '你没有权限访问该同学录')
        return False
    return True


@login_required
def notebook_detail(request, notebook_id):
    """同学录详情 - 学生列表 + 搜索"""
    notebook = get_object_or_404(Notebook, id=notebook_id)
    if not _check_owner(request, notebook):
        return redirect('dashboard')

    q = request.GET.get('q', '').strip()
    students = Student.objects.filter(notebook=notebook, is_deleted=False)
    if q:
        students = students.filter(name__icontains=q)
    students = students.order_by('name')

    return render(request, 'core/notebook_detail.html', {
        'notebook': notebook,
        'students': students,
    })


@login_required
def notebook_search(request, notebook_id):
    """搜索（AJAX）"""
    notebook = get_object_or_404(Notebook, id=notebook_id)
    if not _check_owner(request, notebook):
        return JsonResponse({'code': 403, 'message': '无权限'})

    q = request.GET.get('q', '').strip()
    students = Student.objects.filter(notebook=notebook, is_deleted=False)
    if q:
        students = students.filter(name__icontains=q)
    students = students.order_by('name')

    data = [{'id': s.id, 'name': s.name, 'nickname': s.nickname,
             'phone': s.phone, 'wechat': s.wechat} for s in students]
    return JsonResponse({'code': 200, 'data': data})


@login_required
def notebook_trash(request, notebook_id):
    """回收站"""
    notebook = get_object_or_404(Notebook, id=notebook_id)
    if not _check_owner(request, notebook):
        return redirect('dashboard')

    trash_items = Student.objects.filter(
        notebook=notebook, is_deleted=True
    ).order_by('-deleted_at')

    return render(request, 'core/notebook_trash.html', {
        'notebook': notebook,
        'trash_items': trash_items,
    })


@login_required
def delete_student(request, notebook_id, student_id):
    """软删除同学信息"""
    if request.method != 'POST':
        return redirect('notebook_detail', notebook_id=notebook_id)

    notebook = get_object_or_404(Notebook, id=notebook_id)
    if not _check_owner(request, notebook):
        return redirect('dashboard')

    student = get_object_or_404(Student, id=student_id, notebook=notebook)
    student.soft_delete()
    messages.success(request, f'已删除「{student.name}」的信息，可在回收站找回')

    referer = request.META.get('HTTP_REFERER', '')
    if 'trash' in referer:
        return redirect('notebook_trash', notebook_id=notebook_id)
    return redirect('notebook_detail', notebook_id=notebook_id)


@login_required
def restore_student(request, notebook_id, student_id):
    """从回收站还原"""
    if request.method != 'POST':
        return redirect('notebook_trash', notebook_id=notebook_id)

    notebook = get_object_or_404(Notebook, id=notebook_id)
    if not _check_owner(request, notebook):
        return redirect('dashboard')

    student = get_object_or_404(Student, id=student_id, notebook=notebook, is_deleted=True)
    student.restore()
    messages.success(request, f'已还原「{student.name}」的信息')
    return redirect('notebook_trash', notebook_id=notebook_id)


@login_required
def hard_delete_student(request, notebook_id, student_id):
    """永久删除（含文件）"""
    if request.method != 'POST':
        return redirect('notebook_trash', notebook_id=notebook_id)

    notebook = get_object_or_404(Notebook, id=notebook_id)
    if not _check_owner(request, notebook):
        return redirect('dashboard')

    student = get_object_or_404(Student, id=student_id, notebook=notebook, is_deleted=True)
    name = student.name
    delete_media_files(student.media_files.all())
    student.delete()
    messages.success(request, f'已永久删除「{name}」的信息')
    return redirect('notebook_trash', notebook_id=notebook_id)


@login_required
def empty_trash(request, notebook_id):
    """清空回收站"""
    if request.method != 'POST':
        return redirect('notebook_trash', notebook_id=notebook_id)

    notebook = get_object_or_404(Notebook, id=notebook_id)
    if not _check_owner(request, notebook):
        return redirect('dashboard')

    trash = Student.objects.filter(notebook=notebook, is_deleted=True)
    count = trash.count()
    for s in trash:
        delete_media_files(s.media_files.all())
    trash.delete()
    messages.success(request, f'已清空回收站，共清理 {count} 条记录')
    return redirect('notebook_trash', notebook_id=notebook_id)


# ===== 分享与填写 =====

def fill_form(request, share_code):
    """填写表单"""
    notebook = get_object_or_404(Notebook, share_code=share_code)

    if request.method == 'POST':
        # 创建学生记录
        student = Student(notebook=notebook)
        _fill_student_from_post(student, request)
        student.generate_edit_code()
        student.save()

        # 处理上传文件
        _handle_uploaded_files(student, request)

        from django.urls import reverse
        url = reverse('fill_success', kwargs={'share_code': share_code})
        return redirect(f'{url}?code={student.edit_code}')

    zodiac_choices = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']
    constellation_choices = [
        '白羊座', '金牛座', '双子座', '巨蟹座', '狮子座', '处女座',
        '天秤座', '天蝎座', '射手座', '摩羯座', '水瓶座', '双鱼座'
    ]
    return render(request, 'core/fill_form.html', {
        'notebook': notebook,
        'edit_mode': False,
        'zodiac_choices': zodiac_choices,
        'constellation_choices': constellation_choices,
    })


def fill_success(request, share_code):
    """提交成功页"""
    notebook = get_object_or_404(Notebook, share_code=share_code)
    edit_code = request.GET.get('code', '')
    return render(request, 'core/fill_success.html', {
        'notebook': notebook,
        'edit_code': edit_code,
    })


def edit_form(request, edit_code):
    """编辑表单（凭编辑码）"""
    student = get_object_or_404(Student, edit_code=edit_code, is_deleted=False)

    if not student.can_edit():
        messages.error(request, '编辑已过期（提交后超过3天）')
        return redirect('home')

    notebook = student.notebook
    zodiac_choices = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']
    constellation_choices = [
        '白羊座', '金牛座', '双子座', '巨蟹座', '狮子座', '处女座',
        '天秤座', '天蝎座', '射手座', '摩羯座', '水瓶座', '双鱼座'
    ]

    if request.method == 'POST':
        _fill_student_from_post(student, request)
        student.save()

        # 删除旧文件
        delete_ids = request.POST.getlist('delete_photos') + request.POST.getlist('delete_videos')
        if delete_ids:
            to_delete = MediaFile.objects.filter(id__in=delete_ids, student=student)
            delete_media_files(to_delete)

        # 处理新上传
        _handle_uploaded_files(student, request)

        messages.success(request, '修改已保存！')
        return redirect('edit_form', edit_code=edit_code)

    existing_photos = MediaFile.objects.filter(student=student, file_type='photo')
    existing_videos = MediaFile.objects.filter(student=student, file_type='video')

    return render(request, 'core/fill_form.html', {
        'notebook': notebook,
        'student': student,
        'edit_mode': True,
        'deadline': student.edit_deadline.strftime('%Y-%m-%d %H:%M'),
        'existing_photos': existing_photos,
        'existing_videos': existing_videos,
        'zodiac_choices': zodiac_choices,
        'constellation_choices': constellation_choices,
    })


# ===== 同学详情 =====

@login_required
def student_detail(request, student_id):
    """查看单个同学详情"""
    student = get_object_or_404(Student, id=student_id, is_deleted=False)
    notebook = student.notebook
    if not _check_owner(request, notebook):
        return redirect('dashboard')

    media_files = MediaFile.objects.filter(student=student).order_by('file_type')
    return render(request, 'core/student_detail.html', {
        'notebook': notebook,
        'student': student,
        'media_files': media_files,
    })


# ===== 辅助函数 =====

def _fill_student_from_post(student, request):
    """从 POST 数据填充 Student 字段"""
    post = request.POST
    student.name = post.get('name', '').strip()
    student.nickname = post.get('nickname', '').strip()
    student.phone = post.get('phone', '').strip()
    student.wechat = post.get('wechat', '').strip()
    student.first_impression = post.get('first_impression', '').strip()
    student.words_to_me = post.get('words_to_me', '').strip()
    student.message = post.get('message', '').strip()

    # 选填字段
    birthday = post.get('birthday', '').strip()
    student.birthday = birthday if birthday else None
    student.zodiac_sign = post.get('zodiac_sign', '').strip() or None
    student.constellation = post.get('constellation', '').strip() or None
    student.qq = post.get('qq', '').strip() or None
    student.xiaohongshu = post.get('xiaohongshu', '').strip() or None
    student.douyin = post.get('douyin', '').strip() or None
    student.email = post.get('email', '').strip() or None
    student.address = post.get('address', '').strip() or None
    student.hobbies = post.get('hobbies', '').strip() or None
    student.motto = post.get('motto', '').strip() or None
    student.crush = post.get('crush', '').strip() or None
    student.dislike = post.get('dislike', '').strip() or None
    student.wish = post.get('wish', '').strip() or None
    student.dream = post.get('dream', '').strip() or None
    student.favorite_food = post.get('favorite_food', '').strip() or None
    student.most_want_to_see = post.get('most_want_to_see', '').strip() or None
    student.favorite_movie = post.get('favorite_movie', '').strip() or None
    student.favorite_music = post.get('favorite_music', '').strip() or None
    student.most_want_to_go = post.get('most_want_to_go', '').strip() or None
    student.most_unforgettable = post.get('most_unforgettable', '').strip() or None
    student.hope_10_years = post.get('hope_10_years', '').strip() or None


def _handle_uploaded_files(student, request):
    """处理上传的照片和视频"""
    for f in request.FILES.getlist('photos'):
        MediaFile.objects.create(
            student=student, file=f, file_type='photo',
            file_size=f.size
        )
    for f in request.FILES.getlist('videos'):
        MediaFile.objects.create(
            student=student, file=f, file_type='video',
            file_size=f.size
        )
