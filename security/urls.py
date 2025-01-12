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
    # path('envs', views.EnvsView.as_view(), name='envs'),
] 
