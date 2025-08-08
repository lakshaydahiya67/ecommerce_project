from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from .models import Product, UserInteraction
from .cart_utils import (
    get_cart, add_to_cart, remove_from_cart, update_cart_quantity,
    get_cart_items, clear_cart, get_cart_count
)


class ProductListView(ListView):
    """
    Display all products with simple pagination and category filtering.
    """
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        """Return products, optionally filtered by category."""
        queryset = Product.objects.all()
        
        # Check if category filter is applied via URL
        category = self.kwargs.get('category')
        if category:
            queryset = queryset.filter(category__iexact=category)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        """Add categories for filtering."""
        context = super().get_context_data(**kwargs)
        context['categories'] = Product.objects.values_list('category', flat=True).distinct().order_by('category')
        context['current_category'] = self.kwargs.get('category')
        return context


class ProductDetailView(DetailView):
    """
    Display detailed information for a single product.
    Records user interaction using session for recommendation system.
    """
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    
    def get_object(self, queryset=None):
        """Get the product and record user interaction using session."""
        product = super().get_object(queryset)
        
        # Ensure session exists
        if not self.request.session.session_key:
            self.request.session.create()
        
        # Record user interaction (view) using session
        UserInteraction.objects.get_or_create(
            session_key=self.request.session.session_key,
            product=product,
            interaction_type='view'
        )
        
        return product
    
    def get_context_data(self, **kwargs):
        """Add related products for basic recommendations."""
        context = super().get_context_data(**kwargs)
        
        # Add related products from the same category
        related_products = Product.objects.filter(
            category=self.object.category
        ).exclude(
            id=self.object.id
        )[:4]
        
        context['related_products'] = related_products
        return context


class CartView(View):
    """
    Display cart contents using session storage.
    """
    template_name = 'products/cart.html'
    
    def get(self, request):
        """Display session-based cart items."""
        context = get_cart_items(request)
        return render(request, self.template_name, context)


class AddToCartView(View):
    """
    Handle adding products to session-based cart.
    """
    
    def post(self, request, product_id):
        """Add product to session cart."""
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            messages.error(request, 'Invalid quantity specified.')
            return redirect('products:product_detail', pk=product_id)
        
        # Use utility function to add to cart
        if add_to_cart(request, product_id, quantity):
            cart = get_cart(request)
            if str(product_id) in cart and cart[str(product_id)] > quantity:
                messages.success(request, f'Updated {product.name} quantity in cart.')
            else:
                messages.success(request, f'Added {product.name} to cart.')
        else:
            messages.error(request, 'Product not found.')
            return redirect('products:product_detail', pk=product_id)
        
        # Handle AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cart_count = get_cart_count(request)
            return JsonResponse({
                'success': True,
                'message': f'Added {product.name} to cart.',
                'cart_count': cart_count
            })
        
        return redirect('products:cart')


class UpdateCartView(View):
    """
    Handle cart item quantity updates in session.
    """
    
    def post(self, request, product_id):
        """Update cart item quantity in session."""
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))
        
        # Use utility function to update cart
        if update_cart_quantity(request, product_id, quantity):
            if quantity <= 0:
                messages.success(request, f'Removed {product.name} from cart.')
            else:
                messages.success(request, f'Updated {product.name} quantity.')
        else:
            messages.error(request, 'Product not found.')
        
        # Handle AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cart_data = get_cart_items(request)
            return JsonResponse({
                'success': True,
                'cart_total': float(cart_data['cart_total']),
                'item_count': cart_data['item_count']
            })
        
        return redirect('products:cart')


class RemoveFromCartView(View):
    """
    Handle removing items from session cart.
    """
    
    def post(self, request, product_id):
        """Remove item from session cart."""
        product = get_object_or_404(Product, id=product_id)
        
        # Use utility function to remove from cart
        if remove_from_cart(request, product_id):
            messages.success(request, f'Removed {product.name} from cart.')
        
        # Handle AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cart_data = get_cart_items(request)
            return JsonResponse({
                'success': True,
                'cart_total': float(cart_data['cart_total']),
                'item_count': cart_data['item_count']
            })
        
        return redirect('products:cart')


class CheckoutView(View):
    """
    Handle simple checkout process without complex order management.
    """
    template_name = 'products/checkout.html'
    
    def get(self, request):
        """Display simple checkout form."""
        cart = get_cart(request)
        
        if not cart:
            messages.warning(request, 'Your cart is empty. Add some products before checkout.')
            return redirect('products:cart')
        
        # Use utility function to get cart items
        context = get_cart_items(request)
        return render(request, self.template_name, context)
    
    def post(self, request):
        """Process simple checkout form."""
        cart = request.session.get('cart', {})
        
        if not cart:
            messages.error(request, 'Your cart is empty. Cannot process checkout.')
            return redirect('products:cart')
        
        # Extract basic form data
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        address = request.POST.get('address', '').strip()
        
        # Basic validation
        if not all([first_name, last_name, email, address]):
            messages.error(request, 'Please fill in all required fields.')
            return self.get(request)
        
        # Record purchase interactions for recommendation system
        if not request.session.session_key:
            request.session.create()
        
        for product_id in cart.keys():
            try:
                product = Product.objects.get(id=product_id)
                UserInteraction.objects.create(
                    session_key=request.session.session_key,
                    product=product,
                    interaction_type='purchase'
                )
            except Product.DoesNotExist:
                continue
        
        # Clear cart and show confirmation
        clear_cart(request)
        messages.success(request, 'Order placed successfully! Thank you for your purchase.')
        return redirect('products:order_confirmation')


class OrderConfirmationView(View):
    """
    Display simple order confirmation page.
    """
    template_name = 'products/order_confirmation.html'
    
    def get(self, request):
        """Display order confirmation."""
        return render(request, self.template_name)


@method_decorator(csrf_exempt, name='dispatch')
class ProductInteractionView(View):
    """
    Handle user interactions with products (like/dislike) via AJAX using session.
    """
    
    def post(self, request, product_id):
        """Handle like/dislike interactions with products using session."""
        try:
            data = json.loads(request.body)
            interaction_type = data.get('interaction_type')
            
            if interaction_type not in ['like', 'dislike']:
                return JsonResponse({'success': False, 'error': 'Invalid interaction type'})
            
            product = get_object_or_404(Product, id=product_id)
            
            # Ensure session exists
            if not request.session.session_key:
                request.session.create()
            
            # Remove any existing opposite interaction
            opposite_type = 'dislike' if interaction_type == 'like' else 'like'
            UserInteraction.objects.filter(
                session_key=request.session.session_key,
                product=product,
                interaction_type=opposite_type
            ).delete()
            
            # Toggle current interaction (remove if exists, create if doesn't)
            existing_interaction = UserInteraction.objects.filter(
                session_key=request.session.session_key,
                product=product,
                interaction_type=interaction_type
            ).first()
            
            if existing_interaction:
                existing_interaction.delete()
                user_action = f"Removed {interaction_type}"
                is_active = False
            else:
                UserInteraction.objects.create(
                    session_key=request.session.session_key,
                    product=product,
                    interaction_type=interaction_type
                )
                user_action = f"Added {interaction_type}"
                is_active = True
            
            return JsonResponse({
                'success': True,
                'interaction_type': interaction_type,
                'is_active': is_active,
                'message': user_action
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


