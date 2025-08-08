from .models import Product


def get_cart(request):
    """
    Get cart contents from session.
    Returns a dictionary with product_id as keys and quantities as values.
    """
    return request.session.get('cart', {})


def add_to_cart(request, product_id, quantity=1):
    """
    Add a product to the session-based cart.
    
    Args:
        request: Django request object
        product_id: ID of the product to add
        quantity: Quantity to add (default: 1)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Validate product exists
        Product.objects.get(id=product_id)
        
        # Get or create cart in session
        cart = request.session.get('cart', {})
        product_id_str = str(product_id)
        
        # Add or update quantity
        if product_id_str in cart:
            cart[product_id_str] += quantity
        else:
            cart[product_id_str] = quantity
        
        # Save cart back to session
        request.session['cart'] = cart
        return True
        
    except Product.DoesNotExist:
        return False


def remove_from_cart(request, product_id):
    """
    Remove a product completely from the session-based cart.
    
    Args:
        request: Django request object
        product_id: ID of the product to remove
    
    Returns:
        bool: True if item was removed, False if item wasn't in cart
    """
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
        return True
    
    return False


def update_cart_quantity(request, product_id, quantity):
    """
    Update the quantity of a product in the cart.
    If quantity is 0 or less, removes the item from cart.
    
    Args:
        request: Django request object
        product_id: ID of the product to update
        quantity: New quantity
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Validate product exists
        Product.objects.get(id=product_id)
        
        cart = request.session.get('cart', {})
        product_id_str = str(product_id)
        
        if quantity <= 0:
            # Remove item if quantity is 0 or less
            if product_id_str in cart:
                del cart[product_id_str]
        else:
            # Update quantity
            cart[product_id_str] = quantity
        
        request.session['cart'] = cart
        return True
        
    except Product.DoesNotExist:
        return False


def get_cart_items(request):
    """
    Get detailed cart items with product information and totals.
    
    Args:
        request: Django request object
    
    Returns:
        dict: Contains cart_items list, cart_total, and item_count
    """
    cart = request.session.get('cart', {})
    cart_items = []
    cart_total = 0
    
    # Iterate over a static list to avoid RuntimeError if cart is modified
    for product_id, quantity in list(cart.items()):
        try:
            product = Product.objects.get(id=product_id)
            item_total = product.price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': item_total
            })
            cart_total += item_total
        except Product.DoesNotExist:
            # Remove invalid product from cart
            cart.pop(product_id, None)
            request.session['cart'] = cart
    
    return {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'item_count': sum(cart.values()),
    }


def clear_cart(request):
    """
    Clear all items from the session-based cart.
    
    Args:
        request: Django request object
    """
    request.session['cart'] = {}


def get_cart_count(request):
    """
    Get total number of items in the cart.
    
    Args:
        request: Django request object
    
    Returns:
        int: Total number of items in cart
    """
    cart = request.session.get('cart', {})
    return sum(cart.values())