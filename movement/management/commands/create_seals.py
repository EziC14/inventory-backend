from django.core.management.base import BaseCommand
from product.models import PrimaryProduct, ProductColor, Category
from django.db import transaction

class Command(BaseCommand):
    help = 'Crea productos tipo sello automáticamente'

    def handle(self, *args, **kwargs):
        category_id = "6c237c7f-7268-43c6-8ca5-7fbb67ec0ec0"
        codes = [
            "004910", "004911", "004912", "004913", "004915", "004916", "004922", "004923", "004924",
            "004927", "004928", "004929", "004921", "046025", "003911", "003912", "008911", "004724",
            "004727", "004729", "002910", "005430", "005440", "005460", "004810", "009511", "009512"
        ]

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"La categoría {category_id} no existe."))
            return

        for code in codes:
            try:
                name_number = str(int(code))  # elimina ceros a la izquierda
                with transaction.atomic():
                    primary_product = PrimaryProduct.objects.create(
                        code=code,
                        name=f"Sello {name_number}",
                        description="Producto generado automáticamente",
                        category=category,
                        unit_cost=0.0,  # puedes ajustar esto si lo necesitas
                        has_colors=False
                    )
                    ProductColor.objects.create(
                        primary_product=primary_product,
                        color="Neutro",
                        hex_code="#FFFFFF",
                        stock=20
                    )
                    self.stdout.write(self.style.SUCCESS(f"Producto {code} creado con éxito."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creando producto {code}: {str(e)}"))
