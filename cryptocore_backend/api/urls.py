from django.urls import path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from .views.views import get_crypto_price
from .views.auth_views import register, login, logout

schema_view = get_schema_view(
    openapi.Info(
        title="Cryptocore API",
        default_version='v1',
        description="API for fetching cryptocurrency prices",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[],
)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc-ui'),
    path('price/<str:symbol>/', get_crypto_price, name="get_crypto_price"),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),  # 登出 API
]