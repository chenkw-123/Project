from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token

from user import views

urlpatterns = [
    path("login/", obtain_jwt_token),
    path("captcha/", views.CaptchaAPIView.as_view()),
    path("register/", views.RegisterAPIView.as_view()),
    path("check_phone/<str:mobile>", views.PhoneCheckAPIView.as_view()),
    path("msg/<str:mobile>", views.SendMessageAPIView.as_view()),
]
