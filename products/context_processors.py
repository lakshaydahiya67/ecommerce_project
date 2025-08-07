from .cart_utils import get_cart_count


def cart_context(request):
    """
    Context processor to add session-based cart information to all templates.
    """
    return {
        'cart_count': get_cart_count(request)
    }