from django.urls import path
from .views import MovementReportView, InventoryReportView, SupplierReportView

urlpatterns = [
    path('reports/movements/', MovementReportView.as_view(), name='movement-reports'),
    path('reports/inventory/', InventoryReportView.as_view(), name='inventory-reports'),
    path('reports/suppliers/', SupplierReportView.as_view(), name='supplier-reports'),
]
