from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny

from .serializers import UserRegistrationSerializer
from .manager import UserManager
from .services import UserRoleServiceImpl
from django.contrib.auth import login

class RegisterView(GenericAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            manager = UserManager(role_service=UserRoleServiceImpl())
            data = serializer.validated_data

            result = manager.register_user(
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
            )

            return Response({
                'message': 'Inscription réussie',
                'user': {
                    'email': result['user']['email'],
                    'first_name': result['user']['first_name'],
                    'last_name': result['user']['last_name']
                },
            }, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de l\'inscription {e}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
# class LoginView(GenericAPIView):
#     """User login view using session authentication"""
#     serializer_class = UserLoginSerializer
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = self.get_serializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             manager = UserManager(role_service=UserRoleServiceImpl())
#             data = serializer.validated_data

#             user = manager.authenticate(
#                 email=data['email'],
#                 password=data['password']
#             )

#             if user is None:
#                 return Response(
#                     {'error': 'Email ou mot de passe invalide'},
#                     status=status.HTTP_401_UNAUTHORIZED
#                 )

#             # Log the user in (create a session)
#             login(request, user)

#             return Response({
#                 'message': 'Connexion réussie',
#                 'user': {
#                     'email': user.email,
#                     'first_name': user.first_name,
#                     'last_name': user.last_name
#                 },
#             }, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response(
#                 {'error': f'Erreur lors de la connexion {e}'},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
