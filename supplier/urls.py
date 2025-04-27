from django.urls import path
from . import views

urlpatterns = [
    path('', views.SupplierView.as_view(), name='supplier_list'),
    path('<str:supplier_id>', views.SupplierDetailView.as_view(), name='supplier_update'),
]