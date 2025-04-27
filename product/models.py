from django.db import models
from security.models import Updater
from django.contrib.auth.models import User, Group
from django.utils import timezone
import uuid

class Category(Updater):
    id                = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="ID")
    name = models.CharField(max_length=100)
    description = models.TextField(default=None, blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table            = "category"
        verbose_name        = "Categoría"
        verbose_name_plural = "Categorías"

class PrimaryProduct(Updater):
    id   = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="ID")
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    description = models.TextField(default=None, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='primary_products', default=None, blank=True, null=True)
    has_colors = models.BooleanField(default=False)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
    
    def get_total_stock(self):
        return sum([color.stock for color in self.colors.all()])
    
    def get_colors(self):
        return [
            {
                'id': color.id,
                'name': color.color,
                'hex': color.hex_code,
                'stock': color.stock,
            }
            for color in self.colors.all()
        ]
    
    class Meta:
        db_table            = "primary_product"
        verbose_name        = "Producto Primario"
        verbose_name_plural = "Productos Primarios"

class FinalProduct(Updater):
    id                = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="ID")
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    description = models.TextField(default=None, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='final_products', default=None, blank=True, null=True)
    has_colors = models.BooleanField(default=False)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
    
    def get_total_stock(self):
        return sum([color.stock for color in self.colors.all()])
    
    def get_compositions(self):
        return [
            {
                'id': composition.primary_product.id,
                'name': composition.primary_product.name,
                'category': composition.primary_product.category.name,
                'quantity': composition.quantity,
            }
            for composition in self.compositions.all()
        ]
    
    def get_colors(self):
        return [
            {
                'id': color.id,
                'name': color.color,
                'hex': color.hex_code,
                'stock': color.stock,
            }
            for color in self.colors.all()
        ]
    
    class Meta:
        db_table            = "final_product"
        verbose_name        = "Producto Final"
        verbose_name_plural = "Productos Finales"

class ProductColor(Updater):
    id                = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="ID")
    primary_product = models.ForeignKey(PrimaryProduct, on_delete=models.CASCADE, null=True, blank=True, related_name='colors')
    final_product = models.ForeignKey(FinalProduct, on_delete=models.CASCADE, null=True, blank=True, related_name='colors')
    stock = models.IntegerField(default=0)
    color = models.CharField(max_length=50)
    hex_code = models.CharField(max_length=7)

    def __str__(self):
        return self.color

    class Meta:
        db_table            = "product_color"
        verbose_name        = "Color de Producto"
        verbose_name_plural = "Colores de Producto"

class FinalProductComposition(Updater):
    id                = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="ID")
    final_product = models.ForeignKey(FinalProduct, on_delete=models.CASCADE, related_name='compositions')
    primary_product = models.ForeignKey(PrimaryProduct, on_delete=models.CASCADE, related_name='used_in_compositions')
    quantity = models.IntegerField()

    def __str__(self):
        return self.primary_product.name
    
    class Meta:
        db_table            = "final_product_composition"
        verbose_name        = "Composición de Producto Final"
        verbose_name_plural = "Composiciones de Productos Finales"

