"""
URL configuration for blog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path,include
#导入系统的logging
import logging
#创建(获取)日志器
logger = logging.getLogger('django')


def log(request):
    # logger.info('测试logging模块info')
    # logger.debug('测试logging模块debug')
    # logger.error('测试logging模块error')
    return HttpResponse('test')

urlpatterns = [
    path("admin/", admin.site.urls),
    # path('',log),
    #include 参数1要设置为元组(urlconf_module,app_name)
    #namespace 设置命名空间
    path('',include(('users.urls','users'),namespace='users')),
    path('',include(('home.urls','home'),namespace='home')),
]
#以下代码为设置图片访问路由规则
from django.conf import settings
from django.conf.urls.static import static
urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)