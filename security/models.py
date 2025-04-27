from crequest.middleware import CrequestMiddleware
from django.contrib.auth.models import User
from django.db import models
from decimal import Decimal
import uuid
from datetime import timedelta
from django.utils import timezone

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


class CustomerUser(Updater):
    uuid     = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name     = models.CharField(max_length=250, verbose_name="Nombre")
    last_name = models.CharField(max_length=250, verbose_name="Apellido")
    email    = models.EmailField(max_length=250, verbose_name="Email")
    phone    = models.CharField(max_length=20, verbose_name="Teléfono")
    user     = models.OneToOneField(User,related_name='employee_user', on_delete=models.CASCADE, default=None, blank=True, null=True)
    is_trial = models.BooleanField(default=True, verbose_name="En prueba")
    
    def __str__(self):
        return '{}'.format(self.name)
    
    def complete_name(self):
        return '{} {}'.format(self.name, self.last_name)
    
    class Meta:
        managed             = True
        db_table            = "customer_user"
        verbose_name        = "Cliente Usuario"
        verbose_name_plural = "Clientes Usuarios"
        ordering            = ['name']

class VerificationCode(Updater):
    customer_user = models.ForeignKey(CustomerUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    
    @property
    def is_expired(self):
        return timezone.now() > (self.updated_at + timedelta(minutes=15))

    class Meta:
        db_table            = "verification_code"
        verbose_name        = "Código de verificación"
        verbose_name_plural = "Códigos de verificación"
        
class PasswordResetRequest(Updater):
    customer_user = models.ForeignKey(CustomerUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    changed = models.BooleanField(default=False)
    
    @property
    def is_expired(self):
        return timezone.now() > (self.updated_at + timedelta(minutes=15))
    
    class Meta:
        db_table            = "password_reset_request"
        verbose_name        = "Solicitud de restablecimiento de contraseña"
        verbose_name_plural = "Solicitudes de restablecimiento de contraseña"