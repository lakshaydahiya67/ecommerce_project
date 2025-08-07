"""
URL configuration for the recommendations app.

This module defines URL patterns for simple recommendation functionality.
"""

from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    # Simplified API endpoints for recommendations
    path('api/recommendations/<int:product_id>/', views.get_recommendations_api, name='get_recommendations'),
    path('api/stats/', views.engine_stats_api, name='engine_stats'),
    # Removed complex feedback and refresh endpoints for beginner-level simplicity
]