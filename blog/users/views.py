from django.http import HttpResponseBadRequest,HttpResponse
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection

from libs.captcha.captcha import captcha


class RegisterView(View):
    """
            提供注册界面
            :param request: 请求对象
            :return: 注册界面
    """
    def get(self,request):
        return render(request,"register.html")

class ImageCodeView(View):
    def get(self,request):
        #获取前端传递过来的参数
        uuid=request.GET.get("uuid")
        #判断参数是否为None
        if uuid is None:
            return HttpResponseBadRequest('请求参数错误')
        #获取验证码内容和验证码图片二进制数据
        text,image=captcha.generate_captcha()
        #将图片验证内容保存至redis中,设置过期时间
        redis_conn=get_redis_connection("default")
        redis_conn.setex("img:%s" %uuid,300,text)
        #返回响应,将生成的图片以content_type为image/jpeg的形式返回给请求
        return HttpResponse(image,content_type="image/jpeg")

