from django.test import TestCase
from django.contrib.auth.models import User
from .models import Supplier, Product, Inventory
from rest_framework.test import APIClient
from rest_framework import status
import csv
from io import StringIO
from django.core.files.uploadedfile import SimpleUploadedFile

class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.supplier = Supplier.objects.create(name='Test Supplier', contact_info='123-456-7890', user=self.user)
        self.product = Product.objects.create(name='Test Product', description='Test Description', price=10.0, supplier=self.supplier, user=self.user)
        self.inventory = Inventory.objects.create(product=self.product, quantity=100, user=self.user)

    def test_supplier_creation(self):
        self.assertEqual(self.supplier.name, 'Test Supplier')
        self.assertEqual(self.supplier.user.email, 'test@example.com')

    def test_product_creation(self):
        self.assertEqual(self.product.name, 'Test Product')
        self.assertEqual(self.product.supplier.name, 'Test Supplier')

    def test_inventory_creation(self):
        self.assertEqual(self.inventory.quantity, 100)
        self.assertEqual(self.inventory.product.name, 'Test Product')




class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser1', email='test1@example.com', password='testpass123')

    def test_user_registration(self):
        data = {
            'email': 'newuser@example.com',
            'name': 'New User',
            'password': 'newpass123'
        }
        response = self.client.post('/api/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    def test_user_login(self):
        
        data = {
            'email': 'test1@example.com',
            'password': 'testpass123',
            'username':'testuser1'
        }
        response = self.client.post('/api/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_register_user_missing_fields(self):
        data = {
            'email': 'newuser@example.com',
            'name': 'New User',
            # Missing password
        }
        response = self.client.post('/api/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_register_user_existing_email(self):
        User.objects.create_user(username='existing@example.com', email='existing@example.com', password='testpass123')
        data = {
            'email': 'existing@example.com',
            'name': 'Existing User',
            'password': 'newpass123'
        }
        response = self.client.post('/api/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class ProductTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser2', email='test2@example.com', password='testpass123')
        self.supplier = Supplier.objects.create(name='Test Supplier', contact_info='123-456-7890', user=self.user)
        self.product = Product.objects.create(name='Test Product', description='Test Description', price=10.0, supplier=self.supplier, user=self.user)
        self.client.force_authenticate(user=self.user)

    def test_list_products(self):
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_product(self):
        data = {
            'name': 'New Product',
            'description': 'New Description',
            'price': 20.0,
            'supplier': self.supplier.id
        }
        response = self.client.post('/api/products/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)

    def test_update_product(self):
        data = {
            'name': 'Updated Product',
            'description': 'Updated Description',
            'price': 30.0,
            'supplier': self.supplier.id
        }
        response = self.client.put(f'/api/products/{self.product.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Updated Product')

    def test_delete_product(self):
        response = self.client.delete(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)


    def test_create_product_invalid_data(self):
        data = {
            'name': '',  # Invalid: empty name
            'description': 'New Description',
            'price': 20.0,
            'supplier': self.supplier.id
        }
        response = self.client.post('/api/products/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_product_unauthorized(self):
        another_user = User.objects.create_user(username='anotheruser', email='another@example.com', password='testpass123')
        self.client.force_authenticate(user=another_user)
        data = {
            'name': 'Updated Product',
            'description': 'Updated Description',
            'price': 30.0,
            'supplier': self.supplier.id
        }
        response = self.client.put(f'/api/products/{self.product.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class SupplierViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser3', email='test3@example.com', password='testpass123')
        self.supplier = Supplier.objects.create(name='Test Supplier', contact_info='123-456-7890', user=self.user)
        self.client.force_authenticate(user=self.user)

    def test_create_supplier_invalid_data(self):
        data = {
            'name': '',  # Invalid: empty name
            'contact_info': '123-456-7890'
        }
        response = self.client.post('/api/suppliers/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_supplier_unauthorized(self):
        another_user = User.objects.create_user(username='anotheruser', email='another@example.com', password='testpass123')
        self.client.force_authenticate(user=another_user)
        data = {
            'name': 'Updated Supplier',
            'contact_info': '987-654-3210'
        }
        response = self.client.put(f'/api/suppliers/{self.supplier.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class InventoryViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser4', email='test4@example.com', password='testpass123')
        self.supplier = Supplier.objects.create(name='Test Supplier', contact_info='123-456-7890', user=self.user)
        self.product = Product.objects.create(name='Test Product', description='Test Description', price=10.0, supplier=self.supplier, user=self.user)
        self.inventory = Inventory.objects.create(product=self.product, quantity=100, user=self.user)
        self.client.force_authenticate(user=self.user)

    def test_create_inventory_invalid_data(self):
        data = {
            'product': self.product.id,
            'quantity': -10  # Invalid: negative quantity
        }
        response = self.client.post('/api/inventory/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_inventory_unauthorized(self):
        another_user = User.objects.create_user(username='anotheruser', email='another@example.com', password='testpass123')
        self.client.force_authenticate(user=another_user)
        data = {
            'product': self.product.id,
            'quantity': 200
        }
        response = self.client.put(f'/api/inventory/{self.inventory.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)




class CSVUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser5', email='test5@example.com', password='testpass123')
        self.client.force_authenticate(user=self.user)

    def test_csv_upload(self):
        csv_data = "name,description,price,supplier\nTest Product,Test Description,10.0,Test Supplier"
        csv_file = SimpleUploadedFile(
            name="test.csv",
            content=csv_data.encode('utf-8'),
            content_type="text/csv"
        )
        response = self.client.post('/api/upload-csv/', {'file': csv_file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_invalid_csv_upload(self):
        csv_data = "invalid,data\n1,2,3"
        csv_file = StringIO(csv_data)
        response = self.client.post('/api/upload-csv/', {'file': csv_file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_csv_upload_missing_file(self):
        response = self.client.post('/api/upload-csv/', {}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

class ReportTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser6', email='test6@example.com', password='testpass123')
        self.client.force_authenticate(user=self.user)

    def test_generate_report(self):
        response = self.client.post('/api/generate-report/')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

class TokenObtainPairViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_login_invalid_credentials(self):
        self.user = User.objects.create_user(username='testuser7', email='test7@example.com', password='testpass123')
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post('/api/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class TokenRefreshViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser8', email='test8@example.com', password='testpass123')
        
        login_response = self.client.post('/api/login/', {'username':'testuser8', 'email': 'test8@example.com', 'password': 'testpass123'}, format='json')
        
        self.token = login_response.data.get('refresh')  # Use the refresh token for token refresh

    def test_token_refresh(self):
        
        response = self.client.post('/api/login/refresh/', {'refresh':  self.token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

class CustomFiltersAndPaginationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser9', email='test9@example.com', password='testpass123')
        self.supplier = Supplier.objects.create(name='Test Supplier', contact_info='123-456-7890', user=self.user)
        self.product1 = Product.objects.create(name='Product 1', description='Description 1', price=10.0, supplier=self.supplier, user=self.user)
        self.product2 = Product.objects.create(name='Product 2', description='Description 2', price=20.0, supplier=self.supplier, user=self.user)
        self.client.force_authenticate(user=self.user)

    def test_product_filter(self):
        response = self.client.get('/api/products/?name=Product 1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['name'], 'Product 1')

    def test_product_pagination(self):
        response = self.client.get('/api/products/?page=1&page_size=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)