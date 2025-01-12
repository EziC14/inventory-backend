from django.urls import path
from . import views

urlpatterns = [
    path('category', views.GetPostCategory.as_view(), name='filter_employees'),
    path('primary-product', views.GetPostPrimaryProduct.as_view(), name='filter_employees'),
    path('final-product', views.GetPostFinalProduct.as_view(), name='filter_employees'),
] 
