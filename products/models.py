from django.db import models


class Product(models.Model):
    """Basic product model for e-commerce catalog"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class UserInteraction(models.Model):
    """Track user interactions with products for recommendations"""
    INTERACTION_CHOICES = [
        ('view', 'View'),
        ('like', 'Like'),
        ('dislike', 'Dislike'),
        ('purchase', 'Purchase'),
    ]
    
    session_key = models.CharField(max_length=40)  # Django session key
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.session_key[:8]}... {self.interaction_type} {self.product.name}"



