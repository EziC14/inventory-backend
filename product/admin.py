from django.contrib import admin
from product.models import *
from security.admin import default_list_display
from security.admin import default_list_editable
from security.admin import default_list_filter
from security.admin import default_search_fields
from security.admin import default_readonly_fields
from security.admin import default_fields

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name') + default_list_display
    list_filter = ('name', ) + default_list_filter
    search_fields = ('name',)
    readonly_fields = ('id',) + default_readonly_fields
    fieldsets = (
        ('Información Básica', {
            'fields': ('name',),
        }),
        default_fields
    )

@admin.register(PrimaryProduct)
class PrimaryProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'has_colors','category', 'unit_cost') + default_list_display
    list_filter = ('category',) + default_list_filter
    search_fields = ('code', 'name')
    readonly_fields = ('id',) + default_readonly_fields
    fieldsets = (
        ('Información Básica', {
            'fields': ('code', 'name', 'has_colors', 'category', 'unit_cost'),
        }),
        default_fields
    )

@admin.register(FinalProduct)
class FinalProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'has_colors','category', 'total_cost') + default_list_display
    list_filter = ('category',) + default_list_filter
    search_fields = ('code', 'name')
    readonly_fields = ('id',) + default_readonly_fields
    fieldsets = (
        ('Información Básica', {
            'fields': ('code', 'name', 'category','has_colors', 'total_cost'),
        }),
        default_fields
    )

@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ('id', 'primary_product', 'final_product', 'color', 'hex_code', 'stock') + default_list_display
    list_filter = ('color', 'stock') + default_list_filter
    search_fields = ('color', 'hex_code')
    readonly_fields = ('id',) + default_readonly_fields
    fieldsets = (
        ('Información Básica', {
            'fields': ('primary_product', 'final_product', 'color', 'hex_code', 'stock'),
        }),
        default_fields
    )

@admin.register(FinalProductComposition)
class FinalProductCompositionAdmin(admin.ModelAdmin):
    list_display = ('id', 'final_product', 'primary_product', 'quantity') + default_list_display
    list_filter = ('final_product', 'primary_product') + default_list_filter
    search_fields = ('final_product__name', 'primary_product__name')
    readonly_fields = ('id',) + default_readonly_fields
    fieldsets = (
        ('Información Básica', {
            'fields': ('final_product', 'primary_product', 'quantity'),
        }),
        default_fields
    )