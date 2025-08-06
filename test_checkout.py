#!/usr/bin/env python
"""
Simple test script to verify checkout functionality works correctly.
"""
import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_project.settings')

import django
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from products.models import Product, CartItem, Order, OrderItem, UserInteraction

def test_checkout_process():
    """Test the complete checkout process"""
    print("Testing checkout process...")
    
    # Create or get test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'password': 'testpass123'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
    
    # Create test product
    product = Product.objects.create(
        name='Test Product',
        description='A test product for checkout',
        price=29.99,
        category='Electronics'
    )
    
    # Add product to cart
    cart_item = CartItem.objects.create(
        user=user,
        product=product,
        quantity=2
    )
    
    # Create client and login
    client = Client()
    client.login(username='testuser', password='testpass123')
    
    # Test checkout GET request
    checkout_url = reverse('products:checkout')
    response = client.get(checkout_url)
    print(f"Checkout GET status: {response.status_code}")
    assert response.status_code == 200
    
    # Test checkout POST request
    checkout_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'phone': '555-123-4567',
        'address_line_1': '123 Main St',
        'address_line_2': 'Apt 4B',
        'city': 'New York',
        'state': 'NY',
        'postal_code': '10001',
        'country': 'United States'
    }
    
    response = client.post(checkout_url, checkout_data)
    print(f"Checkout POST status: {response.status_code}")
    
    # Check if order was created
    orders = Order.objects.filter(user=user)
    print(f"Orders created: {orders.count()}")
    
    if orders.exists():
        order = orders.first()
        print(f"Order number: {order.order_number}")
        print(f"Order total: ${order.total_amount}")
        print(f"Order status: {order.status}")
        
        # Check order items
        order_items = OrderItem.objects.filter(order=order)
        print(f"Order items: {order_items.count()}")
        
        # Check purchase interactions
        purchase_interactions = UserInteraction.objects.filter(
            user=user,
            product=product,
            interaction_type='purchase'
        )
        print(f"Purchase interactions: {purchase_interactions.count()}")
        
        # Check cart is cleared
        remaining_cart_items = CartItem.objects.filter(user=user)
        print(f"Remaining cart items: {remaining_cart_items.count()}")
        
        print("✅ Checkout process test completed successfully!")
        return True
    else:
        print("❌ No order was created!")
        return False

if __name__ == '__main__':
    try:
        success = test_checkout_process()
        if success:
            print("\n🎉 All checkout tests passed!")
        else:
            print("\n❌ Some tests failed!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()