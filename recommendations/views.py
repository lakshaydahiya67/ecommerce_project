from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import logging

from .engine import recommendation_engine

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def get_recommendations_api(request, product_id):
    """
    API endpoint to get product recommendations.
    
    Args:
        product_id: ID of the product to base recommendations on
        
    Query parameters:
        - num_recommendations: Number of recommendations (default: 4)
    """
    try:
        num_recommendations = int(request.GET.get('num_recommendations', 4))
        session_key = request.session.session_key
        
        recommendations = recommendation_engine.get_recommendations(
            product_id=int(product_id),
            session_key=session_key,
            num_recommendations=num_recommendations
        )
        
        return JsonResponse({
            'product_id': product_id,
            'recommendations': recommendations,
            'count': len(recommendations)
        })
    
    except Exception as e:
        logger.error(f"Error getting recommendations for product {product_id}: {e}")
        return JsonResponse({
            'error': str(e),
            'product_id': product_id,
            'recommendations': []
        }, status=500)


@require_http_methods(["GET"])
def engine_stats_api(request):
    """
    API endpoint to get recommendation engine statistics.
    """
    try:
        stats = recommendation_engine.get_stats()
        return JsonResponse(stats)
    except Exception as e:
        logger.error(f"Error getting engine stats: {e}")
        return JsonResponse({
            'error': str(e)
        }, status=500)


