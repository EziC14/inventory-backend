from django.urls import path
from rest_framework_simplejwt.views import (
    # TokenObtainPairView,
    TokenRefreshView,
    # TokenVerifyView
)

from . import views

urlpatterns = [
    path('login', views.UserLoginView.as_view(), name='login'),
    path('token/verify/', views.VerifyView.as_view(), name='token_verify'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register', views.UserRegisterView.as_view(), name='register'),
    path('code/verify', views.VerifyCodeView.as_view(), name='verify'),
    path('code/resend', views.ResendVerificationCodeView.as_view(), name='resend'),
    path('token/email', views.GenerateVerificationTokenView.as_view(), name='generate_token_email'),
    path('password/code', views.PasswordResetRequestView.as_view(), name='generate_code_password'),
    path('password/resend', views.PasswordChangeCodeResendView.as_view(), name='resend_code_password'),
    path('password/verify', views.PasswordResetView.as_view(), name='reset_password'),
    path('password/change', views.PasswordChangeView.as_view(), name='change_password'),

    # path('envs', views.EnvsView.as_view(), name='envs'),
] 
