"""全局异常处理中间件"""
import json
import logging
import traceback
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.db.utils import OperationalError, ProgrammingError

logger = logging.getLogger(__name__)


class GlobalExceptionMiddleware:
    """全局异常处理中间件
    
    捕获所有未处理的异常，返回友好的错误页面
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            return self._handle_exception(request, e)
    
    def process_exception(self, request, exception):
        """Django 异常处理钩子"""
        return self._handle_exception(request, exception)
    
    def _handle_exception(self, request, exception):
        """处理异常并返回响应"""
        # 记录异常日志
        logger.error(
            f"异常捕获: {type(exception).__name__}: {str(exception)}\n"
            f"路径: {request.path}\n"
            f"方法: {request.method}\n"
            f"追踪:\n{traceback.format_exc()}"
        )
        
        # 数据库连接错误 - 返回特殊提示
        if isinstance(exception, (OperationalError, ProgrammingError)):
            return self._handle_database_error(request, exception)
        
        # 检查是否是 AJAX 请求
        if self._is_ajax(request):
            return self._handle_ajax_error(exception)
        
        # 根据异常类型返回对应的错误页面
        status_code = self._get_status_code(exception)
        
        try:
            error_html = self._render_error_page(status_code, exception, request)
            return HttpResponse(error_html, status=status_code)
        except Exception:
            # 如果渲染错误页面也失败了，返回简单的 JSON 错误
            logger.critical(f"错误页面渲染失败: {traceback.format_exc()}")
            return HttpResponse("服务器内部错误，请稍后重试", status=500)
    
    def _handle_database_error(self, request, exception):
        """处理数据库相关错误"""
        error_msg = str(exception)
        
        # 判断错误类型
        if 'does not exist' in error_msg.lower() or 'relation' in error_msg.lower():
            # 数据库表不存在 - 可能是迁移未执行
            user_message = '数据库表不存在，请先执行数据库迁移命令'
            detail_message = '运行命令: python3 manage.py migrate'
        elif 'connection refused' in error_msg.lower() or 'could not connect' in error_msg.lower():
            # 数据库连接失败
            user_message = '无法连接到数据库服务'
            detail_message = '请检查数据库服务是否已启动'
        elif 'authentication failed' in error_msg.lower() or 'password' in error_msg.lower():
            # 数据库认证失败
            user_message = '数据库认证失败'
            detail_message = '请检查数据库用户名和密码配置'
        else:
            # 其他数据库错误
            user_message = '数据库操作出错'
            detail_message = '请稍后重试或联系管理员'
        
        # AJAX 请求返回 JSON
        if self._is_ajax(request):
            return HttpResponse(
                json.dumps({'code': 500, 'message': user_message, 'detail': detail_message}, ensure_ascii=False),
                content_type='application/json',
                status=500
            )
        
        # 普通请求返回 HTML 错误页面
        error_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>数据库错误 - 同窗录</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .error-container {{
            background: white;
            border-radius: 24px;
            padding: 50px 40px;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            max-width: 450px;
            width: 90%;
        }}
        .error-icon {{
            width: 90px;
            height: 90px;
            border-radius: 50%;
            background: linear-gradient(135deg, #ff9a9e, #fad0c4);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
        }}
        .error-code {{
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(135deg, #ff9a9e, #fad0c4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        .error-title {{ font-size: 1.3rem; margin-bottom: 12px; color: #333; }}
        .error-message {{ color: #666; margin-bottom: 20px; line-height: 1.6; }}
        .error-detail {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            text-align: left;
        }}
        .error-detail p {{ font-size: 0.9rem; color: #856404; margin-bottom: 5px; }}
        .error-detail code {{
            display: block;
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 10px 15px;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
            margin-top: 8px;
        }}
        .btn {{
            padding: 10px 24px;
            border-radius: 10px;
            border: none;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.3s;
        }}
        .btn-primary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        .btn-primary:hover {{ transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102,126,234,0.4); }}
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-icon">
            <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <ellipse cx="12" cy="5" rx="9" ry="3"></ellipse>
                <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path>
                <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path>
            </svg>
        </div>
        <div class="error-code">500</div>
        <h1 class="error-title">数据库错误</h1>
        <p class="error-message">{user_message}</p>
        <div class="error-detail">
            <p>💡 解决方法：</p>
            <code>{detail_message}</code>
        </div>
        <button onclick="location.reload()" class="btn btn-primary">刷新重试</button>
    </div>
</body>
</html>'''
        return HttpResponse(error_html, status=500)
    
    def _is_ajax(self, request):
        """判断是否为 AJAX 请求"""
        return (
            request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
            request.headers.get('Accept', '').find('application/json') != -1
        )
    
    def _handle_ajax_error(self, exception):
        """处理 AJAX 请求的错误响应"""
        status_code = self._get_status_code(exception)
        error_message = self._get_user_friendly_message(exception)
        
        response_data = {
            'code': status_code,
            'message': error_message,
            'detail': str(exception) if settings.DEBUG else None
        }
        
        response = HttpResponse(
            json.dumps(response_data, ensure_ascii=False),
            content_type='application/json',
            status=status_code
        )
        return response
    
    def _get_status_code(self, exception):
        """根据异常类型获取状态码"""
        if isinstance(exception, Http404):
            return 404
        elif isinstance(exception, PermissionDenied):
            return 403
        elif isinstance(exception, (FileNotFoundError,)):
            return 404
        elif isinstance(exception, (ConnectionError, TimeoutError)):
            return 503
        else:
            return 500
    
    def _get_user_friendly_message(self, exception):
        """获取用户友好的错误消息"""
        status_code = self._get_status_code(exception)
        
        messages = {
            403: '抱歉，您没有权限访问此页面',
            404: '抱歉，您访问的页面不存在',
            500: '抱歉，服务器出现了一些问题，请稍后重试',
            503: '抱歉，服务暂时不可用，请稍后重试',
        }
        
        return messages.get(status_code, '发生了未知错误，请稍后重试')
    
    def _render_error_page(self, status_code, exception, request):
        """渲染错误页面"""
        error_data = {
            'status_code': status_code,
            'error_message': self._get_user_friendly_message(exception),
            'request_path': request.path,
        }
        
        try:
            return render_to_string(f'core/error_{status_code}.html', error_data)
        except Exception:
            # 如果特定错误页面不存在，尝试渲染 500 页面
            try:
                return render_to_string('core/error_500.html', error_data)
            except Exception:
                # 返回简单的错误 HTML
                return self._get_default_error_html(status_code, error_data)
    
    def _get_default_error_html(self, status_code, error_data):
        """获取默认错误页面 HTML"""
        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>错误 {status_code} - 同窗录</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #333;
        }}
        .error-container {{
            background: white;
            border-radius: 20px;
            padding: 60px 40px;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
            max-width: 400px;
        }}
        .error-code {{
            font-size: 6rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
        }}
        .error-title {{
            font-size: 1.5rem;
            margin-bottom: 15px;
            color: #333;
        }}
        .error-message {{
            color: #666;
            margin-bottom: 30px;
            line-height: 1.6;
        }}
        .error-actions {{
            display: flex;
            gap: 15px;
            justify-content: center;
        }}
        .btn {{
            padding: 12px 30px;
            border-radius: 10px;
            border: none;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.3s;
        }}
        .btn-primary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        .btn-secondary {{
            background: #f5f5f5;
            color: #666;
        }}
        .btn:hover {{ transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-code">{status_code}</div>
        <h1 class="error-title">出错了</h1>
        <p class="error-message">{error_data['error_message']}</p>
        <div class="error-actions">
            <a href="/" class="btn btn-primary">返回首页</a>
            <a href="javascript:history.back()" class="btn btn-secondary">返回上一页</a>
        </div>
    </div>
</body>
</html>'''