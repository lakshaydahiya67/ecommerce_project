# Django E-commerce with Machine Learning Recommendations

A simple Django-based e-commerce web application featuring product recommendations powered by machine learning and optimized with Cython. This project demonstrates core skills in Python, Django web development, basic machine learning concepts, and performance optimization.

## Project Features

- **E-commerce Functionality**: Product catalog, shopping cart, and checkout process
- **ML Recommendations**: Content-based product recommendations using cosine similarity
- **Performance Optimization**: Cython-optimized similarity calculations for better performance
- **User Interaction**: Like/dislike feedback system to improve recommendations

## Quick Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation Steps

1. **Navigate to the project directory**
   ```bash
   cd ecommerce_project
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Compile Cython modules** (for performance optimization)
   ```bash
   cd recommendations
   python setup.py build_ext --inplace
   cd ..
   ```

4. **Set up the database**
   ```bash
   python manage.py migrate
   ```

5. **Load sample products**
   ```bash
   python manage.py create_sample_products
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Open your browser and visit**: http://127.0.0.1:8000/

## How to Use

### Basic E-commerce Features
- **Browse Products**: View all products on the homepage with categories and prices
- **Product Details**: Click on any product to see detailed information
- **Shopping Cart**: Add products to cart using the "Add to Cart" button
- **Checkout**: Complete your order with the simple checkout form

### Recommendation System
- **View Recommendations**: See "Similar Products" on each product detail page
- **Provide Feedback**: Click 👍 (like) or 👎 (dislike) buttons on recommendations
- **Personalized Results**: Recommendations improve based on your feedback and browsing

### Testing Performance
- **Check Cython**: Visit any product page - if Cython compiled successfully, similarity calculations run faster
- **Fallback**: If Cython didn't compile, the system uses Python implementation (still works, just slower)

## Technology Stack

- **Backend**: Django 4.2+ (Python web framework)
- **Database**: SQLite (for development)
- **Machine Learning**: pandas (data handling), numpy (math operations)
- **Performance**: Cython (optimization)
- **Frontend**: HTML, Bootstrap CSS, basic JavaScript

## Machine Learning Algorithm

### Content-Based Filtering
The recommendation system uses **content-based filtering**, which recommends products similar to ones you're interested in.

**How it works:**
1. **Product Features**: Each product has features like category and price range
2. **Similarity Calculation**: Uses cosine similarity to find products with similar features
3. **User Preferences**: Tracks your likes/dislikes to personalize recommendations
4. **Final Scoring**: Combines similarity scores with your preferences

**Example**: If you like a laptop in "Electronics" category, the system will recommend other electronics with similar price ranges.

### Why This Algorithm?
- **Simple to understand**: Clear logic behind each recommendation
- **Works immediately**: Provides recommendations even for new users
- **Educational value**: Demonstrates core ML concepts without complexity

## Cython Performance Optimization

### What is Cython?
Cython allows us to speed up Python code by compiling it to C. It's especially useful for mathematical calculations.

### What We Optimized
The **cosine similarity calculation** used to find similar products. This involves nested loops and matrix operations that benefit from compilation.

### Performance Benefits
- **2-5x speedup** for similarity calculations
- **Faster recommendations** especially with many products
- **Graceful fallback**: If compilation fails, Python version still works

### How It Works
1. Mathematical operations use static typing (`cdef int`, `cdef double`)
2. NumPy arrays accessed directly without Python overhead
3. Nested loops compiled to C speed instead of Python speed

## Project Structure

```
ecommerce_project/
├── manage.py                 # Django management commands
├── requirements.txt          # Python dependencies
├── products/                 # Main Django app
│   ├── models.py            # Product and UserInteraction models
│   ├── views.py             # Views for products, cart, checkout
│   ├── cart_utils.py        # Session-based cart functions
│   └── templates/           # HTML templates
├── recommendations/          # ML recommendation engine
│   ├── engine.py            # SimpleRecommendationEngine class
│   ├── similarity.pyx       # Cython optimization
│   └── setup.py            # Cython compilation script
└── static/                  # CSS and JavaScript files
```

## Running Tests

```bash
# Test all functionality
python manage.py test

# Test specific components
python manage.py test products
python manage.py test recommendations
```

## Troubleshooting

### Cython Compilation Issues
If you see warnings about Cython compilation:
```bash
# Install build tools (Ubuntu/Debian)
sudo apt-get install build-essential python3-dev

# Or on other systems, install:
pip install setuptools wheel Cython
```

### Database Issues
If you encounter database errors:
```bash
# Reset database
rm db.sqlite3
python manage.py migrate
python manage.py create_sample_products
```

## Learning Objectives

This project demonstrates:
- **Django basics**: Models, views, templates, URL routing
- **Session management**: Cart functionality without user accounts
- **Machine learning concepts**: Content-based filtering, similarity calculations
- **Performance optimization**: Basic Cython usage with measurable improvements
- **Full-stack development**: Integration of backend ML with web frontend

---

**Created for internship assessment at Warewe Consultancy Private Limited**  
*Demonstrates Django, Machine Learning, and Cython skills at beginner level*