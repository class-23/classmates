"""Core 子路由"""
from django.urls import path
from . import views

urlpatterns = [
    # 公开页面
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # API
    path('api/send-verification-code/', views.send_verification_code, name='send_code'),

    # 同学录 CRUD
    path('dashboard/', views.dashboard, name='dashboard'),
    path('notebook/create/', views.notebook_create, name='notebook_create'),
    path('notebook/<int:notebook_id>/delete/', views.notebook_delete, name='notebook_delete'),
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
