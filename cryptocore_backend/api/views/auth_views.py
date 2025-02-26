from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, get_user_model
from django.conf import settings

# 註冊
@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'password'],
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description="使用者名稱"),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description="使用者密碼"),
            'first_name': openapi.Schema(type=openapi.TYPE_STRING, description="名"),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING, description="姓"),
        },
    ),
    responses={201: "User registered successfully", 400: "Username already exists or bad request"}
)
@api_view(['POST'])
def register(request):
    """
    使用者註冊API
    """
    data = request.data
    username = data.get('username')
    password = data.get('password')
    first_name = data.get('first_name', '')
    last_name = data.get('last_name', '')
    
    if not username or not password:
        return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        
        # 確認使用者是否已存在
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 創建使用者
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        print("Error while connecting to PostgreSQL", e)
        return Response({'error': f'Failed to register user, resons: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# 登入

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'password'],
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description="使用者名稱"),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description="使用者密碼"),
        },
    ),
    responses={200: "JWT Token", 401: "Invalid credentials"}
)
@api_view(['POST'])
def login(request):
    """
    使用者登入 API，回傳 JWT Token
    """
    data = request.data
    username = data.get('username')
    password = data.get('password')

    # 檢查必要參數
    if not username or not password:
        return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 使用 Django 的 authenticate() 來驗證
        user = authenticate(username=username, password=password)

        if user is None:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        # 產生 JWT Token
        refresh = RefreshToken.for_user(user)

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 登出
@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['refresh_token'],
        properties={
            'refresh_token': openapi.Schema(type=openapi.TYPE_STRING, description="JWT Refresh Token"),
        },
    ),
    responses={
        200: "User logged out successfully",
        400: "Refresh token is required",
        401: "Invalid or expired token"
    }
)
@api_view(['POST'])
def logout(request):
    """
    使用者登出 API
    """
    refresh_token = request.data.get('refresh_token')
    
    if not refresh_token:
        return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 確認 Refresh Token 是否有效
        token = RefreshToken(refresh_token)
        token.verify()

        # 確認是否啟用黑名單功能
        if "rest_framework_simplejwt.token_blacklist" in settings.INSTALLED_APPS:
            token.blacklist()
    
        return Response({'message': 'User logged out successfully'}, status=status.HTTP_200_OK)
    except TokenError:
        return Response({'error': 'Invalid or expired token'}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)