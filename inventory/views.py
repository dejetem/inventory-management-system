import csv
from io import StringIO
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Product, Supplier, Inventory
from django_filters import rest_framework as filters
from .filters import CustomPagination,  ProductFilter , SupplierFilter, InventoryFilter
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .serializers import ProductSerializer, SupplierSerializer, InventorySerializer
from .tasks import process_csv, generate_inventory_report
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi







# Django’s built-in User model and DRF’s TokenObtainPairView for JWT authentication.
class RegisterView(APIView):
    """
    Register a new user.
    """
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='User email'),
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='User name'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='User password'),
            },
            required=['email', 'name', 'password']
        ),
        responses={
            201: "User registered successfully",
            400: "Invalid input",
        }
    )
    def post(self, request):
        """
        Register a new user with email, name, and password.
        """
        data = request.data
        email = data.get('email')
        name = data.get('name')
        password = data.get('password')

        if not email or not name or not password:
            return Response({"error": "Email, name, and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"error": "User with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create(
            username=email,
            email=email,
            first_name=name,
            password=make_password(password)
        )
        return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination # Add custom pagination
    filter_backends = [filters.DjangoFilterBackend]  # Add filter backend
    filterset_class = ProductFilter  # Add filterset

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)
    
    # @swagger_auto_schema(
    #     request_body=openapi.Schema(
    #         type=openapi.TYPE_OBJECT,
    #         properties={
    #             'name': openapi.Schema(type=openapi.TYPE_STRING),
    #             'description': openapi.Schema(type=openapi.TYPE_STRING),
    #             'price': openapi.Schema(type=openapi.TYPE_NUMBER),
    #             'supplier': openapi.Schema(type=openapi.TYPE_INTEGER),
    #         },
    #         required=['name', 'description', 'price', 'supplier']
    #     )
    # )
    # def create(self, request, *args, **kwargs):
    #     return super().create(request, *args, **kwargs)


    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SupplierViewSet(viewsets.ModelViewSet):
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination # Add custom pagination
    filter_backends = [filters.DjangoFilterBackend]  # Add filter backend
    filterset_class = SupplierFilter  # Add filterset

    def get_queryset(self):
        return Supplier.objects.filter(user=self.request.user)
    
    # @swagger_auto_schema(
    #     request_body=openapi.Schema(
    #         type=openapi.TYPE_OBJECT,
    #         properties={
    #             'name': openapi.Schema(type=openapi.TYPE_STRING),
    #             'contact_info': openapi.Schema(type=openapi.TYPE_STRING),
    #         },
    #         required=['name', 'contact_info']
    #     )
    # )
    # def create(self, request, *args, **kwargs):
    #     return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class InventoryViewSet(viewsets.ModelViewSet):
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination # Add custom pagination
    filter_backends = [filters.DjangoFilterBackend]  # Add filter backend
    filterset_class = InventoryFilter  # Add filterset

    def get_queryset(self):
        return Inventory.objects.filter(user=self.request.user)
    
    # @swagger_auto_schema(
    #     request_body=openapi.Schema(
    #         type=openapi.TYPE_OBJECT,
    #         properties={
    #             'product': openapi.Schema(type=openapi.TYPE_INTEGER),
    #             'quantity': openapi.Schema(type=openapi.TYPE_INTEGER),
    #         },
    #         required=['product', 'quantity']
    #     )
    # )
    # def create(self, request, *args, **kwargs):
    #     return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CSVUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate file type (CSV)
        if not file.name.endswith('.csv'):
            return Response({"error": "File must be a CSV"}, status=status.HTTP_400_BAD_REQUEST)

        # Read and validate CSV content
        try:
            file_data = file.read().decode('utf-8')
            reader = csv.DictReader(StringIO(file_data))
            required_columns = {'name', 'description', 'price', 'supplier'}
            if not required_columns.issubset(reader.fieldnames):
                return Response(
                    {"error": f"CSV must contain the following columns: {', '.join(required_columns)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response({"error": f"Invalid CSV file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Process the CSV file asynchronously
        process_csv.delay(file_data, request.user.email)
        return Response(
            {"message": "CSV upload is being processed. You will receive an email with the results."},
            status=status.HTTP_202_ACCEPTED
        )
    

class GenerateReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        generate_inventory_report.delay(request.user.email)
        return Response({"message": "Report generation started. You will receive an email with the report."}, status=status.HTTP_202_ACCEPTED)