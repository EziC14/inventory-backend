from django.contrib import admin
from .models import InventoryMovement, InventoryMovementDetail, ReasonType

# Register your models here.

@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'direction', 'reason_type', 'supplier')
    search_fields = ('reason_type__name', 'supplier__name')
    list_filter = ('direction', 'reason_type', 'supplier')
    date_hierarchy = 'date'
    ordering = ('-date',)


@admin.register(InventoryMovementDetail)
class InventoryMovementDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'movement', 'primary_product', 'final_product', 'product_color', 'quantity', 'unit_price', 'total_price')
    search_fields = ('movement__id', 'primary_product__name', 'final_product__name', 'product_color__name')
    list_filter = ('movement__direction', 'movement__reason_type')
    ordering = ('-movement__date',)


@admin.register(ReasonType)
class ReasonTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_input')
    search_fields = ('name',)
    list_filter = ('is_input',)
    ordering = ('name',)