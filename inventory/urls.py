from django.urls import path
from rest_framework.documentation import include_docs_urls
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import ProductViewSet, SupplierViewSet, InventoryViewSet, RegisterView, CSVUploadView, GenerateReportView
# from rest_framework.schemas import get_schema_view
# from rest_framework.renderers import JSONOpenAPIRenderer
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework_simplejwt.authentication import JWTAuthentication


# Initialize urlpatterns
urlpatterns = []

# Add schema view for API documentation
# schema_view = get_schema_view(
#     title="Inventory API",
#     description="API for managing inventory",
#     version="1.0.0",
#     public=True,
#     renderer_classes=[JSONOpenAPIRenderer],
# )


schema_view = get_schema_view(
    openapi.Info(
        title="Inventory API",
        default_version="v1",
        description="API for managing inventory",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=(JWTAuthentication,),
)

# Append routes to urlpatterns
urlpatterns += [
    # path('docs/', schema_view, name='schema_view'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('products/', ProductViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('products/<int:pk>/', ProductViewSet.as_view({'put': 'update', 'delete': 'destroy'})),
    path('suppliers/', SupplierViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('suppliers/<int:pk>/', SupplierViewSet.as_view({'put': 'update', 'delete': 'destroy'})),
    path('inventory/', InventoryViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('inventory/<int:pk>/', InventoryViewSet.as_view({'put': 'update', 'delete': 'destroy'})),
    path('upload-csv/', CSVUploadView.as_view(), name='upload_csv'),
    path('generate-report/', GenerateReportView.as_view(), name='generate_report'),
]