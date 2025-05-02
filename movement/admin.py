from django.contrib import admin
from .models import InventoryMovement, InventoryMovementDetail

# Register your models here.

@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    list_display = ('id', 'direction', 'supplier')
    search_fields = ('supplier__name',)
    list_filter = ('direction', 'supplier',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

@admin.register(InventoryMovementDetail)
class InventoryMovementDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'movement', 'primary_product', 'final_product', 'product_color', 'quantity', 'unit_price', 'total_price')
    search_fields = ('movement__id', 'primary_product__name', 'final_product__name', 'product_color__name')
    list_filter = ('movement__direction',)
    ordering = ('-movement__created_at',)
