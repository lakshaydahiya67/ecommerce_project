from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('category/<str:category>/', views.ProductListView.as_view(), name='product_list_by_category'),
    
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/<int:product_id>/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('cart/update/<int:product_id>/', views.UpdateCartView.as_view(), name='update_cart'),
    path('cart/remove/<int:product_id>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('order/confirmation/', views.OrderConfirmationView.as_view(), name='order_confirmation'),
    
    path('product/<int:product_id>/interact/', views.ProductInteractionView.as_view(), name='product_interact'),
]