from django.db import models
from security.models import Updater
from product.models import PrimaryProduct
import uuid

# Create your views here.

class Supplier(Updater):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="ID")
    contact_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nombre de Contacto")
    company_name = models.CharField(max_length=150, blank=True, null=True, verbose_name="Nombre de la Empresa")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    email = models.EmailField(blank=True, null=True, verbose_name="Correo Electrónico")
    address = models.TextField(blank=True, null=True, verbose_name="Dirección")
    primary_product = models.ManyToManyField(PrimaryProduct, related_name='suppliers')
    
    def __str__(self):
        return self.company_name
    
    class Meta:
        db_table = "supplier"
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
