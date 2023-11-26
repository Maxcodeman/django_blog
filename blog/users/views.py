from django.shortcuts import render
from django.views import View

class RegisterView(View):
    """
            提供注册界面
            :param request: 请求对象
            :return: 注册界面
    """
    def get(self,request):
        return render(request,"register.html")
# Create your views here.
