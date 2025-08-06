from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    """
    Product model representing items available for purchase in the e-commerce store.
    Includes basic product information needed for display and recommendations.
    """
    name = models.CharField(max_length=200, help_text="Product name")
    description = models.TextField(help_text="Detailed product description")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Product price in USD")
    category = models.CharField(max_length=100, help_text="Product category for grouping and recommendations")
    image = models.ImageField(upload_to='products/', blank=True, null=True, help_text="Product image")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Product"
        verbose_name_plural = "Products"
    
    def __str__(self):
        return self.name


class UserInteraction(models.Model):
    """
    Model to track user behavior with products for recommendation system.
    Records different types of interactions: views, likes, dislikes, purchases.
    """
    INTERACTION_CHOICES = [
        ('view', 'View'),
        ('like', 'Like'),
        ('dislike', 'Dislike'),
        ('purchase', 'Purchase'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text="User who performed the interaction")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, help_text="Product that was interacted with")
    interaction_type = models.CharField(
        max_length=20, 
        choices=INTERACTION_CHOICES,
        help_text="Type of interaction performed by the user"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "User Interaction"
        verbose_name_plural = "User Interactions"
        # Prevent duplicate interactions of the same type for the same user-product pair
        unique_together = ['user', 'product', 'interaction_type']
    
    def __str__(self):
        return f"{self.user.username} {self.interaction_type} {self.product.name}"


class CartItem(models.Model):
    """
    Model to store user cart data.
    Tracks products added to cart with quantities for each user.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text="User who owns this cart item")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, help_text="Product in the cart")
    quantity = models.PositiveIntegerField(default=1, help_text="Quantity of the product in cart")
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-added_at']
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        # Ensure one cart item per user-product combination
        unique_together = ['user', 'product']
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name} (x{self.quantity})"
    
    def get_total_price(self):
        """Calculate total price for this cart item (quantity * product price)"""
        return self.quantity * self.product.price


class Order(models.Model):
    """
    Model to store completed purchases.
    Records order information and links to purchased products.
    """
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text="User who placed the order")
    order_number = models.CharField(max_length=20, unique=True, help_text="Unique order identifier")
    
    # Basic order information
    first_name = models.CharField(max_length=100, help_text="Customer's first name")
    last_name = models.CharField(max_length=100, help_text="Customer's last name")
    email = models.EmailField(help_text="Customer's email address")
    phone = models.CharField(max_length=20, blank=True, help_text="Customer's phone number")
    
    # Shipping address
    address_line_1 = models.CharField(max_length=255, help_text="Street address")
    address_line_2 = models.CharField(max_length=255, blank=True, help_text="Apartment, suite, etc.")
    city = models.CharField(max_length=100, help_text="City")
    state = models.CharField(max_length=100, help_text="State/Province")
    postal_code = models.CharField(max_length=20, help_text="ZIP/Postal code")
    country = models.CharField(max_length=100, default='United States', help_text="Country")
    
    # Order details
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total order amount")
    status = models.CharField(
        max_length=20, 
        choices=ORDER_STATUS_CHOICES, 
        default='pending',
        help_text="Current order status"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Order"
        verbose_name_plural = "Orders"
    
    def __str__(self):
        return f"Order {self.order_number} - {self.user.username}"
    
    def get_full_name(self):
        """Return customer's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def get_full_address(self):
        """Return formatted full address"""
        address_parts = [
            self.address_line_1,
            self.address_line_2,
            f"{self.city}, {self.state} {self.postal_code}",
            self.country
        ]
        return "\n".join(part for part in address_parts if part)


class OrderItem(models.Model):
    """
    Model to store individual items within an order.
    Links products to orders with quantities and prices at time of purchase.
    """
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, help_text="Order this item belongs to")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, help_text="Product that was purchased")
    quantity = models.PositiveIntegerField(help_text="Quantity purchased")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price at time of purchase")
    
    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
    
    def __str__(self):
        return f"{self.order.order_number} - {self.product.name} (x{self.quantity})"
    
    def get_total_price(self):
        """Calculate total price for this order item"""
        return self.quantity * self.price
