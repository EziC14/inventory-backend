from django.shortcuts import render
from rest_framework.views import APIView
from product.models import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.db import transaction

# Create your views here.
class GetPostCategory(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        try:
            categories = Category.objects.all()

            category_data = []
            for category in categories:
                category_data.append(
                    {
                        'id': category.id,
                        'name': category.name,
                        'description': category.description,
                    }
                )

            return Response(
                {
                    'status': 'OK',
                    'msg': 'Listado de categorías',
                    'data': category_data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    'status': 'ERROR',
                    'msg': 'Ocurrió un error al obtener las categorías',
                    'detail': str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    def post(self, request):
        try:
            name = request.data.get('name')
            description = request.data.get('description')

            if not name:
                return Response(
                    {
                        'status': 'ERROR',
                        'msg': 'Falta el nombre de la categoría',
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            category = Category.objects.create(
                name=name,
                description=description,
            )

            return Response(
                {
                    'status': 'OK',
                    'msg': 'Categoría creada',
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {
                    'status': 'ERROR',
                    'msg': 'Ocurrió un error al crear la categoría',
                    'detail': str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class GetPostPrimaryProduct(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        try:
            
            category = request.query_params.get('category')

            primary_products = PrimaryProduct.objects.select_related('category').all()
            
            if category:
                primary_products = primary_products.filter(category__id=category)

            primary_product_data = []
            for primary_product in primary_products:
                product_data = {
                    'id': primary_product.id,
                    'code': primary_product.code,
                    'name': primary_product.name,
                    'description': primary_product.description,
                    'category': primary_product.category.name,
                    'unit_cost': primary_product.unit_cost,
                }

                primary_product_data.append(product_data)

            return Response(
                {
                    'status': 'OK',
                    'msg': 'Listado de productos primarios',
                    'data': primary_product_data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    'status': 'ERROR',
                    'msg': 'Ocurrió un error al obtener los productos primarios',
                    'detail': str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    def post(self, request):
        try:
            code = request.data.get('code')
            name = request.data.get('name')
            description = request.data.get('description')
            stock = request.data.get('stock')
            unit_cost = request.data.get('unit_cost')
            category_id = request.data.get('category')
            has_colors = request.data.get('has_colors', False)  # Por defecto False si no se envía
            colors = request.data.get('colors')  # Lista de colores [{'name_color': 'Red', 'hex_code': '#FF0000', stock: 1}, ...]

            if not all([code, name, unit_cost]):
                return Response(
                    {
                        'status': 'ERROR',
                        'msg': 'Faltan datos requeridos para crear el producto primario',
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            category = None
            if category_id:
                try:
                    category = Category.objects.get(id=category_id)
                except Category.DoesNotExist:
                    return Response(
                        {'status': 'ERROR', 'msg': f'La categoría con ID {category_id} no existe.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            with transaction.atomic():  # Comienza la transacción
                primary_product = PrimaryProduct.objects.create(
                    code=code,
                    name=name,
                    description=description,
                    category=category,
                    unit_cost=unit_cost,
                )

                if has_colors:
                    if colors:
                        for color in colors:
                            name_color = color.get('name_color')
                            hex_code = color.get('hex_code')
                            color_stock = color.get('stock')
                            if not all([name_color, hex_code, color_stock]):
                                raise ValueError('Cada color debe incluir "name_color", "hex_code" y "stock".')

                            ProductColor.objects.create(
                                primary_product=primary_product,
                                color=name_color,
                                hex_code=hex_code,
                                stock=color_stock
                            )
                    else:
                        raise ValueError('Se indicó que el producto tiene colores, pero no se proporcionaron colores.')
                else:
                    # Crear un color neutro
                    ProductColor.objects.create(
                        primary_product=primary_product,
                        color='Neutro',
                        hex_code='#FFFFFF',  # Un color predeterminado, como blanco
                        stock=stock
                    )

            return Response(
                {
                    'status': 'OK',
                    'msg': 'Producto primario creado',
                },
                status=status.HTTP_201_CREATED
            )

        except ValueError as ve:
            return Response(
                {
                    'status': 'ERROR',
                    'msg': str(ve),
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {
                    'status': 'ERROR',
                    'msg': 'Ocurrió un error al crear el producto primario',
                    'detail': str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class GetPostFinalProduct(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        try:

            category = request.query_params.get('category')

            final_products = FinalProduct.objects.select_related('category').all()

            if category:
                final_products = final_products.filter(category__id=category)
                
            final_product_data = []
            for final_product in final_products:
                product_data = {
                    'id': final_product.id,
                    'code': final_product.code,
                    'name': final_product.name,
                    'description': final_product.description,
                    'category': final_product.category.name,
                    'total_cost': final_product.total_cost,
                }
                final_product_data.append(product_data)

            return Response(
                {
                    'status': 'OK',
                    'msg': 'Listado de productos finales',
                    'data': final_product_data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    'status': 'ERROR',
                    'msg': 'Ocurrió un error al obtener los productos finales',
                    'detail': str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    def post(self, request):
        try:
            # Datos principales del producto final
            code = request.data.get('code')
            name = request.data.get('name')
            description = request.data.get('description')
            stock = request.data.get('stock')
            unit_cost = request.data.get('unit_cost')
            has_colors = request.data.get('has_colors', False)  # Por defecto False si no se envía
            category_id = request.data.get('category')  # Puede ser opcional
            colors = request.data.get('colors')  # Lista de colores [{'name_color': 'Red', 'hex_code': '#FF0000'}, ...]
            compositions = request.data.get('compositions')  # [{ "id": 1, "quantity": 2 }, ...]

            # Validaciones iniciales
            if not all([code, name, unit_cost, compositions]):
                return Response(
                    {'status': 'ERROR', 'msg': 'Faltan datos requeridos para crear el producto final.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not isinstance(compositions, list) or not all(isinstance(comp, dict) for comp in compositions):
                return Response(
                    {'status': 'ERROR', 'msg': 'La estructura de "compositions" debe ser una lista de objetos con "id" y "quantity".'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if colors and (not isinstance(colors, list) or not all(isinstance(color, dict) for color in colors)):
                return Response(
                    {'status': 'ERROR', 'msg': 'La estructura de "colors" debe ser una lista de objetos con "name_color" y "hex_code".'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Intentar obtener la categoría si está presente
            category = None
            if category_id:
                try:
                    category = Category.objects.get(id=category_id)
                except Category.DoesNotExist:
                    return Response(
                        {'status': 'ERROR', 'msg': f'La categoría con ID {category_id} no existe.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            with transaction.atomic():
                # Crear el producto final
                final_product = FinalProduct.objects.create(
                    code=code,
                    name=name,
                    description=description,
                    category=category,  # Puede ser None
                    total_cost=unit_cost,
                )

                # Manejar colores
                if has_colors:
                    if colors:
                        for color in colors:
                            name_color = color.get('name_color')
                            hex_code = color.get('hex_code')
                            color_stock = color.get('stock')
                            if not name_color or not hex_code or not color_stock:
                                return Response(
                                    {'status': 'ERROR', 'msg': 'Cada color debe incluir "name_color", "hex_code" y "stock".'},
                                    status=status.HTTP_400_BAD_REQUEST
                                )
                            ProductColor.objects.create(
                                final_product=final_product,
                                color=name_color,
                                hex_code=hex_code,
                                stock=color_stock
                            )
                    else:
                        return Response(
                            {'status': 'ERROR', 'msg': 'Se indicó que el producto tiene colores, pero no se proporcionaron colores.'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                else:
                    # Crear un color neutro
                    ProductColor.objects.create(
                        final_product=final_product,
                        color='Neutral',
                        hex_code='#FFFFFF',  # Color predeterminado, como blanco
                        stock=stock
                    )

                # Crear composiciones
                for comp in compositions:
                    primary_product_id = comp.get('id')
                    quantity = comp.get('quantity')

                    if not primary_product_id or not quantity or quantity <= 0:
                        return Response(
                            {
                                'status': 'ERROR',
                                'msg': f'Cada composición debe tener un "id" válido y una "quantity" mayor a 0. ID: {primary_product_id}, Cantidad: {quantity}'
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    try:
                        primary_product = PrimaryProduct.objects.get(id=primary_product_id)
                    except PrimaryProduct.DoesNotExist:
                        return Response(
                            {'status': 'ERROR', 'msg': f'El producto primario con ID {primary_product_id} no existe.'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    FinalProductComposition.objects.create(
                        primary_product=primary_product,
                        final_product=final_product,
                        quantity=quantity,
                    )

            return Response(
                {
                    'status': 'OK',
                    'msg': 'Producto final creado correctamente.',
                    'final_product_id': final_product.id
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {
                    'status': 'ERROR',
                    'msg': 'Ocurrió un error al crear el producto final.',
                    'detail': str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )