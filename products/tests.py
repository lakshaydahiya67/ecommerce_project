from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from decimal import Decimal
import json
from .models import Product, UserInteraction
from .cart_utils import (
    get_cart, add_to_cart, remove_from_cart, update_cart_quantity,
    get_cart_items, clear_cart, get_cart_count
)


class ProductModelTestCase(TestCase):
    """Test case for Product model"""
    
    def setUp(self):
        """Set up test data"""
        self.product_data = {
            'name': 'Test Laptop',
            'description': 'A high-performance laptop for testing',
            'price': Decimal('999.99'),
            'category': 'Electronics'
        }
    
    def test_product_creation(self):
        """Test creating a product with valid data"""
        product = Product.objects.create(**self.product_data)
        
        self.assertEqual(product.name, 'Test Laptop')
        self.assertEqual(product.description, 'A high-performance laptop for testing')
        self.assertEqual(product.price, Decimal('999.99'))
        self.assertEqual(product.category, 'Electronics')
        self.assertIsNotNone(product.created_at)
    
    def test_product_string_representation(self):
        """Test product string representation"""
        product = Product.objects.create(**self.product_data)
        self.assertEqual(str(product), 'Test Laptop')


class UserInteractionModelTestCase(TestCase):
    """Test case for UserInteraction model"""
    
    def setUp(self):
        """Set up test data"""
        self.product = Product.objects.create(
            name='Test Product',
            description='Test description',
            price=Decimal('19.99'),
            category='Electronics'
        )
        self.session_key = 'test_session_key_123'
    
    def test_user_interaction_creation(self):
        """Test creating user interactions with session key"""
        interaction = UserInteraction.objects.create(
            session_key=self.session_key,
            product=self.product,
            interaction_type='view'
        )
        
        self.assertEqual(interaction.session_key, self.session_key)
        self.assertEqual(interaction.product, self.product)
        self.assertEqual(interaction.interaction_type, 'view')
        self.assertIsNotNone(interaction.timestamp)
    
    def test_user_interaction_string_representation(self):
        """Test user interaction string representation"""
        interaction = UserInteraction.objects.create(
            session_key=self.session_key,
            product=self.product,
            interaction_type='like'
        )
        expected_str = f"{self.session_key[:8]}... like {self.product.name}"
        self.assertEqual(str(interaction), expected_str)
    
    def test_user_interaction_choices(self):
        """Test all valid interaction types"""
        valid_types = ['view', 'like', 'dislike', 'purchase']
        
        for interaction_type in valid_types:
            interaction = UserInteraction.objects.create(
                session_key=f"{self.session_key}_{interaction_type}",
                product=self.product,
                interaction_type=interaction_type
            )
            self.assertEqual(interaction.interaction_type, interaction_type)


class SessionCartUtilsTestCase(TestCase):
    """Test case for session-based cart utility functions"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        self.product1 = Product.objects.create(
            name='Test Product 1',
            description='Test description 1',
            price=Decimal('19.99'),
            category='Electronics'
        )
        self.product2 = Product.objects.create(
            name='Test Product 2',
            description='Test description 2',
            price=Decimal('29.99'),
            category='Electronics'
        )
    
    def create_request_with_session(self):
        """Create a request with session support"""
        request = self.factory.get('/')
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        return request
    
    def test_get_cart_empty(self):
        """Test getting empty cart"""
        request = self.create_request_with_session()
        cart = get_cart(request)
        self.assertEqual(cart, {})
    
    def test_add_to_cart(self):
        """Test adding products to cart"""
        request = self.create_request_with_session()
        
        # Add first product
        success = add_to_cart(request, self.product1.id, 2)
        self.assertTrue(success)
        
        cart = get_cart(request)
        self.assertEqual(cart[str(self.product1.id)], 2)
        
        # Add same product again (should update quantity)
        success = add_to_cart(request, self.product1.id, 3)
        self.assertTrue(success)
        
        cart = get_cart(request)
        self.assertEqual(cart[str(self.product1.id)], 5)
    
    def test_add_to_cart_invalid_product(self):
        """Test adding non-existent product to cart"""
        request = self.create_request_with_session()
        success = add_to_cart(request, 99999, 1)
        self.assertFalse(success)
    
    def test_remove_from_cart(self):
        """Test removing products from cart"""
        request = self.create_request_with_session()
        
        # Add product first
        add_to_cart(request, self.product1.id, 2)
        
        # Remove product
        success = remove_from_cart(request, self.product1.id)
        self.assertTrue(success)
        
        cart = get_cart(request)
        self.assertNotIn(str(self.product1.id), cart)
    
    def test_remove_from_cart_not_in_cart(self):
        """Test removing product that's not in cart"""
        request = self.create_request_with_session()
        success = remove_from_cart(request, self.product1.id)
        self.assertFalse(success)
    
    def test_update_cart_quantity(self):
        """Test updating cart item quantities"""
        request = self.create_request_with_session()
        
        # Add product first
        add_to_cart(request, self.product1.id, 2)
        
        # Update quantity
        success = update_cart_quantity(request, self.product1.id, 5)
        self.assertTrue(success)
        
        cart = get_cart(request)
        self.assertEqual(cart[str(self.product1.id)], 5)
        
        # Update to zero (should remove)
        success = update_cart_quantity(request, self.product1.id, 0)
        self.assertTrue(success)
        
        cart = get_cart(request)
        self.assertNotIn(str(self.product1.id), cart)
    
    def test_get_cart_items(self):
        """Test getting detailed cart items"""
        request = self.create_request_with_session()
        
        # Add products to cart
        add_to_cart(request, self.product1.id, 2)
        add_to_cart(request, self.product2.id, 1)
        
        cart_data = get_cart_items(request)
        
        self.assertEqual(len(cart_data['cart_items']), 2)
        self.assertEqual(cart_data['item_count'], 3)
        
        expected_total = (self.product1.price * 2) + (self.product2.price * 1)
        self.assertEqual(cart_data['cart_total'], expected_total)
    
    def test_clear_cart(self):
        """Test clearing cart"""
        request = self.create_request_with_session()
        
        # Add products to cart
        add_to_cart(request, self.product1.id, 2)
        add_to_cart(request, self.product2.id, 1)
        
        # Clear cart
        clear_cart(request)
        
        cart = get_cart(request)
        self.assertEqual(cart, {})
    
    def test_get_cart_count(self):
        """Test getting cart count"""
        request = self.create_request_with_session()
        
        # Empty cart
        count = get_cart_count(request)
        self.assertEqual(count, 0)
        
        # Add products
        add_to_cart(request, self.product1.id, 2)
        add_to_cart(request, self.product2.id, 3)
        
        count = get_cart_count(request)
        self.assertEqual(count, 5)


class SessionCartViewTestCase(TestCase):
    """Test case for session-based cart views"""
    
    def setUp(self):
        """Set up test data"""
        self.product1 = Product.objects.create(
            name='Test Product 1',
            description='Test description 1',
            price=Decimal('19.99'),
            category='Electronics'
        )
        self.product2 = Product.objects.create(
            name='Test Product 2',
            description='Test description 2',
            price=Decimal('29.99'),
            category='Electronics'
        )
        self.client = Client()
    
    def test_cart_view_empty(self):
        """Test cart view with empty cart"""
        response = self.client.get(reverse('products:cart'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your cart is empty')
        self.assertEqual(len(response.context['cart_items']), 0)
    
    def test_add_to_cart_view(self):
        """Test adding products to cart via view"""
        response = self.client.post(
            reverse('products:add_to_cart', args=[self.product1.id]),
            {'quantity': 3}
        )
        
        # Should redirect to cart
        self.assertEqual(response.status_code, 302)
        
        # Check cart view shows the item
        response = self.client.get(reverse('products:cart'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product1.name)
        self.assertEqual(len(response.context['cart_items']), 1)
        self.assertEqual(response.context['cart_items'][0]['quantity'], 3)
    
    def test_add_to_cart_ajax(self):
        """Test adding products to cart via AJAX"""
        response = self.client.post(
            reverse('products:add_to_cart', args=[self.product1.id]),
            {'quantity': 2},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['cart_count'], 2)
    
    def test_update_cart_view(self):
        """Test updating cart item quantities"""
        # Add item to cart first
        self.client.post(
            reverse('products:add_to_cart', args=[self.product1.id]),
            {'quantity': 2}
        )
        
        # Update quantity
        response = self.client.post(
            reverse('products:update_cart', args=[self.product1.id]),
            {'quantity': 5}
        )
        
        self.assertEqual(response.status_code, 302)
        
        # Check updated quantity
        response = self.client.get(reverse('products:cart'))
        self.assertEqual(response.context['cart_items'][0]['quantity'], 5)
    
    def test_remove_from_cart_view(self):
        """Test removing items from cart"""
        # Add item to cart first
        self.client.post(
            reverse('products:add_to_cart', args=[self.product1.id]),
            {'quantity': 2}
        )
        
        # Remove item
        response = self.client.post(
            reverse('products:remove_from_cart', args=[self.product1.id])
        )
        
        self.assertEqual(response.status_code, 302)
        
        # Check item was removed
        response = self.client.get(reverse('products:cart'))
        self.assertEqual(len(response.context['cart_items']), 0)
    
    def test_checkout_view_empty_cart(self):
        """Test checkout view with empty cart"""
        response = self.client.get(reverse('products:checkout'))
        
        # Should redirect to cart
        self.assertEqual(response.status_code, 302)
    
    def test_checkout_view_with_items(self):
        """Test checkout view with items in cart"""
        # Add items to cart
        self.client.post(
            reverse('products:add_to_cart', args=[self.product1.id]),
            {'quantity': 2}
        )
        
        response = self.client.get(reverse('products:checkout'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product1.name)
        self.assertEqual(len(response.context['cart_items']), 1)
    
    def test_checkout_post_valid_data(self):
        """Test checkout POST with valid data"""
        # Add items to cart
        self.client.post(
            reverse('products:add_to_cart', args=[self.product1.id]),
            {'quantity': 2}
        )
        
        checkout_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'address': '123 Main St'
        }
        
        response = self.client.post(reverse('products:checkout'), checkout_data)
        
        # Should redirect to confirmation
        self.assertEqual(response.status_code, 302)
        
        # Check cart was cleared
        response = self.client.get(reverse('products:cart'))
        self.assertEqual(len(response.context['cart_items']), 0)


class ProductViewTestCase(TestCase):
    """Test case for product views"""
    
    def setUp(self):
        """Set up test data"""
        self.product = Product.objects.create(
            name='Test Product',
            description='Test description',
            price=Decimal('19.99'),
            category='Electronics'
        )
        self.client = Client()
    
    def test_product_list_view(self):
        """Test product list view"""
        response = self.client.get(reverse('products:product_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        self.assertEqual(len(response.context['products']), 1)
    
    def test_product_detail_view(self):
        """Test product detail view"""
        response = self.client.get(
            reverse('products:product_detail', args=[self.product.id])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        self.assertContains(response, self.product.description)
        self.assertEqual(response.context['product'], self.product)
    
    def test_product_interaction_view(self):
        """Test product interaction (like/dislike) view"""
        response = self.client.post(
            reverse('products:product_interact', args=[self.product.id]),
            json.dumps({'interaction_type': 'like'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['interaction_type'], 'like')
        
        # Check interaction was recorded
        interactions = UserInteraction.objects.filter(
            product=self.product,
            interaction_type='like'
        )
        self.assertEqual(interactions.count(), 1)