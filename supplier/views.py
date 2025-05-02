from django.shortcuts import render
from rest_framework.views import APIView
from product.models import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.db import transaction
from .models import *

# Create your views here.

class SupplierView(APIView):
    def get(self, request):
        suppliers = Supplier.objects.prefetch_related("primary_product").distinct()
        data = []
        
        for supplier in suppliers:
            # Datos básicos del proveedor
            supplier_data = {
                "id": supplier.id,
                "contact_name": supplier.contact_name,
                "company_name": supplier.company_name,
                "phone": supplier.phone,
                "email": supplier.email,
                "address": supplier.address,
                "ruc": supplier.ruc,
                "products": []  # Lista para almacenar los productos del proveedor
            }
            
            # Añadir todos los productos primarios asociados al proveedor
            for product in supplier.primary_product.all():
                product_data = {
                    "id": product.id,
                    "name": product.name,
                    "category": product.category.name if product.category else None,
                    "unit_cost": product.unit_cost,
                    "code": product.code,
                    # Añade aquí otros campos de PrimaryProduct que quieras incluir
                }
                supplier_data["products"].append(product_data)
                
            data.append(supplier_data)
            
        return Response({'status': 'OK', 'msg': 'Listado de Proveedores', 'data': data}, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        
        # Crear el proveedor con los datos básicos
        supplier = Supplier.objects.create(
            contact_name=data.get("contact_name"),
            company_name=data.get("company_name"),
            phone=data.get("phone"),
            email=data.get("email"),
            address=data.get("address"),
            ruc=data.get("ruc"),
        )
        
        # Asociar productos primarios si se proporcionan
        product_ids = data.get("products", [])
        if product_ids:
            supplier.primary_product.set(product_ids)
        
        return Response({
            'status': 'OK', 
            'msg': 'Proveedor creado correctamente',
            'data': {
                'id': supplier.id,
                'name': supplier.name
            }
        }, status=status.HTTP_201_CREATED)
    
class SupplierDetailView(APIView):
    def get(self, request, supplier_id):
        try:
            supplier = Supplier.objects.get(id=supplier_id)
            data = {
                "id": supplier.id,
                "contact_name": supplier.contact_name,
                "company_name": supplier.company_name,
                "phone": supplier.phone,
                "email": supplier.email,
                "address": supplier.address,
                "ruc": supplier.ruc,
                "products": []  # Lista para almacenar los productos del proveedor
            }
            
            # Añadir todos los productos primarios asociados al proveedor
            for product in supplier.primary_product.all():
                product_data = {
                    "id": product.id,
                    "name": product.name,
                    "category": product.category.name if product.category else None,
                }
                data["products"].append(product_data)
                
            return Response({'status': 'OK', 'msg': 'Proveedor encontrado', 'data': data}, status=status.HTTP_200_OK)
        except Supplier.DoesNotExist:
            return Response({'status': 'ERROR', 'msg': 'Proveedor no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
    def put(self, request, supplier_id):
        try:
            supplier = Supplier.objects.get(id=supplier_id)
            data = request.data
            
            supplier.contact_name = data.get("contact_name", supplier.contact_name)
            supplier.company_name = data.get("company_name", supplier.company_name)
            supplier.phone = data.get("phone", supplier.phone)
            supplier.email = data.get("email", supplier.email)
            supplier.address = data.get("address", supplier.address)
            supplier.ruc = data.get("ruc", supplier.ruc)
            
            supplier.save()
            
            product_ids = data.get("products", [])
            if product_ids:
                supplier.primary_product.set(product_ids)
            
            return Response({
                'status': 'OK', 
                'msg': 'Proveedor actualizado correctamente'
            }, status=status.HTTP_200_OK)
        except Supplier.DoesNotExist:
            return Response({'status': 'ERROR', 'msg': 'Proveedor no encontrado'}, status=status.HTTP_404_NOT_FOUND)