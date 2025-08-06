"""
URL configuration for products app.
Handles product listing, detail views, category filtering, and cart functionality.
"""
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Product list view - shows all products with pagination
    path('', views.ProductListView.as_view(), name='product_list'),
    
    # Product detail view - shows individual product information
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    # Category filtering - shows products filtered by category
    path('category/<str:category>/', views.ProductListView.as_view(), name='product_list_by_category'),
    
    # Cart functionality
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/<int:product_id>/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.UpdateCartView.as_view(), name='update_cart'),
    path('cart/remove/<int:item_id>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    
    # Checkout and order functionality
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('order/confirmation/<str:order_number>/', views.OrderConfirmationView.as_view(), name='order_confirmation'),
    path('orders/', views.OrderHistoryView.as_view(), name='order_history'),
    path('order/<str:order_number>/', views.OrderDetailView.as_view(), name='order_detail'),
    
    # User interaction functionality (like/dislike)
    path('product/<int:product_id>/interact/', views.ProductInteractionView.as_view(), name='product_interact'),
    
    # Recommendation API
    path('api/recommendations/<int:product_id>/', views.RecommendationAPIView.as_view(), name='recommendations_api'),
]