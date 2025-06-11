from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from rest_framework.views import APIView
from rest_framework.response import Response
from movement.models import InventoryMovement
from product.models import FinalProduct
from supplier.models import Supplier
from datetime import datetime, timedelta
from django.utils import timezone

class MovementReportView(APIView):
    def get(self, request):
        # Obtener parámetros
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Si no hay fechas, usar último mes
        if not start_date:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Query base
        movements = InventoryMovement.objects.filter(
            created_at__date__range=[start_date, end_date]
        )
        
        # Resumen por dirección
        direction_summary = movements.values('direction').annotate(
            total=Count('id'),
            total_value=Sum('total_price')
        )
        
        # Resumen por tipo de razón
        reason_summary = movements.values(
            'reason_type__name'
        ).annotate(
            total=Count('id'),
            total_value=Sum('total_price')
        )
        
        # Resumen por mes
        monthly_summary = movements.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            total=Count('id'),
            total_value=Sum('total_price')
        ).order_by('month')
        
        return Response({
            'direction_summary': direction_summary,
            'reason_summary': reason_summary,
            'monthly_summary': monthly_summary
        })

class InventoryReportView(APIView):
    def get(self, request):
        # Stock actual por producto
        products = FinalProduct.objects.all()
        
        products_summary = []
        total_inventory_value = 0
        
        for product in products:
            stock = product.get_total_stock()
            value = stock * product.total_cost
            total_inventory_value += value
            
            products_summary.append({
                'id': product.id,
                'code': product.code,
                'name': product.name,
                'stock': stock,
                'value': value,
                'category': product.category.name if product.category else 'Sin Categoría'
            })
        
        # Productos con bajo stock (menos de 10 unidades)
        low_stock = [p for p in products_summary if p['stock'] < 10]
        
        return Response({
            'products': products_summary,
            'total_value': total_inventory_value,
            'low_stock': low_stock
        })

class SupplierReportView(APIView):
    def get(self, request):
        # Período por defecto: último año
        end_date = timezone.now()
        start_date = end_date - timedelta(days=365)
        
        suppliers = Supplier.objects.all()
        supplier_summary = []
        
        for supplier in suppliers:
            movements = InventoryMovement.objects.filter(
                supplier=supplier,
                created_at__date__range=[start_date, end_date]
            )
            
            total_movements = movements.count()
            total_value = movements.aggregate(
                total=Sum('total_price')
            )['total'] or 0
            
            supplier_summary.append({
                'id': supplier.id,
                'name': supplier.company_name,
                'total_movements': total_movements,
                'total_value': total_value
            })
        
        return Response({
            'suppliers': sorted(supplier_summary, key=lambda x: x['total_value'], reverse=True)
        })
