#!/usr/bin/env python
"""
Simple test script to verify cart functionality
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_project.settings')
django.setup()

from django.contrib.auth.models import User
from products.models import Product, CartItem

def test_cart_functionality():
    """Test basic cart operations"""
    print("Testing Cart Functionality...")
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"Created test user: {user.username}")
    else:
        print(f"Using existing test user: {user.username}")
    
    # Get a sample product
    product = Product.objects.first()
    if not product:
        print("No products found! Please create some products first.")
        return
    
    print(f"Testing with product: {product.name} (${product.price})")
    
    # Test adding to cart
    cart_item, created = CartItem.objects.get_or_create(
        user=user,
        product=product,
        defaults={'quantity': 2}
    )
    
    if created:
        print(f"Added {cart_item.quantity} x {product.name} to cart")
    else:
        cart_item.quantity += 1
        cart_item.save()
        print(f"Updated cart item quantity to {cart_item.quantity}")
    
    # Test cart calculations
    total_price = cart_item.get_total_price()
    print(f"Cart item total: ${total_price}")
    
    # Test cart summary
    user_cart_items = CartItem.objects.filter(user=user)
    cart_total = sum(item.get_total_price() for item in user_cart_items)
    item_count = sum(item.quantity for item in user_cart_items)
    
    print(f"User cart summary:")
    print(f"  - Total items: {item_count}")
    print(f"  - Total value: ${cart_total}")
    
    # List all cart items
    print(f"Cart contents:")
    for item in user_cart_items:
        print(f"  - {item.quantity} x {item.product.name} = ${item.get_total_price()}")
    
    print("Cart functionality test completed successfully!")

if __name__ == '__main__':
    test_cart_functionality()