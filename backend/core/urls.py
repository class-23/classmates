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
    path('notebook/<str:notebook_slug>/delete/', views.notebook_delete, name='notebook_delete'),
    path('notebook/<str:notebook_slug>/', views.notebook_detail, name='notebook_detail'),
    path('notebook/<str:notebook_slug>/search/', views.notebook_search, name='notebook_search'),
    path('notebook/<str:notebook_slug>/delete-student/<str:student_slug>/', views.delete_student, name='delete_student'),
    path('notebook/<str:notebook_slug>/restore/<str:student_slug>/', views.restore_student, name='restore_student'),
    path('notebook/<str:notebook_slug>/hard-delete/<str:student_slug>/', views.hard_delete_student, name='hard_delete_student'),
    path('notebook/<str:notebook_slug>/trash/', views.notebook_trash, name='notebook_trash'),
    path('notebook/<str:notebook_slug>/empty-trash/', views.empty_trash, name='empty_trash'),
    path('notebook/<str:notebook_slug>/<str:student_slug>/', views.student_detail, name='student_detail'),

    # 分享与填写
    path('join/<uuid:share_code>/', views.fill_form, name='fill_form'),
    path('join/<uuid:share_code>/success/', views.fill_success, name='fill_success'),

    # 编辑
    path('edit/<str:edit_code>/', views.edit_form, name='edit_form'),
]
