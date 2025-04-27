from django.urls import path
from . import views

urlpatterns = [
    path('final-product', views.GetPostFinalProduct.as_view(), name='final_product'),
    path('primary-product', views.GetPostPrimaryProduct.as_view(), name='primary_product'),
    path('category', views.GetPostCategory.as_view(), name='post_category'),
    path('<str:product_id>', views.GetProductDetail.as_view(), name='product_detail'),
    path('', views.GetProduct.as_view(), name='product_list'),
]