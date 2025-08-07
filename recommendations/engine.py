"""
Simple Recommendation Engine for E-commerce Application

This module implements a basic content-based filtering recommendation system
using pandas for data manipulation and cosine similarity calculations.
The engine focuses on category and price-based recommendations suitable for beginners.
"""

import pandas as pd
import numpy as np
import time
from products.models import Product, UserInteraction
from typing import List, Dict, Optional

# Try to import Cython-optimized similarity functions
CYTHON_AVAILABLE = False
try:
    from . import similarity as cython_similarity
    CYTHON_AVAILABLE = True
    print("✓ Cython optimization module loaded successfully")
except ImportError:
    print("⚠ Cython module not available - using Python fallback")
    pass


class SimpleRecommendationEngine:
    """
    A basic recommendation engine that uses content-based filtering with cosine similarity.
    
    This engine recommends products based on category and price features using
    cosine similarity calculations. It's designed for beginners learning ML concepts.
    """
    
    def __init__(self):
        """Initialize the recommendation engine."""
        self.products_df = None
        self.feature_matrix = None
        self.similarity_matrix = None
        self.is_loaded = False
    
    def load_data(self):
        """
        Load product data and create feature matrix for similarity calculations.
        """
        try:
            # Load products data
            products_queryset = Product.objects.all().values(
                'id', 'name', 'price', 'category'
            )
            self.products_df = pd.DataFrame(list(products_queryset))
            
            if not self.products_df.empty:
                self._create_feature_matrix()
                self._calculate_similarity_matrix()
                self.is_loaded = True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            self.products_df = pd.DataFrame()
            self.is_loaded = False
    
    def _create_feature_matrix(self):
        """
        Create feature matrix with category and price features for cosine similarity.
        """
        if self.products_df.empty:
            return
        
        # Create category features using one-hot encoding
        category_features = pd.get_dummies(self.products_df['category'], prefix='category')
        
        # Create price range features (normalized)
        # Convert decimal prices to float for calculations
        prices = pd.to_numeric(self.products_df['price'], errors='coerce')
        price_min, price_max = prices.min(), prices.max()
        
        # Normalize prices to 0-1 range
        if price_max > price_min:
            normalized_prices = (prices - price_min) / (price_max - price_min)
        else:
            normalized_prices = pd.Series([0.5] * len(prices))
        
        # Create price range bins (low, medium, high)
        price_bins = pd.cut(normalized_prices, bins=3, labels=['low', 'medium', 'high'])
        price_features = pd.get_dummies(price_bins, prefix='price')
        
        # Combine all features
        self.feature_matrix = pd.concat([category_features, price_features], axis=1)
        self.feature_matrix = self.feature_matrix.fillna(0)
    
    def _calculate_similarity_matrix(self):
        """
        Calculate cosine similarity matrix using the feature matrix.
        """
        if self.feature_matrix is None or self.feature_matrix.empty:
            return
        
        # Use Cython optimization if available, otherwise use numpy
        if CYTHON_AVAILABLE:
            try:
                self.similarity_matrix = cython_similarity.calculate_cosine_similarity(
                    self.feature_matrix.values.astype(np.float64)
                )
            except:
                self.similarity_matrix = self._calculate_cosine_similarity_python()
        else:
            self.similarity_matrix = self._calculate_cosine_similarity_python()
    
    def _calculate_cosine_similarity_python(self):
        """
        Calculate cosine similarity using pure Python/numpy.
        """
        features = self.feature_matrix.values
        
        # Calculate dot product
        dot_product = np.dot(features, features.T)
        
        # Calculate norms
        norms = np.linalg.norm(features, axis=1)
        
        # Calculate cosine similarity
        similarity_matrix = dot_product / (norms[:, np.newaxis] * norms[np.newaxis, :])
        
        # Set diagonal to 0 (don't recommend same product)
        np.fill_diagonal(similarity_matrix, 0)
        
        return similarity_matrix
    

    
    def get_recommendations(self, product_id: int, session_key: Optional[str] = None, 
                          num_recommendations: int = 4) -> List[Dict]:
        """
        Get product recommendations using cosine similarity based on category and price features.
        
        Args:
            product_id: ID of the product to base recommendations on
            session_key: Session key for user interactions (optional)
            num_recommendations: Number of recommendations to return
            
        Returns:
            List of dictionaries containing recommended products with similarity scores
        """
        # Load data if not already loaded
        if not self.is_loaded:
            self.load_data()
        
        # Return empty list if no data available
        if self.products_df.empty or self.similarity_matrix is None:
            return []
        
        # Find the product index
        try:
            product_index = self.products_df[self.products_df['id'] == product_id].index[0]
        except IndexError:
            return self._get_fallback_recommendations(num_recommendations)
        
        # Get similarity scores for this product
        similarities = self.similarity_matrix[product_index]
        
        # Get top similar products (excluding the original product)
        similar_indices = np.argsort(similarities)[::-1]
        
        recommendations = []
        for idx in similar_indices:
            if len(recommendations) >= num_recommendations:
                break
                
            similarity_score = similarities[idx]
            if similarity_score <= 0:  # Skip products with no similarity
                continue
                
            product_info = self.products_df.iloc[idx]
            
            # Apply user feedback if available
            final_score = similarity_score
            if session_key:
                final_score = self._apply_user_feedback(session_key, product_info['id'], similarity_score)
            
            recommendations.append({
                'product_id': int(product_info['id']),
                'name': product_info['name'],
                'price': float(product_info['price']),
                'category': product_info['category'],
                'similarity_score': float(similarity_score),
                'final_score': float(final_score)
            })
        
        # If we don't have enough recommendations, add fallback products
        if len(recommendations) < num_recommendations:
            fallback_recs = self._get_fallback_recommendations(
                num_recommendations - len(recommendations)
            )
            recommendations.extend(fallback_recs)
        
        return recommendations[:num_recommendations]
    
    def _apply_user_feedback(self, session_key: str, product_id: int, base_score: float) -> float:
        """
        Apply user feedback to adjust recommendation scores.
        
        Args:
            session_key: User's session key
            product_id: ID of the product
            base_score: Base similarity score
            
        Returns:
            Adjusted score based on user feedback
        """
        try:
            # Get user interactions for this session and product
            interactions = UserInteraction.objects.filter(
                session_key=session_key,
                product_id=product_id
            )
            
            # Apply simple feedback adjustments
            for interaction in interactions:
                if interaction.interaction_type == 'like':
                    base_score *= 1.2  # Boost liked products
                elif interaction.interaction_type == 'dislike':
                    base_score *= 0.5  # Reduce disliked products
            
            return base_score
        except:
            return base_score
    
    def _get_fallback_recommendations(self, num_recommendations: int) -> List[Dict]:
        """
        Get fallback recommendations when similarity-based recommendations fail.
        
        Args:
            num_recommendations: Number of recommendations to return
            
        Returns:
            List of dictionaries containing fallback recommendations
        """
        if self.products_df.empty:
            return []
        
        recommendations = []
        
        # Get random products as simple fallback
        sample_products = self.products_df.sample(n=min(num_recommendations, len(self.products_df)))
        
        for _, product in sample_products.iterrows():
            recommendations.append({
                'product_id': int(product['id']),
                'name': product['name'],
                'price': float(product['price']),
                'category': product['category'],
                'similarity_score': 0.0,
                'final_score': 0.1  # Low fallback score
            })
        
        return recommendations
    
    def update_with_feedback(self, session_key: str, product_id: int, feedback: str):
        """
        Update user feedback for a product.
        
        Args:
            session_key: User's session key
            product_id: ID of the product
            feedback: Type of feedback ('like' or 'dislike')
        """
        try:
            UserInteraction.objects.create(
                session_key=session_key,
                product_id=product_id,
                interaction_type=feedback
            )
        except Exception as e:
            print(f"Error saving feedback: {e}")
    
    def get_stats(self) -> Dict:
        """
        Get basic statistics about the recommendation engine.
        
        Returns:
            Dictionary containing basic statistics
        """
        if not self.is_loaded:
            self.load_data()
        
        return {
            'total_products': len(self.products_df) if not self.products_df.empty else 0,
            'unique_categories': len(self.products_df['category'].unique()) if not self.products_df.empty else 0,
            'is_loaded': self.is_loaded,
            'cython_available': CYTHON_AVAILABLE
        }
    
    def compare_performance(self, num_runs: int = 3) -> Dict:
        """
        Compare performance between Python and Cython implementations.
        
        Args:
            num_runs: Number of runs for timing comparison
            
        Returns:
            Dictionary containing performance comparison results
        """
        if not self.is_loaded or self.feature_matrix is None or self.feature_matrix.empty:
            return {'error': 'No data loaded for performance comparison'}
        
        features = self.feature_matrix.values.astype(np.float64)
        results = {
            'cython_available': CYTHON_AVAILABLE,
            'matrix_size': features.shape,
            'num_runs': num_runs
        }
        
        # Time Python implementation
        python_times = []
        for _ in range(num_runs):
            start_time = time.time()
            self._calculate_cosine_similarity_python()
            python_times.append(time.time() - start_time)
        
        results['python_avg_time'] = sum(python_times) / len(python_times)
        results['python_min_time'] = min(python_times)
        
        # Time Cython implementation if available
        if CYTHON_AVAILABLE:
            cython_times = []
            for _ in range(num_runs):
                start_time = time.time()
                try:
                    cython_similarity.calculate_cosine_similarity(features)
                    cython_times.append(time.time() - start_time)
                except Exception as e:
                    results['cython_error'] = str(e)
                    break
            
            if cython_times:
                results['cython_avg_time'] = sum(cython_times) / len(cython_times)
                results['cython_min_time'] = min(cython_times)
                results['speedup'] = results['python_avg_time'] / results['cython_avg_time']
        else:
            results['cython_avg_time'] = None
            results['speedup'] = None
        
        return results
    
    def refresh_data(self):
        """
        Refresh the loaded data from the database.
        """
        self.is_loaded = False
        self.load_data()


# Global instance of the recommendation engine
# This allows the engine to maintain loaded data across requests
recommendation_engine = SimpleRecommendationEngine()