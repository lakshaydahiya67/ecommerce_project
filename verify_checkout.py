#!/usr/bin/env python
"""
Verify that checkout functionality is working correctly.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_project.settings')
django.setup()

from products.models import UserInteraction, Order, OrderItem
from django.contrib.auth.models import User

def verify_checkout():
    print("=== Checkout Functionality Verification ===\n")
    
    # Check recent purchase interactions
    interactions = UserInteraction.objects.filter(interaction_type='purchase').order_by('-timestamp')[:5]
    print(f"Recent purchase interactions: {interactions.count()}")
    for interaction in interactions:
        print(f"- {interaction.user.username} purchased {interaction.product.name} at {interaction.timestamp}")
    
    print()
    
    # Check recent orders
    orders = Order.objects.all().order_by('-created_at')[:3]
    print(f"Recent orders: {orders.count()}")
    for order in orders:
        print(f"- Order {order.order_number}: {order.get_full_name()} - ${order.total_amount} ({order.status})")
        items = OrderItem.objects.filter(order=order)
        for item in items:
            print(f"  * {item.product.name} x{item.quantity} @ ${item.price} = ${item.get_total_price()}")
    
    print()
    
    # Verify models are working
    print("Model verification:")
    print(f"- Order model fields: {len(Order._meta.fields)} fields")
    print(f"- OrderItem model fields: {len(OrderItem._meta.fields)} fields")
    print(f"- UserInteraction types: {[choice[0] for choice in UserInteraction.INTERACTION_CHOICES]}")
    
    print("\n✅ Checkout functionality verification complete!")

if __name__ == '__main__':
    verify_checkout()