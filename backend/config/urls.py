"""Config 根路由"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import Http404
from django.shortcuts import render


def custom_404_view(request, exception):
    """自定义 404 页面"""
    return render(request, 'core/error_404.html', status=404)


def custom_500_view(request):
    """自定义 500 页面"""
    return render(request, 'core/error_500.html', status=500)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

# 自定义错误页面处理器（仅在生产环境 DEBUG=False 时生效）
handler404 = custom_404_view
handler500 = custom_500_view

# 媒体文件支持（开发和生产环境均通过 Django 处理，生产环境建议配合 Nginx）
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
