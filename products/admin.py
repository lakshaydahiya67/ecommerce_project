from django.contrib import admin
from .models import Product, UserInteraction, CartItem, Order, OrderItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin interface for Product model with enhanced functionality for managing products.
    """
    list_display = ['name', 'category', 'price', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description', 'category']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category')
        }),
        ('Pricing', {
            'fields': ('price',)
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    """
    Admin interface for UserInteraction model to view and analyze user behavior.
    """
    list_display = ['user', 'product', 'interaction_type', 'timestamp']
    list_filter = ['interaction_type', 'timestamp', 'product__category']
    search_fields = ['user__username', 'product__name']
    ordering = ['-timestamp']
    readonly_fields = ['timestamp']
    
    # Make the admin read-only since interactions should be created through user actions
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """
    Admin interface for CartItem model to manage user cart items.
    """
    list_display = ['user', 'product', 'quantity', 'get_total_price', 'added_at']
    list_filter = ['added_at', 'product__category']
    search_fields = ['user__username', 'product__name']
    ordering = ['-added_at']
    readonly_fields = ['added_at', 'updated_at', 'get_total_price']
    
    def get_total_price(self, obj):
        """Display total price for this cart item in admin"""
        return f"${obj.get_total_price():.2f}"
    get_total_price.short_description = 'Total Price'


class OrderItemInline(admin.TabularInline):
    """
    Inline admin for OrderItem model to display order items within Order admin.
    """
    model = OrderItem
    extra = 0
    readonly_fields = ['get_total_price']
    
    def get_total_price(self, obj):
        """Display total price for this order item"""
        if obj.pk:
            return f"${obj.get_total_price():.2f}"
        return "-"
    get_total_price.short_description = 'Total Price'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Admin interface for Order model with enhanced functionality for managing orders.
    """
    list_display = ['order_number', 'user', 'get_full_name', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'country']
    search_fields = ['order_number', 'user__username', 'first_name', 'last_name', 'email']
    ordering = ['-created_at']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'total_amount')
        }),
        ('Customer Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Shipping Address', {
            'fields': ('address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'country')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        """Display customer's full name in admin list"""
        return obj.get_full_name()
    get_full_name.short_description = 'Customer Name'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Admin interface for OrderItem model to manage individual order items.
    """
    list_display = ['order', 'product', 'quantity', 'price', 'get_total_price']
    list_filter = ['order__created_at', 'product__category']
    search_fields = ['order__order_number', 'product__name']
    ordering = ['-order__created_at']
    
    def get_total_price(self, obj):
        """Display total price for this order item in admin"""
        return f"${obj.get_total_price():.2f}"
    get_total_price.short_description = 'Total Price'