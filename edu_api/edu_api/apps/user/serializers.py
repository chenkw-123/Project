import re

from django.contrib.auth.hashers import make_password
from django_redis import get_redis_connection
from rest_framework import serializers

from user.models import UserInfo
from user.utils import get_user_by_account


class RegisterModelserializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=1000,read_only=True,help_text="用户token")
    msg_code = serializers.CharField(min_length=4,max_length=6,required=True,write_only=True,help_text="用户的验证码")
    class Meta:
        model = UserInfo
        fields = ('id', 'username', 'password', 'phone','token','msg_code')

        extra_kwargs = {
            "id": {
                "read_only": True
            },
            "username": {
                "read_only": True
            },
            "password": {
                "write_only": True
            },
            "phone": {
                "write_only": True
            }
        }


    #全局钩子验证手机号
    def validate(self, attrs):

        #计数器
        counts = 0

        phone = attrs.get("phone")
        password = attrs.get("password")
        msg_code = attrs.get("msg_code")
        print(msg_code,"1111")  #前端传入的msg_code
        #验证格式是否正确
        if not re.match(r'^1[35678]\d{9}$',phone):
            raise serializers.ValidationError("手机号格式错误！")
        #验证手机号是否被注册
        try:
            user = get_user_by_account(phone)
        except:
            user = None

        if user:
            raise serializers.ValidationError("手机号已被注册")

        #验证手机号短信验证码是否正确
        redis_connection = get_redis_connection("msg_code")
        phone_code = redis_connection.get("mobile_%s" % phone)
        print(phone_code)
        if phone_code.decode() != msg_code:
            #TODO 设置一个手机号只能验证N次
            counts+=1
            raise serializers.ValidationError("验证码不一致")

        #防止验证多次
        if counts>=5:
            raise serializers.ValidationError("验证码输入次数超出范围，请重新获取验证码")
        #之后将验证码删除

        return attrs

    #为用户设置默认的用户名
    def create(self, validated_data):

        password = validated_data.get("password")
        hash_password = make_password(password)
        #设置用户名默认值为手机号
        username = validated_data.get("phone")

        #添加数据
        user = UserInfo.objects.create(
            phone=username,
            username=username,
            password=hash_password
        )

        #生成token
        from rest_framework_jwt.settings import api_settings
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handle = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        # token = jwt_encode_handle(payload)
        user.token = jwt_encode_handle(payload)
        # print(user)
        return user