#!/usr/bin/env python
"""
Test script to verify that the product detail template renders correctly
with the new like/dislike functionality.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from products.models import Product, UserInteraction

def test_template_rendering():
    """Test that the product detail template renders correctly."""
    print("Testing Template Rendering...")
    print("=" * 50)
    
    # Create a test client
    client = Client()
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='templatetest',
        defaults={
            'email': 'template@example.com',
            'password': 'testpass123'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
    
    # Login the user
    client.login(username='templatetest', password='testpass123')
    
    # Get a test product
    product = Product.objects.first()
    if not product:
        print("No products found. Please create some products first.")
        return
    
    print(f"Testing template rendering for product: {product.name}")
    
    # Test 1: Load product detail page
    print("\n1. Testing product detail page load...")
    response = client.get(f'/product/{product.id}/')
    
    if response.status_code == 200:
        print("   ✓ Product detail page loaded successfully")
        
        # Check if like/dislike buttons are present
        content = response.content.decode('utf-8')
        
        if 'id="like-btn"' in content:
            print("   ✓ Like button found in template")
        else:
            print("   ✗ Like button not found in template")
        
        if 'id="dislike-btn"' in content:
            print("   ✓ Dislike button found in template")
        else:
            print("   ✗ Dislike button not found in template")
        
        if 'data-product-id' in content:
            print("   ✓ Product ID data attribute found")
        else:
            print("   ✗ Product ID data attribute not found")
        
        if 'handleInteraction' in content:
            print("   ✓ JavaScript interaction handler found")
        else:
            print("   ✗ JavaScript interaction handler not found")
        
        # Check if CSRF token is present
        if 'csrfmiddlewaretoken' in content:
            print("   ✓ CSRF token found")
        else:
            print("   ✗ CSRF token not found")
    
    else:
        print(f"   ✗ Product detail page failed to load: {response.status_code}")
    
    # Test 2: Create some interactions and reload page
    print("\n2. Testing page with existing interactions...")
    
    # Create a like interaction
    UserInteraction.objects.get_or_create(
        user=user,
        product=product,
        interaction_type='like'
    )
    
    # Reload the page
    response = client.get(f'/product/{product.id}/')
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        print("   ✓ Page reloaded successfully with existing interactions")
        
        # The JavaScript should initialize the button state based on user_interactions
        if 'user_interactions' in content or 'interaction.interaction_type' in content:
            print("   ✓ User interactions context variable found")
        else:
            print("   ✗ User interactions context variable not found")
            # Let's check what interactions-related content is there
            if 'interaction' in content.lower():
                print("   ℹ Some interaction-related content found")
    
    # Test 3: Test unauthenticated access
    print("\n3. Testing unauthenticated access...")
    client.logout()
    
    response = client.get(f'/product/{product.id}/')
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        print("   ✓ Page loads for unauthenticated users")
        
        # Should show login message instead of like/dislike buttons
        if 'Login' in content and 'to add items to cart' in content:
            print("   ✓ Login message shown for unauthenticated users")
        else:
            print("   ✗ Login message not properly shown")
    
    print("\n" + "=" * 50)
    print("Template rendering testing completed!")

if __name__ == '__main__':
    test_template_rendering()