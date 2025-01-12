from crequest.middleware import CrequestMiddleware
from django.contrib.auth.models import User
from django.db import models
from decimal import Decimal

def get_user():
    current_request = CrequestMiddleware.get_request()
    result = None
    if current_request is not None:
        result = None if not current_request.user.is_authenticated else current_request.user

class Updater(models.Model):
    is_active  = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    created_by = models.CharField(max_length=500, null=True, blank=True, default=None, verbose_name="Creado por")
    updated_by = models.CharField(max_length=500, null=True, blank=True, default=None, verbose_name="Actualizado por")

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        user = get_user()
        if user is not None:
            if not hasattr( self, 'created_by') or  self.created_by is None:
                self.created_by = user.username
            self.updated_by = user.username
        super(Updater, self).save(*args, **kwargs)
