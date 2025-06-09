from django.db import models
from security.models import Updater
from django.contrib.auth.models import User, Group
from django.utils import timezone
from product.models import PrimaryProduct, FinalProduct, ProductColor
from supplier.models import Supplier
import uuid
from django.core.exceptions import ValidationError

# Create your models here.
class ReasonType(Updater):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="ID")
    name = models.CharField(max_length=100, verbose_name="Nombre")  # Compra, Venta, Devolución, Ajuste, etc.
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = "movement_type"
        verbose_name = "Tipo de Movimiento"
        verbose_name_plural = "Tipos de Movimientos"

class InventoryMovement(Updater):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    direction = models.CharField(max_length=10, choices=[('IN', 'Entrada'), ('OUT', 'Salida')], verbose_name="Dirección")
    reason_type = models.ForeignKey(ReasonType, on_delete=models.PROTECT, related_name='movements', verbose_name="Motivo del Movimiento")
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Proveedor")
    client_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nombre del Cliente")
    notes = models.TextField(blank=True, null=True, verbose_name="Notas")
    total_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Precio Total", blank=True)

    def __str__(self):
        return f"{self.get_direction_display()} - {self.created_at.strftime('%d/%m/%Y')}"

    class Meta:
        db_table = "inventory_movement"
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"

class InventoryMovementDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    movement = models.ForeignKey(InventoryMovement, on_delete=models.CASCADE, related_name='details')
    final_product = models.ForeignKey(FinalProduct, on_delete=models.SET_NULL, null=True, blank=True)
    primary_product = models.ForeignKey(PrimaryProduct, on_delete=models.SET_NULL, null=True, blank=True)
    product_color = models.ForeignKey(ProductColor, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        if self.movement.direction == 'OUT' and self.product_color:
            if self.product_color.stock < self.quantity:
                raise ValidationError(f"No hay suficiente stock para {self.product_color.color}. Stock disponible: {self.product_color.stock}")

        self.total_price = self.quantity * self.unit_price

        if self.product_color:
            if self.movement.direction == 'IN':
                self.product_color.stock += self.quantity
            elif self.movement.direction == 'OUT':
                self.product_color.stock -= self.quantity
            self.product_color.save()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.product_color:
            if self.movement.direction == 'IN':
                self.product_color.stock -= self.quantity
            elif self.movement.direction == 'OUT':
                self.product_color.stock += self.quantity
            self.product_color.save()

        super().delete(*args, **kwargs)

    class Meta:
        db_table = "inventory_movement_detail"
        verbose_name = "Detalle de Movimiento de Inventario"
        verbose_name_plural = "Detalles de Movimientos de Inventario"