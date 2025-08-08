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
    Content-based product recommendation engine using cosine similarity.
    """
    
    def __init__(self):
        """Initialize the recommendation engine."""
        self.products_df = None
        self.feature_matrix = None
        self.similarity_matrix = None
        self.is_loaded = False

    def _format_recommendation(self, product_row, similarity_score=0.0, final_score=0.0, reason=""):
        """
        Format a product row as a recommendation dict.
        """
        product_id = int(product_row['id'])
        # Try to get image URL if available
        image_url = None
        if 'image' in product_row and product_row['image']:
            image_url = str(product_row['image']) if str(product_row['image']).startswith('/media/') else f'/media/products/{product_row["image"]}'
        else:
            image_url = None
        return {
            'product_id': product_id,
            'name': product_row['name'],
            'price': float(product_row['price']),
            'category': product_row['category'],
            'similarity_score': float(similarity_score),
            'final_score': float(final_score),
            'detail_url': f'/product/{product_id}/',
            'image_url': image_url,
            'reason': reason
        }
    
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
        similarities = self.similarity_matrix[product_index].copy()
        
        # Apply user preference learning if session key is provided
        if session_key:
            similarities = self._apply_user_preferences(session_key, similarities)
        
        # Get top similar products (excluding the original product)
        similar_indices = np.argsort(similarities)[::-1]
        
        recommendations = []
        seen_products = {product_id}  # Exclude the current product
        
        for idx in similar_indices:
            if len(recommendations) >= num_recommendations:
                break
            product_info = self.products_df.iloc[idx]
            if product_info['id'] in seen_products:
                continue
            similarity_score = similarities[idx]
            if similarity_score <= 0:
                continue
            seen_products.add(product_info['id'])
            reason = self._get_recommendation_reason(session_key, product_info, similarity_score)
            recommendations.append(
                self._format_recommendation(
                    product_info,
                    similarity_score=similarity_score,
                    final_score=similarity_score,
                    reason=reason
                )
            )
        
        # If we don't have enough recommendations, add personalized fallback products
        if len(recommendations) < num_recommendations:
            fallback_recs = self._get_personalized_fallback_recommendations(
                session_key, num_recommendations - len(recommendations), seen_products
            )
            recommendations.extend(fallback_recs)
        return recommendations[:num_recommendations]
    
    def _apply_user_preferences(self, session_key: str, similarities: np.ndarray) -> np.ndarray:
        """
        Apply user preferences learned from interaction history to adjust similarity scores.
        
        Args:
            session_key: User's session key
            similarities: Base similarity scores array
            
        Returns:
            Adjusted similarity scores based on user preferences
        """
        try:
            # Get all user interactions for this session
            interactions = UserInteraction.objects.filter(session_key=session_key)
            
            if not interactions.exists():
                return similarities
            
            # Build user preference profile
            category_preferences = {}
            price_preferences = []
            
            for interaction in interactions:
                try:
                    product = Product.objects.get(id=interaction.product_id)
                    
                    # Track category preferences
                    if product.category not in category_preferences:
                        category_preferences[product.category] = {'likes': 0, 'dislikes': 0}
                    
                    if interaction.interaction_type == 'like':
                        category_preferences[product.category]['likes'] += 1
                        price_preferences.append(float(product.price))
                    elif interaction.interaction_type == 'dislike':
                        category_preferences[product.category]['dislikes'] += 1
                except Product.DoesNotExist:
                    continue
            
            # Calculate preference scores for each category
            category_scores = {}
            for category, prefs in category_preferences.items():
                # Stronger boost for liked categories
                score = 1.0 + (prefs['likes'] * 0.5) - (prefs['dislikes'] * 0.3)
                category_scores[category] = max(0.1, score)  # Minimum score of 0.1
            
            # Calculate preferred price range if we have liked products
            price_boost_range = None
            if price_preferences:
                avg_price = np.mean(price_preferences)
                std_price = np.std(price_preferences) if len(price_preferences) > 1 else avg_price * 0.2
                price_boost_range = (avg_price - std_price, avg_price + std_price)
            
            # Apply preferences to all products
            adjusted_similarities = similarities.copy()
            for idx, product in self.products_df.iterrows():
                # Apply category preference boost
                if product['category'] in category_scores:
                    adjusted_similarities[idx] *= category_scores[product['category']]
                
                # Apply price preference boost
                if price_boost_range:
                    product_price = float(product['price'])
                    if price_boost_range[0] <= product_price <= price_boost_range[1]:
                        adjusted_similarities[idx] *= 1.3  # Boost products in preferred price range
                
                # Apply direct product interaction history
                product_interactions = interactions.filter(product_id=product['id'])
                for pi in product_interactions:
                    if pi.interaction_type == 'like':
                        adjusted_similarities[idx] *= 1.5  # Strong boost for directly liked products
                    elif pi.interaction_type == 'dislike':
                        adjusted_similarities[idx] *= 0.3  # Strong reduction for disliked products
            
            return adjusted_similarities
            
        except Exception as e:
            print(f"Error applying user preferences: {e}")
            return similarities
    
    def _get_recommendation_reason(self, session_key: Optional[str], product_info: pd.Series, score: float) -> str:
        """
        Generate a personalized recommendation reason based on user history.
        """
        base_category = product_info["category"].lower()
        try:
            if not session_key:
                return f'Similar {base_category} product'
            # Check if user has liked products in this category
            liked_in_category = UserInteraction.objects.filter(
                session_key=session_key,
                interaction_type='like',
                product__category=product_info['category']
            ).exists()
            if liked_in_category:
                return f'Based on your interest in {base_category}'
            # Check if this specific product was interacted with
            product_interaction = UserInteraction.objects.filter(
                session_key=session_key,
                product_id=product_info['id']
            ).first()
            if product_interaction:
                if product_interaction.interaction_type == 'like':
                    return 'Previously liked by you'
                elif product_interaction.interaction_type == 'view':
                    return 'Previously viewed by you'
            # High score means strong similarity
            if score > 0.8:
                return f'Highly similar {base_category} product'
            return f'Similar {base_category} product'
        except Exception as e:
            print(f"Error in _get_recommendation_reason: {e}")
            return f'Similar {base_category} product'
    
    def _get_personalized_fallback_recommendations(self, session_key: Optional[str], 
                                                   num_recommendations: int, 
                                                   seen_products: set) -> List[Dict]:
        """
        Get personalized fallback recommendations based on user preferences.
        """
        def sample_and_format(df, n, reason_func):
            sampled = df.sample(n=min(n, len(df))) if not df.empty else pd.DataFrame()
            return [self._format_recommendation(row, similarity_score=0.5, final_score=0.5, reason=reason_func(row)) for _, row in sampled.iterrows()]

        if not session_key:
            return self._get_fallback_recommendations(num_recommendations)
        try:
            liked_categories = list(UserInteraction.objects.filter(
                session_key=session_key,
                interaction_type='like'
            ).values_list('product__category', flat=True).distinct())
            recommendations = []
            if liked_categories:
                preferred_products = self.products_df[
                    (self.products_df['category'].isin(liked_categories)) &
                    (~self.products_df['id'].isin(seen_products))
                ]
                recommendations.extend(sample_and_format(
                    preferred_products,
                    num_recommendations,
                    lambda row: f'Popular in {row["category"].lower()} (your preferred category)'
                ))
            # If still need more, add general fallback
            if len(recommendations) < num_recommendations:
                remaining = num_recommendations - len(recommendations)
                recommendations.extend(self._get_fallback_recommendations(remaining))
            return recommendations[:num_recommendations]
        except Exception as e:
            print(f"Error in personalized fallback: {e}")
            return self._get_fallback_recommendations(num_recommendations)
    
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
        sample_products = self.products_df.sample(n=min(num_recommendations, len(self.products_df)))
        for _, product in sample_products.iterrows():
            recommendations.append(
                self._format_recommendation(
                    product,
                    similarity_score=0.0,
                    final_score=0.1,
                    reason=f'Popular {product["category"].lower()} product'
                )
            )
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