import random
import re

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status as http_status, status
from rest_framework.generics import CreateAPIView

from edu_api.libs.geetest import GeetestLib
from edu_api.settings import constants
from user.models import UserInfo
from user.serializers import RegisterModelserializer
from user.utils import get_user_by_account

from rest_framework.generics import CreateAPIView

from django_redis import get_redis_connection

from utils.send_msg import Message

pc_geetest_id = "6f91b3d2afe94ed29da03c14988fb4ef"
pc_geetest_key = "7a01b1933685931ef5eaf5dabefd3df2"


class CaptchaAPIView(APIView):
    """极验验证码"""

    user_id = 0
    status = False

    def get(self, request, *args, **kwargs):
        """获取验证码"""

        username = request.query_params.get('username')
        user = get_user_by_account(username)
        if user is None:
            return Response({"message": "用户不存在"}, status=http_status.HTTP_400_BAD_REQUEST)

        self.user_id = user.id

        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        self.status = gt.pre_process(self.user_id)
        response_str = gt.get_response_str()
        return Response(response_str)

    def post(self, request, *args, **kwargs):
        """验证验证码"""
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        # 判断用户是否存在
        if self.user_id:
            result = gt.success_validate(challenge, validate, seccode, self.user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        result = {"status": "success"} if result else {"status": "fail"}
        return Response(result)


class RegisterAPIView(CreateAPIView):
    # 用户注册视图
    queryset = UserInfo.objects.all()
    serializer_class = RegisterModelserializer


# 判断手机号是否唯一
class PhoneCheckAPIView(APIView):

    def get(self, request, mobile):

        if not re.match(r'^1[35678]\d{9}', mobile):
            return Response({"message": "手机号格式不对"}, status=http_status.HTTP_400_BAD_REQUEST)

        user = get_user_by_account(mobile)

        if user is not None:
            return Response({"message": "手机号已被注册！"}, status=http_status.HTTP_400_BAD_REQUEST)

        return Response({"message": "合法"})


class SendMessageAPIView(APIView):

    def get(self, request, mobile):
        redis_connection = get_redis_connection("msg_code")

        #判断手机验证码是否在60s内发送短信
        mobile_code = redis_connection.get("msg_%s" % mobile)
        if mobile_code is not None:
            return Response({"message":"60s后才能发送短信"}, status=http_status.HTTP_400_BAD_REQUEST)
        #生成随机短信验证码
        code = "%06d" % random.randint(0,999999)

        #将验证码保存带redis中
        redis_connection.setex("msg_%s" % mobile, constants.SMS_EXPIRE_TIME ,code) # 60s内不允许再次发送
        redis_connection.setex("mobile_%s" % mobile, constants.MOBILE_EXPIRE_TIME, code)  # 验证码的有效时间
        #调用方法 完成短信的发送
        try:
            message = Message(constants.API_KEY)
            message.send_message(mobile,code)
        except:
            return Response({"message":"短信发送失败"},status=http_status.HTTP_400_BAD_REQUEST)

        #响应回来
        return Response({"message":"短信发送成功！"},status=http_status.HTTP_200_OK)