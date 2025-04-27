from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import InventoryMovement, InventoryMovementDetail, ReasonType
from django.db import transaction
import uuid

# Create your views here.

class InventoryMovementListCreateView(APIView):
    def get(self, request):
        movements = InventoryMovement.objects.all().order_by('-date')
        
        # Filtrado opcional
        direction = request.query_params.get('direction')
        reason_type = request.query_params.get('reason_type')
        supplier = request.query_params.get('supplier')
        
        if direction:
            movements = movements.filter(direction=direction)
        if reason_type:
            movements = movements.filter(reason_type=reason_type)
        if supplier:
            movements = movements.filter(supplier=supplier)
        
        data = []
        
        for movement in movements:
            details_data = []
            for detail in movement.details.all():
                detail_data = {
                    "id": detail.id,
                    "quantity": detail.quantity,
                    "unit_price": detail.unit_price,
                    "total_price": detail.total_price,
                }
                
                if detail.primary_product:
                    detail_data["primary_product"] = {
                        "id": detail.primary_product.id,
                        "name": detail.primary_product.name
                    }
                else:
                    detail_data["primary_product"] = None
                
                if detail.final_product:
                    detail_data["final_product"] = {
                        "id": detail.final_product.id,
                        "name": detail.final_product.name
                    }
                else:
                    detail_data["final_product"] = None
                
                if detail.product_color:
                    detail_data["product_color"] = {
                        "id": detail.product_color.id,
                        "name": detail.product_color.name
                    }
                else:
                    detail_data["product_color"] = None
                
                details_data.append(detail_data)
            
            movement_data = {
                "id": movement.id,
                "date": movement.date,
                "direction": movement.direction,
                "direction_display": movement.get_direction_display(),
                "notes": movement.notes,
                "details": details_data
            }
            
            if movement.reason_type:
                movement_data["reason_type"] = {
                    "id": movement.reason_type.id,
                    "name": movement.reason_type.name
                }
            
            if movement.supplier:
                movement_data["supplier"] = {
                    "id": movement.supplier.id,
                    "name": movement.supplier.name
                }
            else:
                movement_data["supplier"] = None
            
            data.append(movement_data)
        
        return Response({'status': 'OK', 'msg': 'Listado de Movimientos de Inventario', 'data': data}, status=status.HTTP_200_OK)
    
    @transaction.atomic
    def post(self, request):
        try:
            # Datos del movimiento principal
            movement_data = {
                'date': request.data.get('date'),
                'direction': request.data.get('direction'),
                'notes': request.data.get('notes'),
            }
            
            # Referencias a otros modelos
            reason_type_id = request.data.get('reason_type')
            if reason_type_id:
                reason_type = get_object_or_404(ReasonType, id=reason_type_id)
                movement_data['reason_type'] = reason_type
            
            supplier_id = request.data.get('supplier')
            if supplier_id:
                from supplier.models import Supplier
                supplier = get_object_or_404(Supplier, id=supplier_id)
                movement_data['supplier'] = supplier
            
            # Crear el movimiento
            movement = InventoryMovement.objects.create(**movement_data)
            
            # Procesar los detalles
            details = request.data.get('details', [])
            details_data = []
            
            for detail in details:
                detail_data = {
                    'movement': movement,
                    'quantity': detail.get('quantity'),
                    'unit_price': detail.get('unit_price')
                }
                
                # Referencias a productos
                primary_product_id = detail.get('primary_product')
                if primary_product_id:
                    from product.models import PrimaryProduct
                    primary_product = get_object_or_404(PrimaryProduct, id=primary_product_id)
                    detail_data['primary_product'] = primary_product
                
                final_product_id = detail.get('final_product')
                if final_product_id:
                    from product.models import FinalProduct
                    final_product = get_object_or_404(FinalProduct, id=final_product_id)
                    detail_data['final_product'] = final_product
                
                product_color_id = detail.get('product_color')
                if product_color_id:
                    from product.models import ProductColor
                    product_color = get_object_or_404(ProductColor, id=product_color_id)
                    detail_data['product_color'] = product_color
                
                # Crear el detalle - el stock se actualiza automáticamente en el método save()
                detail_obj = InventoryMovementDetail.objects.create(**detail_data)
                
                # Preparar los datos para la respuesta
                detail_response = {
                    'id': detail_obj.id,
                    'quantity': detail_obj.quantity,
                    'unit_price': detail_obj.unit_price,
                    'total_price': detail_obj.total_price,
                }
                
                if detail_obj.primary_product:
                    detail_response['primary_product'] = {
                        'id': detail_obj.primary_product.id,
                        'name': detail_obj.primary_product.name
                    }
                
                if detail_obj.final_product:
                    detail_response['final_product'] = {
                        'id': detail_obj.final_product.id,
                        'name': detail_obj.final_product.name
                    }
                
                if detail_obj.product_color:
                    detail_response['product_color'] = {
                        'id': detail_obj.product_color.id,
                        'name': detail_obj.product_color.name
                    }
                
                details_data.append(detail_response)
            
            # Preparar la respuesta
            response_data = {
                'id': movement.id,
                'date': movement.date,
                'direction': movement.direction,
                'direction_display': movement.get_direction_display(),
                'notes': movement.notes,
                'details': details_data
            }
            
            if movement.reason_type:
                response_data['reason_type'] = {
                    'id': movement.reason_type.id,
                    'name': movement.reason_type.name
                }
            
            if movement.supplier:
                response_data['supplier'] = {
                    'id': movement.supplier.id,
                    'name': movement.supplier.name
                }
            
            return Response({
                'status': 'OK',
                'msg': 'Movimiento de inventario creado exitosamente',
                'data': response_data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'status': 'ERROR',
                'msg': f'Error al crear el movimiento: {str(e)}',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

class InventoryMovementDetailView(APIView):
    def get(self, request, id):
        try:
            movement = get_object_or_404(InventoryMovement, id=id)
            
            details_data = []
            for detail in movement.details.all():
                detail_data = {
                    "id": detail.id,
                    "quantity": detail.quantity,
                    "unit_price": detail.unit_price,
                    "total_price": detail.total_price,
                }
                
                if detail.primary_product:
                    detail_data["primary_product"] = {
                        "id": detail.primary_product.id,
                        "name": detail.primary_product.name
                    }
                else:
                    detail_data["primary_product"] = None
                
                if detail.final_product:
                    detail_data["final_product"] = {
                        "id": detail.final_product.id,
                        "name": detail.final_product.name
                    }
                else:
                    detail_data["final_product"] = None
                
                if detail.product_color:
                    detail_data["product_color"] = {
                        "id": detail.product_color.id,
                        "name": detail.product_color.name
                    }
                else:
                    detail_data["product_color"] = None
                
                details_data.append(detail_data)
            
            movement_data = {
                "id": movement.id,
                "date": movement.date,
                "direction": movement.direction,
                "direction_display": movement.get_direction_display(),
                "notes": movement.notes,
                "details": details_data
            }
            
            if movement.reason_type:
                movement_data["reason_type"] = {
                    "id": movement.reason_type.id,
                    "name": movement.reason_type.name
                }
            
            if movement.supplier:
                movement_data["supplier"] = {
                    "id": movement.supplier.id,
                    "name": movement.supplier.name
                }
            else:
                movement_data["supplier"] = None
            
            return Response({
                'status': 'OK',
                'msg': 'Detalle de Movimiento de Inventario',
                'data': movement_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'ERROR',
                'msg': f'Error al obtener el movimiento: {str(e)}',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)
    
    @transaction.atomic
    def put(self, request, id):
        try:
            movement = get_object_or_404(InventoryMovement, id=id)
            
            # Actualizar datos del movimiento principal
            if 'date' in request.data:
                movement.date = request.data.get('date')
            
            if 'direction' in request.data:
                movement.direction = request.data.get('direction')
            
            if 'notes' in request.data:
                movement.notes = request.data.get('notes')
            
            # Actualizar referencias a otros modelos
            reason_type_id = request.data.get('reason_type')
            if reason_type_id:
                reason_type = get_object_or_404(ReasonType, id=reason_type_id)
                movement.reason_type = reason_type
            
            supplier_id = request.data.get('supplier')
            if supplier_id:
                from supplier.models import Supplier
                supplier = get_object_or_404(Supplier, id=supplier_id)
                movement.supplier = supplier
            elif 'supplier' in request.data and request.data['supplier'] is None:
                movement.supplier = None
            
            movement.save()
            
            # Actualizar detalles: Eliminamos los actuales y creamos nuevos
            if 'details' in request.data:
                # Revertir el stock de los detalles anteriores antes de eliminarlos
                for detail in movement.details.all():
                    if detail.product_color:
                        if movement.direction == 'input':
                            detail.product_color.stock -= detail.quantity
                        else:
                            detail.product_color.stock += detail.quantity
                        detail.product_color.save()
                
                # Eliminar los detalles actuales
                movement.details.all().delete()
                
                # Crear los nuevos detalles
                details = request.data.get('details', [])
                details_data = []
                
                for detail in details:
                    detail_data = {
                        'movement': movement,
                        'quantity': detail.get('quantity'),
                        'unit_price': detail.get('unit_price')
                    }
                    
                    # Referencias a productos
                    primary_product_id = detail.get('primary_product')
                    if primary_product_id:
                        from product.models import PrimaryProduct
                        primary_product = get_object_or_404(PrimaryProduct, id=primary_product_id)
                        detail_data['primary_product'] = primary_product
                    
                    final_product_id = detail.get('final_product')
                    if final_product_id:
                        from product.models import FinalProduct
                        final_product = get_object_or_404(FinalProduct, id=final_product_id)
                        detail_data['final_product'] = final_product
                    
                    product_color_id = detail.get('product_color')
                    if product_color_id:
                        from product.models import ProductColor
                        product_color = get_object_or_404(ProductColor, id=product_color_id)
                        detail_data['product_color'] = product_color
                    
                    # Crear el detalle - el stock se actualiza automáticamente en el método save()
                    detail_obj = InventoryMovementDetail.objects.create(**detail_data)
                    
                    # Preparar los datos para la respuesta
                    detail_response = {
                        'id': detail_obj.id,
                        'quantity': detail_obj.quantity,
                        'unit_price': detail_obj.unit_price,
                        'total_price': detail_obj.total_price,
                    }
                    
                    if detail_obj.primary_product:
                        detail_response['primary_product'] = {
                            'id': detail_obj.primary_product.id,
                            'name': detail_obj.primary_product.name
                        }
                    
                    if detail_obj.final_product:
                        detail_response['final_product'] = {
                            'id': detail_obj.final_product.id,
                            'name': detail_obj.final_product.name
                        }
                    
                    if detail_obj.product_color:
                        detail_response['product_color'] = {
                            'id': detail_obj.product_color.id,
                            'name': detail_obj.product_color.name
                        }
                    
                    details_data.append(detail_response)
            else:
                # Si no hay detalles en la solicitud, mantener los actuales
                details_data = []
                for detail in movement.details.all():
                    detail_data = {
                        "id": detail.id,
                        "quantity": detail.quantity,
                        "unit_price": detail.unit_price,
                        "total_price": detail.total_price,
                    }
                    
                    if detail.primary_product:
                        detail_data["primary_product"] = {
                            "id": detail.primary_product.id,
                            "name": detail.primary_product.name
                        }
                    else:
                        detail_data["primary_product"] = None
                    
                    if detail.final_product:
                        detail_data["final_product"] = {
                            "id": detail.final_product.id,
                            "name": detail.final_product.name
                        }
                    else:
                        detail_data["final_product"] = None
                    
                    if detail.product_color:
                        detail_data["product_color"] = {
                            "id": detail.product_color.id,
                            "name": detail.product_color.name
                        }
                    else:
                        detail_data["product_color"] = None
                    
                    details_data.append(detail_data)
            
            # Preparar la respuesta
            response_data = {
                'id': movement.id,
                'date': movement.date,
                'direction': movement.direction,
                'direction_display': movement.get_direction_display(),
                'notes': movement.notes,
                'details': details_data
            }
            
            if movement.reason_type:
                response_data['reason_type'] = {
                    'id': movement.reason_type.id,
                    'name': movement.reason_type.name
                }
            
            if movement.supplier:
                response_data['supplier'] = {
                    'id': movement.supplier.id,
                    'name': movement.supplier.name
                }
            
            return Response({
                'status': 'OK',
                'msg': 'Movimiento de inventario actualizado exitosamente',
                'data': response_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'ERROR',
                'msg': f'Error al actualizar el movimiento: {str(e)}',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @transaction.atomic
    def delete(self, request, id):
        try:
            movement = get_object_or_404(InventoryMovement, id=id)
            
            # Revertir el stock de los detalles antes de eliminar
            for detail in movement.details.all():
                if detail.product_color:
                    if movement.direction == 'input':
                        detail.product_color.stock -= detail.quantity
                    else:
                        detail.product_color.stock += detail.quantity
                    detail.product_color.save()
            
            # Eliminar el movimiento (los detalles se eliminarán automáticamente por CASCADE)
            movement.delete()
            
            return Response({
                'status': 'OK',
                'msg': 'Movimiento de inventario eliminado exitosamente',
                'data': None
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'ERROR',
                'msg': f'Error al eliminar el movimiento: {str(e)}',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

class ReasonTypeView(APIView):
    def get(self, request):
        reason_types = ReasonType.objects.all()
        
        data = []
        
        for reason_type in reason_types:
            reason_type_data = {
                "id": reason_type.id,
                "name": reason_type.name,
                "description": reason_type.description,
                "is_input": reason_type.is_input
            }
            data.append(reason_type_data)
        
        return Response({'status': 'OK', 'msg': 'Listado de Tipos de Movimiento', 'data': data}, status=status.HTTP_200_OK)
    
    def post(self, request):
        data = request.data
        
        if ReasonType.objects.filter(name=data.get("name")).exists():
            return Response({'status': 'ERROR', 'msg': 'El tipo de movimiento ya existe'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Crear el tipo de movimiento con los datos proporcionados
        reason_type = ReasonType.objects.create(
            name=data.get("name"),
            description=data.get("description"),
            is_input=data.get("is_input")
        )
        
        return Response({'status': 'OK', 'msg': 'Tipo de Movimiento creado', 'data': str(reason_type.id)}, status=status.HTTP_201_CREATED)
    
class ReasonTypeDetailView(APIView):
    def get(self, request, reason_type_id):
        try:
            reason_type = ReasonType.objects.get(id=reason_type_id)
            data = {
                "id": reason_type.id,
                "name": reason_type.name,
                "description": reason_type.description,
                "is_input": reason_type.is_input
            }
            
            return Response({'status': 'OK', 'msg': 'Tipo de Movimiento encontrado', 'data': data}, status=status.HTTP_200_OK)
        except ReasonType.DoesNotExist:
            return Response({'status': 'ERROR', 'msg': 'Tipo de Movimiento no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, reason_type_id):
        try:
            reason_type = ReasonType.objects.get(id=reason_type_id)
            data = request.data
            
            # Actualizar los campos del tipo de movimiento
            reason_type.name = data.get("name", reason_type.name)
            reason_type.description = data.get("description", reason_type.description)
            reason_type.is_input = data.get("is_input", reason_type.is_input)
            reason_type.save()
            
            return Response({'status': 'OK', 'msg': 'Tipo de Movimiento actualizado', 'data': str(reason_type.id)}, status=status.HTTP_200_OK)
        except ReasonType.DoesNotExist:
            return Response({'status': 'ERROR', 'msg': 'Tipo de Movimiento no encontrado'}, status=status.HTTP_404_NOT_FOUND)