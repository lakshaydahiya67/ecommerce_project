from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Sum, F
from django.db import transaction
from django.utils.crypto import get_random_string
import uuid
import json
from .models import Product, UserInteraction, CartItem, Order, OrderItem


class ProductListView(ListView):
    """
    Display all products with pagination and category filtering.
    Supports filtering by category through URL parameter.
    """
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12  # Show 12 products per page
    
    def get_queryset(self):
        """
        Return products, optionally filtered by category.
        """
        queryset = Product.objects.all()
        
        # Check if category filter is applied via URL
        category = self.kwargs.get('category')
        if category:
            queryset = queryset.filter(category__iexact=category)
        
        # Order by creation date (newest first)
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        """
        Add additional context data for template rendering.
        """
        context = super().get_context_data(**kwargs)
        
        # Add all available categories for filtering
        context['categories'] = Product.objects.values_list('category', flat=True).distinct().order_by('category')
        
        # Add current category if filtering is applied
        context['current_category'] = self.kwargs.get('category')
        
        # Add total product count
        context['total_products'] = self.get_queryset().count()
        
        return context


class ProductDetailView(DetailView):
    """
    Display detailed information for a single product.
    Records user interaction (view) for recommendation system.
    """
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    
    def get_object(self, queryset=None):
        """
        Get the product and record user interaction if user is authenticated.
        """
        product = super().get_object(queryset)
        
        # Record user interaction (view) if user is authenticated
        if self.request.user.is_authenticated:
            UserInteraction.objects.get_or_create(
                user=self.request.user,
                product=product,
                interaction_type='view',
                defaults={'timestamp': None}  # Will use auto_now_add
            )
        
        return product
    
    def get_context_data(self, **kwargs):
        """
        Add additional context data for template rendering.
        """
        context = super().get_context_data(**kwargs)
        
        # Add related products from the same category (for basic recommendations)
        related_products = Product.objects.filter(
            category=self.object.category
        ).exclude(
            id=self.object.id
        )[:4]  # Show 4 related products
        
        context['related_products'] = related_products
        
        # Add user interaction data if user is authenticated
        if self.request.user.is_authenticated:
            user_interactions = UserInteraction.objects.filter(
                user=self.request.user,
                product=self.object
            )
            context['user_interactions'] = user_interactions
        
        return context


class AddToCartView(LoginRequiredMixin, View):
    """
    Handle adding products to cart.
    Supports both POST requests and AJAX requests.
    """
    
    def post(self, request, product_id):
        """
        Add product to cart or update quantity if already exists.
        """
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))
        
        # Validate quantity
        if quantity <= 0:
            messages.error(request, 'Invalid quantity specified.')
            return redirect('products:product_detail', pk=product_id)
        
        # Get or create cart item
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # Update quantity if item already exists
            cart_item.quantity += quantity
            cart_item.save()
            messages.success(request, f'Updated {product.name} quantity in cart.')
        else:
            messages.success(request, f'Added {product.name} to cart.')
        
        # Handle AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cart_count = CartItem.objects.filter(user=request.user).aggregate(
                total=Sum('quantity')
            )['total'] or 0
            
            return JsonResponse({
                'success': True,
                'message': f'Added {product.name} to cart.',
                'cart_count': cart_count
            })
        
        # Redirect to cart or back to product
        next_url = request.POST.get('next', 'cart')
        if next_url == 'cart':
            return redirect('products:cart')
        else:
            return redirect('products:product_detail', pk=product_id)


class CartView(LoginRequiredMixin, View):
    """
    Display cart contents with quantities and totals.
    """
    template_name = 'products/cart.html'
    
    def get(self, request):
        """
        Display user's cart items.
        """
        cart_items = CartItem.objects.filter(user=request.user).select_related('product')
        
        # Calculate totals
        cart_total = sum(item.get_total_price() for item in cart_items)
        item_count = sum(item.quantity for item in cart_items)
        
        context = {
            'cart_items': cart_items,
            'cart_total': cart_total,
            'item_count': item_count,
        }
        
        return render(request, self.template_name, context)


class UpdateCartView(LoginRequiredMixin, View):
    """
    Handle cart item quantity updates.
    """
    
    def post(self, request, item_id):
        """
        Update cart item quantity or remove item if quantity is 0.
        """
        cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            # Remove item from cart
            product_name = cart_item.product.name
            cart_item.delete()
            messages.success(request, f'Removed {product_name} from cart.')
        else:
            # Update quantity
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, f'Updated {cart_item.product.name} quantity.')
        
        # Handle AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Recalculate cart totals
            cart_items = CartItem.objects.filter(user=request.user)
            cart_total = sum(item.get_total_price() for item in cart_items)
            item_count = sum(item.quantity for item in cart_items)
            
            return JsonResponse({
                'success': True,
                'cart_total': float(cart_total),
                'item_count': item_count,
                'item_total': float(cart_item.get_total_price()) if quantity > 0 else 0
            })
        
        return redirect('products:cart')


class RemoveFromCartView(LoginRequiredMixin, View):
    """
    Handle removing items from cart.
    """
    
    def post(self, request, item_id):
        """
        Remove item from cart completely.
        """
        cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
        product_name = cart_item.product.name
        cart_item.delete()
        
        messages.success(request, f'Removed {product_name} from cart.')
        
        # Handle AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Recalculate cart totals
            cart_items = CartItem.objects.filter(user=request.user)
            cart_total = sum(item.get_total_price() for item in cart_items)
            item_count = sum(item.quantity for item in cart_items)
            
            return JsonResponse({
                'success': True,
                'cart_total': float(cart_total),
                'item_count': item_count
            })
        
        return redirect('products:cart')


# Helper function to get cart count for templates
def get_cart_count(user):
    """
    Get total number of items in user's cart.
    Used in templates and context processors.
    """
    if user.is_authenticated:
        return CartItem.objects.filter(user=user).aggregate(
            total=Sum('quantity')
        )['total'] or 0
    return 0


class CheckoutView(LoginRequiredMixin, View):
    """
    Handle the checkout process - display checkout form and process orders.
    """
    template_name = 'products/checkout.html'
    
    def get(self, request):
        """
        Display checkout form with cart items and order summary.
        """
        # Get user's cart items
        cart_items = CartItem.objects.filter(user=request.user).select_related('product')
        
        # Redirect to cart if no items
        if not cart_items.exists():
            messages.warning(request, 'Your cart is empty. Add some products before checkout.')
            return redirect('products:cart')
        
        # Calculate totals
        cart_total = sum(item.get_total_price() for item in cart_items)
        item_count = sum(item.quantity for item in cart_items)
        
        # Pre-fill form with user information if available
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
        
        context = {
            'cart_items': cart_items,
            'cart_total': cart_total,
            'item_count': item_count,
            'initial_data': initial_data,
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        """
        Process the checkout form and create order.
        """
        # Get user's cart items
        cart_items = CartItem.objects.filter(user=request.user).select_related('product')
        
        # Redirect to cart if no items
        if not cart_items.exists():
            messages.error(request, 'Your cart is empty. Cannot process checkout.')
            return redirect('products:cart')
        
        # Extract form data
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address_line_1 = request.POST.get('address_line_1', '').strip()
        address_line_2 = request.POST.get('address_line_2', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        country = request.POST.get('country', 'United States').strip()
        
        # Basic validation
        required_fields = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'address_line_1': address_line_1,
            'city': city,
            'state': state,
            'postal_code': postal_code,
        }
        
        missing_fields = [field for field, value in required_fields.items() if not value]
        if missing_fields:
            messages.error(request, f'Please fill in all required fields: {", ".join(missing_fields)}')
            return self.get(request)
        
        # Calculate total
        total_amount = sum(item.get_total_price() for item in cart_items)
        
        try:
            # Use database transaction to ensure data consistency
            with transaction.atomic():
                # Generate unique order number
                order_number = self._generate_order_number()
                
                # Create order
                order = Order.objects.create(
                    user=request.user,
                    order_number=order_number,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone=phone,
                    address_line_1=address_line_1,
                    address_line_2=address_line_2,
                    city=city,
                    state=state,
                    postal_code=postal_code,
                    country=country,
                    total_amount=total_amount,
                    status='pending'
                )
                
                # Create order items and record purchase interactions
                for cart_item in cart_items:
                    # Create order item
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        price=cart_item.product.price
                    )
                    
                    # Record purchase interaction for recommendation system
                    UserInteraction.objects.create(
                        user=request.user,
                        product=cart_item.product,
                        interaction_type='purchase'
                    )
                
                # Clear user's cart
                cart_items.delete()
                
                # Update order status to processing
                order.status = 'processing'
                order.save()
                
                messages.success(request, f'Order {order_number} placed successfully!')
                return redirect('products:order_confirmation', order_number=order_number)
                
        except Exception as e:
            messages.error(request, 'An error occurred while processing your order. Please try again.')
            return self.get(request)
    
    def _generate_order_number(self):
        """
        Generate a unique order number.
        """
        while True:
            # Generate order number with format: ORD-YYYYMMDD-XXXXX
            from datetime import datetime
            date_str = datetime.now().strftime('%Y%m%d')
            random_str = get_random_string(5, allowed_chars='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            order_number = f'ORD-{date_str}-{random_str}'
            
            # Check if order number already exists
            if not Order.objects.filter(order_number=order_number).exists():
                return order_number


class OrderConfirmationView(LoginRequiredMixin, View):
    """
    Display order confirmation page after successful checkout.
    """
    template_name = 'products/order_confirmation.html'
    
    def get(self, request, order_number):
        """
        Display order confirmation details.
        """
        # Get the order for the current user
        order = get_object_or_404(
            Order.objects.prefetch_related('items__product'),
            order_number=order_number,
            user=request.user
        )
        
        context = {
            'order': order,
        }
        
        return render(request, self.template_name, context)


class OrderHistoryView(LoginRequiredMixin, ListView):
    """
    Display user's order history.
    """
    model = Order
    template_name = 'products/order_history.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        """
        Return orders for the current user.
        """
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')


class OrderDetailView(LoginRequiredMixin, DetailView):
    """
    Display detailed information for a specific order.
    """
    model = Order
    template_name = 'products/order_detail.html'
    context_object_name = 'order'
    slug_field = 'order_number'
    slug_url_kwarg = 'order_number'
    
    def get_queryset(self):
        """
        Ensure users can only view their own orders.
        """
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')


@method_decorator(login_required, name='dispatch')
class ProductInteractionView(View):
    """
    Handle user interactions with products (like/dislike) via AJAX.
    This view supports immediate feedback for recommendation system.
    """
    
    def post(self, request, product_id):
        """
        Handle like/dislike interactions with products.
        Expects JSON data with 'interaction_type' field.
        """
        try:
            # Parse JSON data from request
            data = json.loads(request.body)
            interaction_type = data.get('interaction_type')
            
            # Validate interaction type
            if interaction_type not in ['like', 'dislike']:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid interaction type. Must be "like" or "dislike".'
                }, status=400)
            
            # Get the product
            product = get_object_or_404(Product, id=product_id)
            
            # Check if user already has this interaction
            existing_interaction = UserInteraction.objects.filter(
                user=request.user,
                product=product,
                interaction_type=interaction_type
            ).first()
            
            if existing_interaction:
                # Remove existing interaction (toggle off)
                existing_interaction.delete()
                action = 'removed'
            else:
                # Remove opposite interaction if it exists
                opposite_type = 'dislike' if interaction_type == 'like' else 'like'
                UserInteraction.objects.filter(
                    user=request.user,
                    product=product,
                    interaction_type=opposite_type
                ).delete()
                
                # Create new interaction
                UserInteraction.objects.create(
                    user=request.user,
                    product=product,
                    interaction_type=interaction_type
                )
                action = 'added'
            
            # Get current interaction counts for this product
            like_count = UserInteraction.objects.filter(
                product=product,
                interaction_type='like'
            ).count()
            
            dislike_count = UserInteraction.objects.filter(
                product=product,
                interaction_type='dislike'
            ).count()
            
            # Get user's current interactions with this product
            user_interactions = UserInteraction.objects.filter(
                user=request.user,
                product=product
            ).values_list('interaction_type', flat=True)
            
            return JsonResponse({
                'success': True,
                'action': action,
                'interaction_type': interaction_type,
                'like_count': like_count,
                'dislike_count': dislike_count,
                'user_liked': 'like' in user_interactions,
                'user_disliked': 'dislike' in user_interactions,
                'message': f'Successfully {action} {interaction_type} for {product.name}'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'An error occurred: {str(e)}'
            }, status=500)


@method_decorator(login_required, name='dispatch')
class RecommendationAPIView(View):
    """
    API endpoint for fetching product recommendations via AJAX.
    Uses the recommendation engine to provide personalized suggestions.
    """
    
    def get(self, request, product_id):
        """
        Get recommendations for a specific product.
        Supports query parameters: num_recommendations (default: 5)
        """
        try:
            # Get query parameters
            num_recommendations = int(request.GET.get('num_recommendations', 5))
            num_recommendations = min(max(num_recommendations, 1), 20)  # Limit between 1-20
            
            # Get the product
            product = get_object_or_404(Product, id=product_id)
            
            # Import recommendation engine
            from recommendations.engine import recommendation_engine
            
            # Get recommendations
            recommendations = recommendation_engine.get_recommendations(
                product_id=product_id,
                user_id=request.user.id,
                num_recommendations=num_recommendations
            )
            
            # Format recommendations for JSON response
            formatted_recommendations = []
            for rec in recommendations:
                # Get additional product details
                try:
                    rec_product = Product.objects.get(id=rec['product_id'])
                    formatted_recommendations.append({
                        'product_id': rec['product_id'],
                        'name': rec['name'],
                        'price': rec['price'],
                        'category': rec['category'],
                        'image_url': rec_product.image.url if rec_product.image else None,
                        'detail_url': f"/product/{rec['product_id']}/",
                        'similarity_score': rec['similarity_score'],
                        'user_score': rec['user_score'],
                        'collaborative_score': rec.get('collaborative_score', 0.0),
                        'popularity_score': rec['popularity_score'],
                        'final_score': rec['final_score'],
                        'reason': rec['reason']
                    })
                except Product.DoesNotExist:
                    continue
            
            return JsonResponse({
                'success': True,
                'product_id': product_id,
                'product_name': product.name,
                'recommendations': formatted_recommendations,
                'total_recommendations': len(formatted_recommendations)
            })
            
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid num_recommendations parameter'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'An error occurred: {str(e)}'
            }, status=500)