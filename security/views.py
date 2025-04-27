from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenVerifySerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import User
import re
from django.conf import settings
from .models import CustomerUser, VerificationCode, PasswordResetRequest
from django.db import transaction
import random
import string
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenVerifySerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import User
import re
from django.conf import settings
from django.utils.text import capfirst
from typing import Protocol
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from rest_framework.permissions import AllowAny
from django.http import HttpResponse
import random
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
import datetime
from django.core.exceptions import ObjectDoesNotExist

# Vista para autenticar usuarios y generar tokens
class UserLoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        username = request.data.get('username', None)
        password = request.data.get('password', None)

        # Validación de campos requeridos
        errors = {}
        if username is None:
            errors["username"] = "Campo requerido"
        if password is None:
            errors["password"] = "Campo requerido"

        # Manejo de errores de validación
        if len(errors.keys()) > 0:
            return Response({"detail": errors}, status=status.HTTP_400_BAD_REQUEST)

        # Autenticar al usuario
        user = authenticate(username=username, password=password)
        if user is None:
            return Response({"detail": "El usuario o contraseña son incorrectos"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            # Generar tokens de acceso y actualización
            refresh = RefreshToken.for_user(user)

            model = CustomerUser.objects.select_related('user').get(email=username)
            
            if model.is_active == False:
                return Response({"detail": "Usuario no verificado", "verify": False}, status=status.HTTP_401_UNAUTHORIZED)
            
            if model:
                user_info = {
                    'id': model.uuid if model and model.uuid else "",
                    'name': model.complete_name(),
                    'email': model.email,
                    'phone': model.phone,
                    'is_trial': model.is_trial,
                    'rol': 'ADM'
                }
                # Respuesta con confirmación de autenticación y tokens
                return Response({
                    'confirmation': 'Autenticación exitosa',
                    'user': user_info,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            else:
                return Response({"detail": "Empleado no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        except CustomerUser.DoesNotExist:
            return Response({"detail": "Empleado no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

def send_verification_email(email, code, name, type='verify'):
    if type == 'verify':
        subject = 'Verificación de cuenta'
        message = render_to_string("template_verify_user.html", {
            'user' : name,
            'random_number': code
        })
    else:
        subject = 'Recuperación de contraseña'
        message = render_to_string("template_reset_password.html", {
            'user' : name,
            'random_number': code
        })

    email = EmailMessage(subject, message, to=[email])
    email.content_subtype = "html"
    email.send()

class UserRegisterView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        name = request.data.get('name')
        last_name = request.data.get('last_name')
        phone = request.data.get('phone')
        password = request.data.get('password')
        email = request.data.get('email')

        # Validaciones de campos requeridos
        required_fields = {
            'password': 'contraseña',
            'email': 'email',
            'name': 'nombre',
            'last_name': 'apellido',
            'phone': 'teléfono'
        }
        
        for field, field_name in required_fields.items():
            if not locals()[field]:
                return Response(
                    {"status": "ERROR", "msg": f'El campo {field_name} es requerido'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return Response(
                {"status": "ERROR", "msg": 'El email no tiene un formato válido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                # Verificar si existe un usuario no verificado
                existing_user = CustomerUser.objects.filter(email=email).first()
                if existing_user:
                    if existing_user.is_active == False:
                        # Actualizar datos del usuario existente
                        return Response(
                            {"status": "ERROR", "msg": 'Existe un usuario con el email ingresado, pero no está verificado', 'verify': False},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    else:
                        return Response(
                            {"status": "ERROR", "msg": 'El email ya está registrado, intente con otro o inicie sesión'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                else:
                    # Crear nuevo usuario
                    user = User.objects.create_user(
                        username=email,
                        password=password,
                        email=email,
                    )

                    customer_user = CustomerUser.objects.create(
                        name=name,
                        last_name=last_name,
                        phone=phone,
                        email=email,
                        user=user,
                        is_active=False
                    )

                    # Generar y guardar código de verificación
                    code = generate_verification_code()

                    VerificationCode.objects.update_or_create(
                        customer_user=customer_user,
                        defaults={'code': code}
                    )

                    # Enviar email de verificación
                    send_verification_email(email, code, f'{name}, {last_name}')

                    # Generar token para el proceso de verificación usando el User de Django
                    refresh = RefreshToken.for_user(user)
                    
                    return Response({
                        "status": "OK",
                        "msg": "Usuario creado exitosamente. Por favor verifica tu email.",
                        "token": str(refresh.access_token)
                    }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"status": "ERROR", "msg": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
# Vista para verificar tokens de acceso
class VerifyView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = TokenVerifySerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            access_token_obj = AccessToken(request.data['token'])
            user_id = access_token_obj['user_id']
            user = User.objects.get(id=user_id)

            model = CustomerUser.objects.select_related('user').get(user=user)
                
            if model:
                user_info = {
                    'id': model.uuid if model and model.uuid else "",
                    'name': model.complete_name(),
                    'email': model.email,
                    'phone': model.phone,
                    'is_trial': model.is_trial,
                    'rol': 'ADM'
                }
                # Respuesta con confirmación de autenticación y tokens
            return Response({
                'user': user_info,
                'access': request.data['token'],
            })
        except TokenError as e:
            return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

class VerifyCodeView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        verification_token = request.data.get('token')
        code = request.data.get('code')

        if not verification_token or not code:
            return Response({
                "status": "ERROR",
                "msg": "Token de verificación y código son requeridos"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Decodificar token y obtener usuario
            access_token_obj = AccessToken(verification_token)
            user_id = access_token_obj['user_id']
            user = User.objects.get(id=user_id)
            customer_user = CustomerUser.objects.get(user=user)

            # Verificar código
            verification = VerificationCode.objects.filter(customer_user=customer_user).first()
            if not verification:
                return Response({
                    "status": "ERROR",
                    "msg": "Código de verificación no encontrado"
                }, status=status.HTTP_404_NOT_FOUND)

            if verification.is_expired:
                return Response({
                    "status": "ERROR",
                    "msg": "El código ha expirado, solicita uno nuevo"
                }, status=status.HTTP_400_BAD_REQUEST)

            if verification.code != code:
                return Response({
                    "status": "ERROR",
                    "msg": "Código incorrecto"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Activar usuario
            customer_user.is_active = True
            customer_user.save()

            # Eliminar código de verificación
            verification.delete()

            return Response({
                "status": "OK",
                "msg": "Usuario verificado exitosamente"
            })

        except TokenError:
            return Response({
                "status": "ERROR",
                "msg": "Token inválido"
            }, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({
                "status": "ERROR",
                "msg": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ResendVerificationCodeView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        verification_token = request.data.get('token')

        if not verification_token:
            return Response({
                "status": "ERROR",
                "msg": "Token de verificación es requerido"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Decodificar token y obtener usuario
            access_token_obj = AccessToken(verification_token)
            user_id = access_token_obj['user_id']
            user = User.objects.get(id=user_id)
            customer_user = CustomerUser.objects.get(user=user)

            if customer_user.is_active:
                return Response({
                    "status": "ERROR",
                    "msg": "El usuario ya está verificado"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Generar nuevo código
            code = generate_verification_code()
            VerificationCode.objects.update_or_create(
                customer_user=customer_user,
                defaults={'code': code}
            )

            # Reenviar email
            send_verification_email(customer_user.email, code, f'{customer_user.name}, {customer_user.last_name}')

            return Response({
                "status": "OK",
                "msg": "Código de verificación reenviado"
            })

        except TokenError:
            return Response({
                "status": "ERROR",
                "msg": "Token inválido"
            }, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({
                "status": "ERROR",
                "msg": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GenerateVerificationTokenView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({
                "status": "ERROR",
                "msg": "El correo electrónico es requerido"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:

            user = User.objects.get(email=email)
            customer_user = CustomerUser.objects.get(user=user)

            if customer_user.is_active:
                return Response({
                    "status": "ERROR",
                    "msg": "El usuario ya está verificado"
                }, status=status.HTTP_400_BAD_REQUEST)

            refresh = RefreshToken.for_user(user)
            verification_token = str(refresh.access_token)

            code = generate_verification_code()
            VerificationCode.objects.update_or_create(
                customer_user=customer_user,
                defaults={'code': code}
            )

            send_verification_email(
                customer_user.email, 
                code, 
                f'{customer_user.name}, {customer_user.last_name}'
            )

            return Response({
                "status": "OK",
                "msg": "Token generado exitosamente",
                "data": {
                    "token": verification_token,
                }
            })

        except ObjectDoesNotExist:
            return Response({
                "status": "ERROR",
                "msg": "Usuario no encontrado"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "status": "ERROR",
                "msg": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PasswordResetRequestView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({
                "status": "ERROR",
                "msg": "El correo electrónico es requerido"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            customer_user = CustomerUser.objects.get(user=user)

            code = generate_verification_code()

            refresh = RefreshToken.for_user(user)
            verification_token = str(refresh.access_token)

            PasswordResetRequest.objects.update_or_create(
                customer_user=customer_user,
                defaults={'code': code}
            )

            send_verification_email(
                customer_user.email, 
                code, 
                f'{customer_user.name}, {customer_user.last_name}',
                type='reset'
            )

            return Response({
                "status": "OK",
                "msg": "Código de recuperación enviado exitosamente",
                "data": {
                    "token": verification_token,
                }
            })

        except ObjectDoesNotExist:
            return Response({
                "status": "ERROR",
                "msg": "Usuario no encontrado"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "status": "ERROR",
                "msg": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class PasswordResetView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        verification_token = request.data.get('token')
        code = request.data.get('code')

        if not verification_token or not code:
            return Response({
                "status": "ERROR",
                "msg": "Correo electrónico y código son requeridos"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            access_token_obj = AccessToken(verification_token)
            user_id = access_token_obj['user_id']
            user = User.objects.get(id=user_id)
            customer_user = CustomerUser.objects.get(user=user)

            reset_request = PasswordResetRequest.objects.filter(customer_user=customer_user).first()
            if not reset_request:
                return Response({
                    "status": "ERROR",
                    "msg": "No se ha solicitado un cambio de contraseña"
                }, status=status.HTTP_404_NOT_FOUND)

            if reset_request.is_expired:
                return Response({
                    "status": "ERROR",
                    "msg": "El código ha expirado, solicita uno nuevo"
                }, status=status.HTTP_400_BAD_REQUEST)

            if reset_request.code != code:
                return Response({
                    "status": "ERROR",
                    "msg": "Código incorrecto"
                }, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "status": "OK",
                "msg": "Codigo correcto"
            })
        
        except ObjectDoesNotExist:
            return Response({
                "status": "ERROR",
                "msg": "Usuario no encontrado"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "status": "ERROR",
                "msg": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PasswordChangeCodeResendView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        verification_token = request.data.get('token')

        if not verification_token:
            return Response({
                "status": "ERROR",
                "msg": "Token de verificación es requerido"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            access_token_obj = AccessToken(verification_token)
            user_id = access_token_obj['user_id']
            user = User.objects.get(id=user_id)
            customer_user = CustomerUser.objects.get(user=user)

            reset_request = PasswordResetRequest.objects.filter(customer_user=customer_user).first()

            if reset_request.changed:
                return Response({
                    "status": "ERROR",
                    "msg": "La contraseña ya ha sido cambiada"
                }, status=status.HTTP_400_BAD_REQUEST)

            code = generate_verification_code()
            reset_request.code = code
            reset_request.save()

            send_verification_email(
                customer_user.email, 
                code, 
                f'{customer_user.name}, {customer_user.last_name}',
                type='reset'
            )

            return Response({
                "status": "OK",
                "msg": "Código de recuperación reenviado exitosamente"
            })

        except ObjectDoesNotExist:
            return Response({
                "status": "ERROR",
                "msg": "Usuario no encontrado"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "status": "ERROR",
                "msg": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PasswordChangeView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        token = request.data.get('token')
        password = request.data.get('password')

        if not token or not password:
            return Response({
                "status": "ERROR",
                "msg": "Correo electrónico y contraseña son requeridos"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            access_token_obj = AccessToken(token)
            user_id = access_token_obj['user_id']
            user = User.objects.get(id=user_id)
            customer_user = CustomerUser.objects.get(user=user)

            reset_request = PasswordResetRequest.objects.filter(customer_user=customer_user).first()
            if not reset_request:
                return Response({
                    "status": "ERROR",
                    "msg": "No se ha solicitado un cambio de contraseña"
                }, status=status.HTTP_404_NOT_FOUND)

            user.set_password(password)
            user.save()

            reset_request.changed = True
            reset_request.save()

            return Response({
                "status": "OK",
                "msg": "Contraseña cambiada exitosamente"
            })
        
        except ObjectDoesNotExist:
            return Response({
                "status": "ERROR",
                "msg": "Usuario no encontrado"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "status": "ERROR",
                "msg": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)