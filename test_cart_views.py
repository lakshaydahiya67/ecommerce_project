#!/usr/bin/env python
"""
Test script to verify cart views functionality
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from products.models import Product, CartItem

def test_cart_views():
    """Test cart views functionality"""
    print("Testing Cart Views...")
    
    # Create test client
    client = Client()
    
    # Get or create test user
    user, created = User.objects.get_or_create(
        username='viewtestuser',
        defaults={'email': 'viewtest@example.com'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
    
    # Login user
    client.login(username='viewtestuser', password='testpass123')
    print(f"Logged in as: {user.username}")
    
    # Get a sample product
    product = Product.objects.first()
    print(f"Testing with product: {product.name}")
    
    # Test cart view (should be empty initially)
    response = client.get('/cart/')
    print(f"Cart view status: {response.status_code}")
    
    # Test adding to cart
    response = client.post(f'/cart/add/{product.id}/', {
        'quantity': 3,
        'next': 'cart'
    })
    print(f"Add to cart status: {response.status_code}")
    
    # Check if item was added
    cart_items = CartItem.objects.filter(user=user)
    print(f"Cart items count: {cart_items.count()}")
    
    if cart_items.exists():
        item = cart_items.first()
        print(f"Cart item: {item.quantity} x {item.product.name}")
        
        # Test updating cart
        response = client.post(f'/cart/update/{item.id}/', {
            'quantity': 5
        })
        print(f"Update cart status: {response.status_code}")
        
        # Check updated quantity
        item.refresh_from_db()
        print(f"Updated quantity: {item.quantity}")
        
        # Test cart view with items
        response = client.get('/cart/')
        print(f"Cart view with items status: {response.status_code}")
        
        # Test removing from cart
        response = client.post(f'/cart/remove/{item.id}/')
        print(f"Remove from cart status: {response.status_code}")
        
        # Check if item was removed
        remaining_items = CartItem.objects.filter(user=user).count()
        print(f"Remaining cart items: {remaining_items}")
    
    print("Cart views test completed!")

if __name__ == '__main__':
    test_cart_views()