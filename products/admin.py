from django.contrib import admin
from .models import Product, UserInteraction


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'created_at']
    list_filter = ['category']
    search_fields = ['name', 'category']


@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'product', 'interaction_type', 'timestamp']
    list_filter = ['interaction_type']
    readonly_fields = ['timestamp']