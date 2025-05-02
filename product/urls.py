from django.urls import path
from . import views

urlpatterns = [
    path('final-product', views.GetPostFinalProduct.as_view(), name='final_product'),
    path('product-color/<str:primary_product_id>', views.ProductColorListView.as_view(), name='product_color'),
    path('primary-product', views.GetPostPrimaryProduct.as_view(), name='primary_product'),
    path('category', views.GetPostCategory.as_view(), name='post_category'),
    path('category/<str:category_id>', views.GetPutDeleteCategory.as_view(), name='get_category'),
    path('<str:product_id>', views.GetProductDetail.as_view(), name='product_detail'),
    path('', views.GetProduct.as_view(), name='product_list'),
]