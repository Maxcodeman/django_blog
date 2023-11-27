from django.contrib.auth import login
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django_redis import get_redis_connection

from libs.captcha.captcha import captcha
import re
from users.models import User
from django.db import DatabaseError

class RegisterView(View):
    """
            提供注册界面
            :param request: 请求对象
            :return: 注册界面
    """

    def get(self, request):
        return render(request, "register.html")
    def post(self, request):
        # 接收参数
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        smscode = request.POST.get('sms_code')

        # 判断参数是否齐全
        if not all([mobile, password, password2, smscode]):
            return HttpResponseBadRequest('缺少必传参数')
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest('请输入正确的手机号码')
        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return HttpResponseBadRequest('请输入8-20位的密码')
        # 判断两次密码是否一致
        if password != password2:
            return HttpResponseBadRequest('两次输入的密码不一致')

        # 验证短信验证码
        redis_conn = get_redis_connection('default')
        sms_code_server = redis_conn.get('sms:%s' % mobile)
        if sms_code_server is None:
            return HttpResponseBadRequest('短信验证码已过期')
        if smscode != sms_code_server.decode():
            return HttpResponseBadRequest('短信验证码错误')

        # 保存注册数据
        try:
            #create_user可以使用系统的方法对密码进行加密
            user = User.objects.create_user(username=mobile, mobile=mobile, password=password)
        except DatabaseError as e:
            logger.error(e)
            return HttpResponseBadRequest('注册失败')

        #实现状态保持
        login(request,user)

        # 响应注册结果
        # return HttpResponse('注册成功，重定向到首页')
        #reverse是可以通过namespace:name来获取到视图所对应的路由
        from django.urls import reverse
        response = redirect(reverse("home:index"))

        #设置cookie
        #登录状态,会话结束后自动过期
        response.set_cookie('is_login', True)
        #设置用户名有效期一个月
        response.set_cookie('username', user.username, max_age=30 * 24 * 3600)
        return response

class ImageCodeView(View):
    def get(self, request):
        # 获取前端传递过来的参数
        uuid = request.GET.get("uuid")
        # 判断参数是否为None
        if uuid is None:
            return HttpResponseBadRequest('请求参数错误')
        # 获取验证码内容和验证码图片二进制数据
        text, image = captcha.generate_captcha()
        # 将图片验证内容保存至redis中,设置过期时间
        redis_conn = get_redis_connection("default")
        redis_conn.setex("img:%s" % uuid, 300, text)
        # 返回响应,将生成的图片以content_type为image/jpeg的形式返回给请求
        return HttpResponse(image, content_type="image/jpeg")


from django.http import JsonResponse
from utils.response_code import RETCODE
from random import randint
from libs.yuntongxun.sms import CCP
import logging

logger = logging.getLogger('django')


class SmsCodeView(View):

    def get(self, request):
        # 接收参数
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')
        mobile = request.GET.get('mobile')

        # 校验参数
        if not all([image_code_client, uuid, mobile]):
            return JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '缺少必传参数'})

        # 创建连接到redis的对象
        redis_conn = get_redis_connection('default')
        # 提取图形验证码
        image_code_server = redis_conn.get('img:%s' % uuid)
        if image_code_server is None:
            # 图形验证码过期或者不存在
            return JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码失效'})
        # 删除图形验证码，避免恶意测试图形验证码
        try:
            redis_conn.delete('img:%s' % uuid)
        except Exception as e:
            logger.error(e)
        # 对比图形验证码
        image_code_server = image_code_server.decode()  # bytes转字符串
        if image_code_client.lower() != image_code_server.lower():  # 转小写后比较
            return JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '输入图形验证码有误'})

        # 生成短信验证码：生成4位数验证码
        sms_code = '%04d' % randint(0, 9999)
        # 将验证码输出在控制台，以方便调试
        logger.info(sms_code)
        # 保存短信验证码到redis中，并设置有效期
        redis_conn.setex('sms:%s' % mobile, 300, sms_code)
        # 发送短信验证码
        CCP().send_template_sms(mobile, [sms_code, 5], 1)

        # 响应结果
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '发送短信成功'})






