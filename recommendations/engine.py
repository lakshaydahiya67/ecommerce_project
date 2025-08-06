"""
Simple Recommendation Engine for E-commerce Application

This module implements a basic content-based filtering recommendation system
using pandas for data manipulation and simple similarity calculations.
The engine focuses on category-based recommendations suitable for beginners.
"""

import pandas as pd
import numpy as np
from django.db.models import Count, Q
from products.models import Product, UserInteraction
from typing import List, Dict, Optional


class SimpleRecommendationEngine:
    """
    A basic recommendation engine that uses content-based filtering.
    
    This engine recommends products based on:
    1. Category similarity (primary factor)
    2. User interaction patterns (secondary factor)
    3. Product popularity (fallback)
    
    The implementation uses pandas for data manipulation and basic
    mathematical operations for similarity calculations.
    """
    
    def __init__(self):
        """Initialize the recommendation engine."""
        self.products_df = None
        self.interactions_df = None
        self.category_similarity = None
        self.is_loaded = False
    
    def load_data(self):
        """
        Load product and interaction data from Django models into pandas DataFrames.
        
        This method converts Django QuerySets to pandas DataFrames for easier
        manipulation and analysis. It's called automatically when recommendations
        are requested if data hasn't been loaded yet.
        """
        try:
            # Load products data
            products_queryset = Product.objects.all().values(
                'id', 'name', 'description', 'price', 'category', 'created_at'
            )
            self.products_df = pd.DataFrame(list(products_queryset))
            
            # Load user interactions data
            interactions_queryset = UserInteraction.objects.all().values(
                'user_id', 'product_id', 'interaction_type', 'timestamp'
            )
            self.interactions_df = pd.DataFrame(list(interactions_queryset))
            
            # If we have products, calculate category similarity
            if not self.products_df.empty:
                self._calculate_category_similarity()
                self.is_loaded = True
            
            print(f"Loaded {len(self.products_df)} products and {len(self.interactions_df)} interactions")
            
        except Exception as e:
            print(f"Error loading data: {e}")
            # Initialize empty DataFrames as fallback
            self.products_df = pd.DataFrame()
            self.interactions_df = pd.DataFrame()
            self.is_loaded = False
    
    def _calculate_category_similarity(self):
        """
        Calculate similarity between products based on categories.
        
        This method creates a simple similarity matrix where products
        in the same category get a similarity score of 1.0, and products
        in different categories get a score of 0.0.
        
        In a more advanced system, this could be enhanced with:
        - Subcategory relationships
        - Price range similarity
        - Brand similarity
        - Feature-based similarity
        """
        if self.products_df.empty:
            self.category_similarity = pd.DataFrame()
            return
        
        # Get unique categories
        categories = self.products_df['category'].unique()
        
        # Create a simple category similarity matrix
        # Products in the same category have similarity = 1.0
        # Products in different categories have similarity = 0.0
        similarity_data = []
        
        for _, product1 in self.products_df.iterrows():
            similarities = []
            for _, product2 in self.products_df.iterrows():
                if product1['id'] == product2['id']:
                    # Same product
                    similarity = 0.0  # Don't recommend the same product
                elif product1['category'] == product2['category']:
                    # Same category
                    similarity = 1.0
                else:
                    # Different category
                    similarity = 0.0
                
                similarities.append(similarity)
            
            similarity_data.append(similarities)
        
        # Create similarity matrix DataFrame
        product_ids = self.products_df['id'].tolist()
        self.category_similarity = pd.DataFrame(
            similarity_data,
            index=product_ids,
            columns=product_ids
        )
        
        print(f"Calculated category similarity matrix: {self.category_similarity.shape}")
    
    def _get_user_interaction_score(self, user_id: Optional[int], product_id: int) -> float:
        """
        Calculate a score based on user interactions with similar products.
        
        This method looks at the user's interaction history and gives higher
        scores to products that are similar to ones the user has interacted
        with positively (likes, purchases).
        
        Args:
            user_id: ID of the user (None for anonymous users)
            product_id: ID of the product to score
            
        Returns:
            Float score between 0.0 and 1.0
        """
        if user_id is None or self.interactions_df.empty:
            return 0.0
        
        # Get user's positive interactions (likes and purchases)
        user_interactions = self.interactions_df[
            (self.interactions_df['user_id'] == user_id) &
            (self.interactions_df['interaction_type'].isin(['like', 'purchase']))
        ]
        
        if user_interactions.empty:
            return 0.0
        
        # Calculate score based on category overlap with user's liked products
        liked_product_ids = user_interactions['product_id'].tolist()
        liked_products = self.products_df[self.products_df['id'].isin(liked_product_ids)]
        
        if liked_products.empty:
            return 0.0
        
        # Get the category of the product we're scoring
        product_category = self.products_df[
            self.products_df['id'] == product_id
        ]['category'].iloc[0] if not self.products_df[
            self.products_df['id'] == product_id
        ].empty else None
        
        if product_category is None:
            return 0.0
        
        # Count how many liked products are in the same category
        same_category_count = len(liked_products[liked_products['category'] == product_category])
        total_liked = len(liked_products)
        
        # Return the ratio as a score
        return same_category_count / total_liked if total_liked > 0 else 0.0
    
    def _get_collaborative_filtering_score(self, user_id: Optional[int], product_id: int) -> float:
        """
        Calculate collaborative filtering score: "users who liked X also liked Y"
        
        This method finds users with similar preferences and recommends products
        they liked. It implements a basic collaborative filtering approach.
        
        Args:
            user_id: ID of the user (None for anonymous users)
            product_id: ID of the product to score
            
        Returns:
            Float score between 0.0 and 1.0
        """
        if user_id is None or self.interactions_df.empty:
            return 0.0
        
        # Get current user's liked products
        user_likes = self.interactions_df[
            (self.interactions_df['user_id'] == user_id) &
            (self.interactions_df['interaction_type'] == 'like')
        ]['product_id'].tolist()
        
        if not user_likes:
            return 0.0
        
        # Find other users who liked the same products
        similar_users = self.interactions_df[
            (self.interactions_df['product_id'].isin(user_likes)) &
            (self.interactions_df['interaction_type'] == 'like') &
            (self.interactions_df['user_id'] != user_id)
        ]['user_id'].unique()
        
        if len(similar_users) == 0:
            return 0.0
        
        # Count how many similar users liked the target product
        similar_user_likes = self.interactions_df[
            (self.interactions_df['user_id'].isin(similar_users)) &
            (self.interactions_df['product_id'] == product_id) &
            (self.interactions_df['interaction_type'] == 'like')
        ]
        
        # Calculate score based on the ratio of similar users who liked this product
        likes_count = len(similar_user_likes)
        total_similar_users = len(similar_users)
        
        return likes_count / total_similar_users if total_similar_users > 0 else 0.0
    
    def _get_popularity_score(self, product_id: int) -> float:
        """
        Calculate popularity score based on user interactions.
        
        Products with more views, likes, and purchases get higher scores.
        This is used as a fallback when category-based recommendations
        are not sufficient.
        
        Args:
            product_id: ID of the product to score
            
        Returns:
            Float score representing popularity (normalized between 0.0 and 1.0)
        """
        if self.interactions_df.empty:
            return 0.0
        
        # Count interactions for this product
        product_interactions = self.interactions_df[
            self.interactions_df['product_id'] == product_id
        ]
        
        if product_interactions.empty:
            return 0.0
        
        # Weight different interaction types
        interaction_weights = {
            'view': 1.0,
            'like': 2.0,
            'purchase': 3.0,
            'dislike': -1.0
        }
        
        # Calculate weighted score
        total_score = 0.0
        for _, interaction in product_interactions.iterrows():
            weight = interaction_weights.get(interaction['interaction_type'], 0.0)
            total_score += weight
        
        # Normalize by the maximum possible score in the dataset
        if not self.interactions_df.empty:
            max_interactions = self.interactions_df.groupby('product_id').size().max()
            max_possible_score = max_interactions * max(interaction_weights.values())
            return min(total_score / max_possible_score, 1.0) if max_possible_score > 0 else 0.0
        
        return 0.0
    
    def get_recommendations(self, product_id: int, user_id: Optional[int] = None, 
                          num_recommendations: int = 5) -> List[Dict]:
        """
        Get product recommendations based on the given product.
        
        This method combines category similarity, user interaction patterns,
        and popularity to generate recommendations. It's the main interface
        for getting recommendations from the engine.
        
        Args:
            product_id: ID of the product to base recommendations on
            user_id: ID of the user requesting recommendations (optional)
            num_recommendations: Number of recommendations to return
            
        Returns:
            List of dictionaries containing recommended products with scores
        """
        # Load data if not already loaded
        if not self.is_loaded:
            self.load_data()
        
        # Return empty list if no data available
        if self.products_df.empty:
            return []
        
        # Check if the product exists
        if product_id not in self.products_df['id'].values:
            return self._get_fallback_recommendations(num_recommendations)
        
        recommendations = []
        
        # Get category-based similarities
        if not self.category_similarity.empty and product_id in self.category_similarity.index:
            similarities = self.category_similarity.loc[product_id]
            
            # Sort by similarity score (descending)
            similar_products = similarities.sort_values(ascending=False)
            
            # Get top similar products (excluding the original product)
            for similar_product_id, similarity_score in similar_products.items():
                if similar_product_id == product_id or similarity_score == 0.0:
                    continue
                
                # Get product details
                product_info = self.products_df[
                    self.products_df['id'] == similar_product_id
                ].iloc[0]
                
                # Calculate additional scores
                user_score = self._get_user_interaction_score(user_id, similar_product_id)
                collaborative_score = self._get_collaborative_filtering_score(user_id, similar_product_id)
                popularity_score = self._get_popularity_score(similar_product_id)
                
                # Combine scores (category similarity is primary factor)
                final_score = (
                    similarity_score * 0.4 +      # Category similarity (40%)
                    user_score * 0.2 +            # User preference (20%)
                    collaborative_score * 0.3 +   # Collaborative filtering (30%)
                    popularity_score * 0.1        # Popularity (10%)
                )
                
                recommendations.append({
                    'product_id': int(similar_product_id),
                    'name': product_info['name'],
                    'price': float(product_info['price']),
                    'category': product_info['category'],
                    'similarity_score': float(similarity_score),
                    'user_score': float(user_score),
                    'collaborative_score': float(collaborative_score),
                    'popularity_score': float(popularity_score),
                    'final_score': float(final_score),
                    'reason': f'Same category: {product_info["category"]}'
                })
                
                if len(recommendations) >= num_recommendations:
                    break
        
        # If we don't have enough recommendations, add popular products
        if len(recommendations) < num_recommendations:
            fallback_recs = self._get_fallback_recommendations(
                num_recommendations - len(recommendations)
            )
            recommendations.extend(fallback_recs)
        
        # Sort by final score and return top N
        recommendations.sort(key=lambda x: x['final_score'], reverse=True)
        return recommendations[:num_recommendations]
    
    def _get_fallback_recommendations(self, num_recommendations: int) -> List[Dict]:
        """
        Get fallback recommendations when category-based recommendations fail.
        
        This method returns popular products or recently added products
        as a fallback when the main recommendation algorithm cannot
        provide sufficient results.
        
        Args:
            num_recommendations: Number of recommendations to return
            
        Returns:
            List of dictionaries containing fallback recommendations
        """
        if self.products_df.empty:
            return []
        
        recommendations = []
        
        # Get products sorted by creation date (newest first) as a simple fallback
        recent_products = self.products_df.sort_values('created_at', ascending=False)
        
        for _, product in recent_products.iterrows():
            popularity_score = self._get_popularity_score(product['id'])
            
            recommendations.append({
                'product_id': int(product['id']),
                'name': product['name'],
                'price': float(product['price']),
                'category': product['category'],
                'similarity_score': 0.0,
                'user_score': 0.0,
                'collaborative_score': 0.0,
                'popularity_score': float(popularity_score),
                'final_score': float(popularity_score),
                'reason': 'Popular product'
            })
            
            if len(recommendations) >= num_recommendations:
                break
        
        return recommendations
    
    def refresh_data(self):
        """
        Refresh the loaded data from the database.
        
        This method should be called when products or interactions
        are added/modified to ensure recommendations stay current.
        """
        self.is_loaded = False
        self.load_data()
    
    def get_stats(self) -> Dict:
        """
        Get statistics about the recommendation engine's data.
        
        Returns:
            Dictionary containing statistics about loaded data
        """
        if not self.is_loaded:
            self.load_data()
        
        stats = {
            'total_products': len(self.products_df) if not self.products_df.empty else 0,
            'total_interactions': len(self.interactions_df) if not self.interactions_df.empty else 0,
            'unique_categories': len(self.products_df['category'].unique()) if not self.products_df.empty else 0,
            'is_loaded': self.is_loaded
        }
        
        if not self.products_df.empty:
            stats['categories'] = self.products_df['category'].value_counts().to_dict()
        
        if not self.interactions_df.empty:
            stats['interaction_types'] = self.interactions_df['interaction_type'].value_counts().to_dict()
        
        return stats


# Global instance of the recommendation engine
# This allows the engine to maintain loaded data across requests
recommendation_engine = SimpleRecommendationEngine()