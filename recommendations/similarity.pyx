"""
Simple Cython optimization for cosine similarity calculations.

This module provides a basic Cython-optimized implementation of cosine similarity
calculation for the recommendation engine. It focuses on one main optimization
to demonstrate the performance benefits of Cython for mathematical operations.
"""

import numpy as np
cimport numpy as np
cimport cython
from libc.math cimport sqrt

# Define NumPy array types for better performance
DTYPE = np.float64
ctypedef np.float64_t DTYPE_t


@cython.boundscheck(False)  # Disable bounds checking for performance
@cython.wraparound(False)   # Disable negative index wrapping
def calculate_cosine_similarity(np.ndarray[DTYPE_t, ndim=2] matrix):
    """
    Calculate cosine similarity matrix using optimized Cython code.
    
    This function computes the cosine similarity between all pairs of rows
    in the input matrix. This is the main optimization target for demonstrating
    Cython performance benefits.
    
    Formula: cosine_similarity(A, B) = (A · B) / (||A|| * ||B||)
    
    Args:
        matrix: 2D NumPy array where each row represents a feature vector
        
    Returns:
        2D NumPy array containing cosine similarities between all pairs
    """
    cdef int n = matrix.shape[0]  # Number of rows (products)
    cdef int m = matrix.shape[1]  # Number of features
    cdef np.ndarray[DTYPE_t, ndim=2] similarity = np.zeros((n, n), dtype=DTYPE)
    
    # Declare loop variables with static types for performance
    cdef int i, j, k
    cdef DTYPE_t dot_product, norm_i, norm_j, temp_i, temp_j
    
    # Calculate similarity for each pair of rows
    for i in range(n):
        for j in range(n):
            if i == j:
                # Same item - set similarity to 0 (don't recommend same product)
                similarity[i, j] = 0.0
            else:
                # Calculate dot product and norms
                dot_product = 0.0
                norm_i = 0.0
                norm_j = 0.0
                
                # Compute dot product and norms in a single loop for efficiency
                for k in range(m):
                    temp_i = matrix[i, k]
                    temp_j = matrix[j, k]
                    
                    dot_product += temp_i * temp_j
                    norm_i += temp_i * temp_i
                    norm_j += temp_j * temp_j
                
                # Calculate norms (square roots)
                norm_i = sqrt(norm_i)
                norm_j = sqrt(norm_j)
                
                # Calculate cosine similarity
                if norm_i > 0.0 and norm_j > 0.0:
                    similarity[i, j] = dot_product / (norm_i * norm_j)
                else:
                    similarity[i, j] = 0.0
    
    return similarity