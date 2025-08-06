#!/usr/bin/env python
"""
Test script for user interaction tracking functionality.
This script tests the like/dislike functionality and recommendation improvements.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_project.settings')
django.setup()

from django.contrib.auth.models import User
from products.models import Product, UserInteraction
from recommendations.engine import recommendation_engine

def test_user_interactions():
    """Test user interaction tracking functionality."""
    print("Testing User Interaction Tracking...")
    print("=" * 50)
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"Created test user: {user.username}")
    else:
        print(f"Using existing test user: {user.username}")
    
    # Get some products to test with
    products = Product.objects.all()[:5]
    if not products:
        print("No products found. Please create some products first.")
        return
    
    print(f"Found {len(products)} products to test with")
    
    # Test creating interactions
    print("\n1. Testing interaction creation...")
    for i, product in enumerate(products[:3]):
        interaction_type = 'like' if i % 2 == 0 else 'dislike'
        interaction, created = UserInteraction.objects.get_or_create(
            user=user,
            product=product,
            interaction_type=interaction_type
        )
        if created:
            print(f"   Created {interaction_type} interaction for {product.name}")
        else:
            print(f"   Interaction already exists: {interaction_type} for {product.name}")
    
    # Test view interactions (these should already exist from ProductDetailView)
    print("\n2. Testing view interactions...")
    for product in products:
        view_interaction, created = UserInteraction.objects.get_or_create(
            user=user,
            product=product,
            interaction_type='view'
        )
        if created:
            print(f"   Created view interaction for {product.name}")
    
    # Display current interactions
    print("\n3. Current user interactions:")
    user_interactions = UserInteraction.objects.filter(user=user)
    for interaction in user_interactions:
        print(f"   {interaction.user.username} {interaction.interaction_type} {interaction.product.name}")
    
    # Test recommendation engine with interactions
    print("\n4. Testing recommendation engine with interactions...")
    if products:
        test_product = products[0]
        print(f"Getting recommendations for: {test_product.name}")
        
        # Refresh recommendation engine data
        recommendation_engine.refresh_data()
        
        # Get recommendations
        recommendations = recommendation_engine.get_recommendations(
            product_id=test_product.id,
            user_id=user.id,
            num_recommendations=3
        )
        
        print(f"Found {len(recommendations)} recommendations:")
        for rec in recommendations:
            print(f"   - {rec['name']} (Score: {rec['final_score']:.3f})")
            print(f"     Category: {rec['similarity_score']:.3f}, "
                  f"User: {rec['user_score']:.3f}, "
                  f"Collaborative: {rec['collaborative_score']:.3f}, "
                  f"Popularity: {rec['popularity_score']:.3f}")
            print(f"     Reason: {rec['reason']}")
    
    # Test interaction counts
    print("\n5. Testing interaction counts...")
    for product in products[:3]:
        like_count = UserInteraction.objects.filter(
            product=product,
            interaction_type='like'
        ).count()
        dislike_count = UserInteraction.objects.filter(
            product=product,
            interaction_type='dislike'
        ).count()
        view_count = UserInteraction.objects.filter(
            product=product,
            interaction_type='view'
        ).count()
        
        print(f"   {product.name}: {like_count} likes, {dislike_count} dislikes, {view_count} views")
    
    print("\n" + "=" * 50)
    print("User interaction testing completed!")

def test_collaborative_filtering():
    """Test collaborative filtering functionality."""
    print("\nTesting Collaborative Filtering...")
    print("=" * 50)
    
    # Create multiple test users with different preferences
    users_data = [
        ('user1', ['Electronics', 'Electronics']),  # Likes electronics
        ('user2', ['Books', 'Books']),              # Likes books
        ('user3', ['Electronics', 'Books']),        # Likes both
    ]
    
    for username, preferred_categories in users_data:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': f'{username}@example.com'}
        )
        
        if created:
            print(f"Created user: {username}")
        
        # Create like interactions for products in preferred categories
        for category in preferred_categories:
            products_in_category = Product.objects.filter(category=category)[:2]
            for product in products_in_category:
                UserInteraction.objects.get_or_create(
                    user=user,
                    product=product,
                    interaction_type='like'
                )
    
    # Test collaborative filtering
    print("\nTesting collaborative recommendations...")
    test_user = User.objects.get(username='user1')
    electronics_products = Product.objects.filter(category='Electronics')
    
    if electronics_products:
        test_product = electronics_products[0]
        recommendation_engine.refresh_data()
        
        recommendations = recommendation_engine.get_recommendations(
            product_id=test_product.id,
            user_id=test_user.id,
            num_recommendations=5
        )
        
        print(f"Collaborative filtering recommendations for {test_user.username}:")
        for rec in recommendations:
            if rec['collaborative_score'] > 0:
                print(f"   - {rec['name']} (Collaborative Score: {rec['collaborative_score']:.3f})")

if __name__ == '__main__':
    test_user_interactions()
    test_collaborative_filtering()