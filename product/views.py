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
                    has_colors=has_colors,
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
                    has_colors=has_colors,
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

class GetProduct(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        try:
            
            category = request.query_params.get('category')
            type = request.query_params.get('type')

            primary_products = PrimaryProduct.objects.select_related('category').all()
            final_products = FinalProduct.objects.select_related('category').all()

            if category:
                primary_products = primary_products.filter(category__id=category)
                final_products = final_products.filter(category__id=category)
            
            if type:
                if type == 'PRI':
                    final_products = []
                elif type == 'FIN':
                    primary_products = []
                else:
                    return Response(
                        {
                            'status': 'ERROR',
                            'msg': 'El tipo de producto debe ser "primary" o "final"',
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            product_data = []

            for primary_product in primary_products:
                product_data.append(
                    {
                        'id': primary_product.id,
                        'code': primary_product.code,
                        'name': primary_product.name,
                        'description': primary_product.description,
                        'category': primary_product.category.name,
                        'unit_cost': primary_product.unit_cost,
                        'total_stock': primary_product.get_total_stock(),
                        'type': 'PRI'
                    }
                )
            
            for final_product in final_products:
                product_data.append(
                    {
                        'id': final_product.id,
                        'code': final_product.code,
                        'name': final_product.name,
                        'description': final_product.description,
                        'category': final_product.category.name,
                        'unit_cost': final_product.total_cost,
                        'total_stock': final_product.get_total_stock(),
                        'type': 'FIN'
                    }
                )

            return Response(
                {
                    'status': 'OK',
                    'msg': 'Listado de productos',
                    'data': product_data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    'status': 'ERROR',
                    'msg': 'Ocurrió un error al obtener los productos',
                    'detail': str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GetProductDetail(APIView):
    permission_classes = [AllowAny]
    def get(self, request, product_id):
        try:
            primary_product = PrimaryProduct.objects.select_related('category').filter(id=product_id).first()
            final_product = FinalProduct.objects.select_related('category').filter(id=product_id).first()

            
            if primary_product:

                product_data = {
                    'id': primary_product.id,
                    'code': primary_product.code,
                    'name': primary_product.name,
                    'description': primary_product.description,
                    'category': {
                        'id': primary_product.category.id,
                        'name': primary_product.category.name,
                    },
                    'is_final': False,
                    'has_colors': primary_product.has_colors,
                    'colors': primary_product.get_colors(),
                    'unit_cost': primary_product.unit_cost,
                }
            elif final_product:

                product_data = {
                    'id': final_product.id,
                    'code': final_product.code,
                    'name': final_product.name,
                    'description': final_product.description,
                    'category': {
                        'id': final_product.category.id,
                        'name': final_product.category.name,
                    },
                    'unit_cost': final_product.total_cost,
                    'is_final': True,
                    'has_colors': final_product.has_colors,
                    'colors': final_product.get_colors(),
                    'compositions': final_product.get_compositions(),
                }
            else:
                return Response(
                    {
                        'status': 'ERROR',
                        'msg': 'El producto no existe',
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(
                {
                    'status': 'OK',
                    'msg': 'Detalle del producto',
                    'data': product_data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    'status': 'ERROR',
                    'msg': 'Ocurrió un error al obtener el detalle del producto',
                    'detail': str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, product_id):
        """
        Actualiza un producto primario o final.
        Args:
            product_type: "primary" o "final".
            product_id: ID del producto a actualizar.
        """
        try:
            data = request.data
            
            code = data.get('code')
            name = data.get('name')
            description = data.get('description')
            stock = data.get('stock')
            unit_cost = data.get('unit_cost')
            category_id = data.get('category')
            is_product_final = data.get('is_product_final', False)
            has_colors = data.get('has_colors', False)
            compositions = data.get('compositions', [])
            colors = data.get('colors', [])
            
            # Validar tipo de producto
            product_type = "final" if is_product_final else "primary"

            if product_type not in ["primary", "final"]:
                return Response(
                    {'status': 'ERROR', 'msg': 'Tipo de producto inválido. Debe ser "primary" o "final".'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Validar datos básicos
            if not all([code, name, unit_cost]):
                return Response(
                    {'status': 'ERROR', 'msg': 'Faltan datos requeridos: "code", "name" o "unit_cost".'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Obtener y validar el producto
            model = PrimaryProduct if product_type == "primary" else FinalProduct
            try:
                product = model.objects.get(id=product_id)
            except model.DoesNotExist:
                return Response(
                    {'status': 'ERROR', 'msg': f'El producto con ID {product_id} no existe.'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Validar categoría, si se envía
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
                # Actualizar datos principales del producto
                product.code = code
                product.name = name
                product.description = description
                product.unit_cost = unit_cost if product_type == "primary" else product.total_cost
                product.category = category
                product.has_colors = has_colors
                product.save()

                # Actualizar colores
                if has_colors:
                    if colors:
                        # Eliminar colores existentes y agregar los nuevos
                        ProductColor.objects.filter(
                            primary_product=product if product_type == "primary" else None,
                            final_product=product if product_type == "final" else None,
                        ).delete()

                        for color in colors:
                            name_color = color.get('name_color')
                            hex_code = color.get('hex_code')
                            color_stock = color.get('stock')
                            if not all([name_color, hex_code, color_stock]):
                                raise ValueError('Cada color debe incluir "name_color", "hex_code" y "stock".')

                            ProductColor.objects.create(
                                primary_product=product if product_type == "primary" else None,
                                final_product=product if product_type == "final" else None,
                                color=name_color,
                                hex_code=hex_code,
                                stock=color_stock
                            )
                    else:
                        raise ValueError('Se indicó que el producto tiene colores, pero no se proporcionaron colores.')
                else:
                    # Si no tiene colores, asegurarse de que existe un color neutro
                    ProductColor.objects.filter(
                        primary_product=product if product_type == "primary" else None,
                        final_product=product if product_type == "final" else None,
                    ).delete()
                    ProductColor.objects.create(
                        primary_product=product if product_type == "primary" else None,
                        final_product=product if product_type == "final" else None,
                        color='Neutral',
                        hex_code='#FFFFFF',
                        stock=stock or 0
                    )

                # Actualizar composiciones (solo para productos finales)
                if product_type == "final":
                    if compositions:
                        # Eliminar composiciones existentes y agregar las nuevas
                        FinalProductComposition.objects.filter(final_product=product).delete()
                        for comp in compositions:
                            primary_product_id = comp.get('id')
                            quantity = comp.get('quantity')
                            if not primary_product_id or not quantity or quantity <= 0:
                                raise ValueError(f'Cada composición debe incluir "id" válido y "quantity" mayor a 0.')

                            try:
                                primary_product = PrimaryProduct.objects.get(id=primary_product_id)
                            except PrimaryProduct.DoesNotExist:
                                raise ValueError(f'El producto primario con ID {primary_product_id} no existe.')

                            FinalProductComposition.objects.create(
                                final_product=product,
                                primary_product=primary_product,
                                quantity=quantity,
                            )

            return Response(
                {'status': 'OK', 'msg': f'{product_type.capitalize()} product actualizado correctamente.'},
                status=status.HTTP_200_OK
            )

        except ValueError as ve:
            return Response(
                {'status': 'ERROR', 'msg': str(ve)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'status': 'ERROR', 'msg': 'Ocurrió un error al actualizar el producto.', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        