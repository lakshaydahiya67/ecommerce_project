#!/usr/bin/env python
"""
Test script for AJAX endpoints (like/dislike and recommendations API).
This script tests the API endpoints that will be called by JavaScript.
"""

import os
import sys
import django
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from products.models import Product, UserInteraction

def test_ajax_endpoints():
    """Test AJAX endpoints for user interactions and recommendations."""
    print("Testing AJAX Endpoints...")
    print("=" * 50)
    
    # Create a test client
    client = Client()
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='ajaxtest',
        defaults={
            'email': 'ajax@example.com',
            'password': 'testpass123'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"Created test user: {user.username}")
    
    # Login the user
    client.login(username='ajaxtest', password='testpass123')
    print("User logged in successfully")
    
    # Get a test product
    product = Product.objects.first()
    if not product:
        print("No products found. Please create some products first.")
        return
    
    print(f"Testing with product: {product.name} (ID: {product.id})")
    
    # Test 1: Like interaction
    print("\n1. Testing like interaction...")
    response = client.post(
        f'/product/{product.id}/interact/',
        data=json.dumps({'interaction_type': 'like'}),
        content_type='application/json',
        HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Like successful: {data['success']}")
        print(f"   Action: {data['action']}")
        print(f"   Like count: {data['like_count']}")
        print(f"   User liked: {data['user_liked']}")
    else:
        print(f"   ✗ Like failed with status {response.status_code}")
        print(f"   Response: {response.content}")
    
    # Test 2: Dislike interaction
    print("\n2. Testing dislike interaction...")
    response = client.post(
        f'/product/{product.id}/interact/',
        data=json.dumps({'interaction_type': 'dislike'}),
        content_type='application/json',
        HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Dislike successful: {data['success']}")
        print(f"   Action: {data['action']}")
        print(f"   Dislike count: {data['dislike_count']}")
        print(f"   User disliked: {data['user_disliked']}")
    else:
        print(f"   ✗ Dislike failed with status {response.status_code}")
        print(f"   Response: {response.content}")
    
    # Test 3: Toggle like (should remove dislike and add like)
    print("\n3. Testing like toggle (should remove dislike)...")
    response = client.post(
        f'/product/{product.id}/interact/',
        data=json.dumps({'interaction_type': 'like'}),
        content_type='application/json',
        HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Like toggle successful: {data['success']}")
        print(f"   User liked: {data['user_liked']}")
        print(f"   User disliked: {data['user_disliked']}")
    
    # Test 4: Recommendations API
    print("\n4. Testing recommendations API...")
    response = client.get(f'/api/recommendations/{product.id}/')
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Recommendations API successful: {data['success']}")
        print(f"   Product: {data['product_name']}")
        print(f"   Total recommendations: {data['total_recommendations']}")
        
        for i, rec in enumerate(data['recommendations'][:3]):  # Show first 3
            print(f"   Recommendation {i+1}: {rec['name']} (Score: {rec['final_score']:.3f})")
    else:
        print(f"   ✗ Recommendations API failed with status {response.status_code}")
        print(f"   Response: {response.content}")
    
    # Test 5: Invalid interaction type
    print("\n5. Testing invalid interaction type...")
    response = client.post(
        f'/product/{product.id}/interact/',
        data=json.dumps({'interaction_type': 'invalid'}),
        content_type='application/json',
        HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    )
    
    if response.status_code == 400:
        data = response.json()
        print(f"   ✓ Invalid interaction properly rejected: {data['error']}")
    else:
        print(f"   ✗ Invalid interaction not properly handled")
    
    # Test 6: Unauthenticated access
    print("\n6. Testing unauthenticated access...")
    client.logout()
    response = client.post(
        f'/product/{product.id}/interact/',
        data=json.dumps({'interaction_type': 'like'}),
        content_type='application/json',
        HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    )
    
    if response.status_code == 302:  # Redirect to login
        print("   ✓ Unauthenticated access properly redirected to login")
    else:
        print(f"   ✗ Unauthenticated access not properly handled: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("AJAX endpoints testing completed!")

if __name__ == '__main__':
    test_ajax_endpoints()