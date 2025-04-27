from django.db import models
from security.models import Updater
from django.contrib.auth.models import User, Group
from django.utils import timezone
from product.models import PrimaryProduct, FinalProduct, ProductColor
from supplier.models import Supplier
import uuid

# Create your models here.
class ReasonType(Updater):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="ID")
    name = models.CharField(max_length=100, verbose_name="Nombre")  # Compra, Venta, Devolución, Ajuste, etc.
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    is_input = models.BooleanField(default=True, verbose_name="Es Entrada")
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = "movement_type"
        verbose_name = "Tipo de Movimiento"
        verbose_name_plural = "Tipos de Movimientos"

class InventoryMovement(Updater):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateTimeField(default=timezone.now, verbose_name="Fecha y Hora")
    direction = models.CharField(max_length=10, choices=[('input', 'Entrada'), ('output', 'Salida')], verbose_name="Dirección")
    reason_type = models.ForeignKey(ReasonType, on_delete=models.PROTECT, related_name='movements', verbose_name="Motivo del Movimiento")
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Proveedor")
    notes = models.TextField(blank=True, null=True, verbose_name="Notas")

    def __str__(self):
        return f"{self.get_direction_display()} - {self.date.strftime('%d/%m/%Y')}"

    class Meta:
        db_table = "inventory_movement"
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"

class InventoryMovementDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    movement = models.ForeignKey(InventoryMovement, on_delete=models.CASCADE, related_name="details", verbose_name="Movimiento")
    primary_product = models.ForeignKey(PrimaryProduct, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Producto Primario")
    final_product = models.ForeignKey(FinalProduct, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Producto Final")
    product_color = models.ForeignKey(ProductColor, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Color")
    quantity = models.IntegerField(verbose_name="Cantidad")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unitario")
    total_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Precio Total", blank=True)

    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.quantity * self.unit_price
        
        # Ajustar stock
        if self.product_color:
            if self.movement.direction == 'input':
                self.product_color.stock += self.quantity
            else:
                self.product_color.stock -= self.quantity
            self.product_color.save()

        super().save(*args, **kwargs)

    def __str__(self):
        producto = self.primary_product or self.final_product
        return f"{producto} x {self.quantity}"

    class Meta:
        db_table = "inventory_movement_detail"
        verbose_name = "Detalle del Movimiento"
        verbose_name_plural = "Detalles de Movimiento"