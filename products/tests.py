from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from .models import Product, CartItem, UserInteraction


class CartFunctionalityTestCase(TestCase):
    """
    Test case for shopping cart functionality
    """
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test products
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
        
        # Create test client
        self.client = Client()
    
    def test_cart_model(self):
        """Test CartItem model functionality"""
        # Create cart item
        cart_item = CartItem.objects.create(
            user=self.user,
            product=self.product1,
            quantity=2
        )
        
        # Test string representation
        expected_str = f"{self.user.username} - {self.product1.name} (x2)"
        self.assertEqual(str(cart_item), expected_str)
        
        # Test total price calculation
        expected_total = self.product1.price * 2
        self.assertEqual(cart_item.get_total_price(), expected_total)
        
        # Test unique constraint
        with self.assertRaises(Exception):
            CartItem.objects.create(
                user=self.user,
                product=self.product1,
                quantity=1
            )
    
    def test_add_to_cart_view(self):
        """Test adding products to cart"""
        # Login user
        self.client.login(username='testuser', password='testpass123')
        
        # Add product to cart
        response = self.client.post(
            reverse('products:add_to_cart', args=[self.product1.id]),
            {'quantity': 3}
        )
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        
        # Check cart item was created
        cart_item = CartItem.objects.get(user=self.user, product=self.product1)
        self.assertEqual(cart_item.quantity, 3)
        
        # Add same product again (should update quantity)
        response = self.client.post(
            reverse('products:add_to_cart', args=[self.product1.id]),
            {'quantity': 2}
        )
        
        # Check quantity was updated
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 5)
    
    def test_cart_view(self):
        """Test cart display view"""
        # Login user
        self.client.login(username='testuser', password='testpass123')
        
        # Create cart items
        CartItem.objects.create(user=self.user, product=self.product1, quantity=2)
        CartItem.objects.create(user=self.user, product=self.product2, quantity=1)
        
        # Access cart view
        response = self.client.get(reverse('products:cart'))
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product1.name)
        self.assertContains(response, self.product2.name)
        
        # Check context data
        self.assertEqual(len(response.context['cart_items']), 2)
        self.assertEqual(response.context['item_count'], 3)
        
        expected_total = (self.product1.price * 2) + (self.product2.price * 1)
        self.assertEqual(response.context['cart_total'], expected_total)
    
    def test_update_cart_view(self):
        """Test updating cart item quantities"""
        # Login user
        self.client.login(username='testuser', password='testpass123')
        
        # Create cart item
        cart_item = CartItem.objects.create(
            user=self.user,
            product=self.product1,
            quantity=2
        )
        
        # Update quantity
        response = self.client.post(
            reverse('products:update_cart', args=[cart_item.id]),
            {'quantity': 5}
        )
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        
        # Check quantity was updated
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 5)
        
        # Test removing item by setting quantity to 0
        response = self.client.post(
            reverse('products:update_cart', args=[cart_item.id]),
            {'quantity': 0}
        )
        
        # Check item was deleted
        self.assertFalse(CartItem.objects.filter(id=cart_item.id).exists())
    
    def test_remove_from_cart_view(self):
        """Test removing items from cart"""
        # Login user
        self.client.login(username='testuser', password='testpass123')
        
        # Create cart item
        cart_item = CartItem.objects.create(
            user=self.user,
            product=self.product1,
            quantity=3
        )
        
        # Remove item
        response = self.client.post(
            reverse('products:remove_from_cart', args=[cart_item.id])
        )
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        
        # Check item was deleted
        self.assertFalse(CartItem.objects.filter(id=cart_item.id).exists())
    
    def test_cart_context_processor(self):
        """Test cart context processor"""
        from .context_processors import cart_context
        from django.http import HttpRequest
        
        # Create request with authenticated user
        request = HttpRequest()
        request.user = self.user
        
        # Test empty cart
        context = cart_context(request)
        self.assertEqual(context['cart_count'], 0)
        
        # Add items to cart
        CartItem.objects.create(user=self.user, product=self.product1, quantity=2)
        CartItem.objects.create(user=self.user, product=self.product2, quantity=3)
        
        # Test cart with items
        context = cart_context(request)
        self.assertEqual(context['cart_count'], 5)
    
    def test_unauthenticated_cart_access(self):
        """Test cart access for unauthenticated users"""
        # Try to access cart without login
        response = self.client.get(reverse('products:cart'))
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        
        # Try to add to cart without login
        response = self.client.post(
            reverse('products:add_to_cart', args=[self.product1.id]),
            {'quantity': 1}
        )
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_cart_with_invalid_data(self):
        """Test cart with invalid data"""
        # Login user
        self.client.login(username='testuser', password='testpass123')
        
        # Try to add invalid quantity
        response = self.client.post(
            reverse('products:add_to_cart', args=[self.product1.id]),
            {'quantity': -1}
        )
        
        # Should redirect back to product
        self.assertEqual(response.status_code, 302)
        
        # Check no cart item was created
        self.assertFalse(CartItem.objects.filter(user=self.user, product=self.product1).exists())
        
        # Try to add non-existent product
        response = self.client.post(
            reverse('products:add_to_cart', args=[99999]),
            {'quantity': 1}
        )
        
        # Should return 404
        self.assertEqual(response.status_code, 404)