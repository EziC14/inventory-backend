from django.urls import path
from . import views

urlpatterns = [
    path('reason-types', views.ReasonTypeView.as_view(), name='reason-type-list'),
    path('reason-types/<uuid:id>', views.ReasonTypeDetailView.as_view(), name='reason-type-detail'),
    path('<uuid:id>', views.InventoryMovementDetailView.as_view(), name='movement-detail'),
    path('', views.InventoryMovementListCreateView.as_view(), name='movement-list'),
    path('analyze-document', views.DocumentAnalyzerAPIView.as_view(), name='analyze-document'),
    
    # La vista para ReasonType ya la tienes implementada
]