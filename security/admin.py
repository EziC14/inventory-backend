from django.contrib import admin
from django.contrib.auth.models import Group
# from .models import UserProfile

default_list_display    = ('is_active', 'created_at', 'created_by', 'updated_at', 'updated_by')
default_list_editable   = ('is_active',)
default_list_filter     = ('created_at', 'created_by', 'updated_at', 'updated_by')
default_search_fields   = ('created_at', 'created_by', 'updated_at', 'updated_by')
default_readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by')
default_fields          = ('Información de Auditoria', {
                            'fields': (
                                ('created_at', 'created_by'),
                                ('updated_at', 'updated_by')
                            )
                        })

# admin.site.unregister(Group)
# admin.site.register(UserProfile)