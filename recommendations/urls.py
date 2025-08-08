from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    path('recommendations/<int:product_id>/', views.get_recommendations_api, name='get_recommendations'),
    path('stats/', views.engine_stats_api, name='engine_stats'),
]