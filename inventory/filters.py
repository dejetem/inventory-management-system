from rest_framework.pagination import PageNumberPagination
from django_filters import rest_framework as filters
from .models import Product, Supplier, Inventory


class ProductFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')  # Case-insensitive partial match

    class Meta:
        model = Product
        fields = ['name', 'price']  # Fields to filter by

class SupplierFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')  # Case-insensitive partial match

    class Meta:
        model = Supplier
        fields = ['name']  # Fields to filter by

class InventoryFilter(filters.FilterSet):
    quantity = filters.NumberFilter(lookup_expr='exact')  # Exact match for quantity

    class Meta:
        model = Inventory
        fields = ['quantity']  # Fields to filter by

class CustomPagination(PageNumberPagination):
    page_size = 10  # Items per page
    page_size_query_param = 'page_size'  # Allow client to override page size
    max_page_size = 100  # Maximum page size