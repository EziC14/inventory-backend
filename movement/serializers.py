from rest_framework import serializers
from .models import InventoryMovement, InventoryMovementDetail

class InventoryMovementDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryMovementDetail
        fields = ['id', 'primary_product', 'final_product', 'product_color', 'quantity', 'unit_price', 'total_price']

class InventoryMovementSerializer(serializers.ModelSerializer):
    details = InventoryMovementDetailSerializer(many=True, read_only=True)
    
    class Meta:
        model = InventoryMovement
        fields = ['id', 'date', 'direction', 'reason_type', 'supplier', 'notes', 'details']