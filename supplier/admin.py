from django.contrib import admin
from supplier.models import *
from security.admin import default_list_display
from security.admin import default_list_editable
from security.admin import default_list_filter
from security.admin import default_search_fields
from security.admin import default_readonly_fields
from security.admin import default_fields

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('id', 'contact_name', 'contact_name', 'company_name', 'phone', 'email') + default_list_display
    list_filter = ('contact_name',) + default_list_filter
    search_fields = ('contact_name', 'company_name')
    readonly_fields = ('id',) + default_readonly_fields
    fieldsets = (
        ('Información Básica', {
            'fields': ('contact_name', 'company_name', 'phone', 'email', 'address', 'ruc'),
        }),
        default_fields
    )



