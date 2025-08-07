from django.core.management.base import BaseCommand
from products.models import Product
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create sample product data for testing the e-commerce application'

    def handle(self, *args, **options):
        # Clear existing products
        Product.objects.all().delete()
        self.stdout.write('Cleared existing products')

        # Sample product data with different categories
        sample_products = [
            # Electronics
            {
                'name': 'MacBook Pro 16"',
                'description': 'Apple MacBook Pro with M2 Pro chip, 16GB RAM, 512GB SSD. Perfect for professional work and creative tasks.',
                'price': Decimal('2499.99'),
                'category': 'Electronics'
            },
            {
                'name': 'iPhone 15 Pro',
                'description': 'Latest iPhone with A17 Pro chip, 128GB storage, Pro camera system with 3x optical zoom.',
                'price': Decimal('999.99'),
                'category': 'Electronics'
            },
            {
                'name': 'Samsung 4K Smart TV 55"',
                'description': 'Crystal UHD 4K Smart TV with HDR, built-in streaming apps, and voice control.',
                'price': Decimal('699.99'),
                'category': 'Electronics'
            },
            {
                'name': 'Sony WH-1000XM5 Headphones',
                'description': 'Industry-leading noise canceling wireless headphones with 30-hour battery life.',
                'price': Decimal('399.99'),
                'category': 'Electronics'
            },
            {
                'name': 'Gaming Mechanical Keyboard',
                'description': 'RGB backlit mechanical keyboard with Cherry MX switches, perfect for gaming and typing.',
                'price': Decimal('149.99'),
                'category': 'Electronics'
            },     
       # Clothing
            {
                'name': 'Classic Denim Jacket',
                'description': 'Vintage-style denim jacket made from premium cotton. Perfect for casual wear.',
                'price': Decimal('89.99'),
                'category': 'Clothing'
            },
            {
                'name': 'Running Sneakers',
                'description': 'Lightweight running shoes with advanced cushioning and breathable mesh upper.',
                'price': Decimal('129.99'),
                'category': 'Clothing'
            },
            {
                'name': 'Wool Winter Coat',
                'description': 'Warm and stylish wool coat for cold weather. Available in multiple colors.',
                'price': Decimal('199.99'),
                'category': 'Clothing'
            },
            {
                'name': 'Cotton T-Shirt Pack',
                'description': 'Set of 3 premium cotton t-shirts in different colors. Comfortable and durable.',
                'price': Decimal('39.99'),
                'category': 'Clothing'
            },
            {
                'name': 'Leather Belt',
                'description': 'Genuine leather belt with classic buckle. Perfect for formal and casual wear.',
                'price': Decimal('49.99'),
                'category': 'Clothing'
            },

            # Home & Garden
            {
                'name': 'Coffee Maker',
                'description': 'Programmable drip coffee maker with thermal carafe. Brews up to 12 cups.',
                'price': Decimal('79.99'),
                'category': 'Home & Garden'
            },
            {
                'name': 'Indoor Plant Set',
                'description': 'Collection of 3 low-maintenance indoor plants perfect for home decoration.',
                'price': Decimal('34.99'),
                'category': 'Home & Garden'
            },
            {
                'name': 'Kitchen Knife Set',
                'description': 'Professional 8-piece knife set with wooden block. High-carbon stainless steel.',
                'price': Decimal('159.99'),
                'category': 'Home & Garden'
            },
            {
                'name': 'Throw Pillow Set',
                'description': 'Set of 2 decorative throw pillows with removable covers. Multiple patterns available.',
                'price': Decimal('29.99'),
                'category': 'Home & Garden'
            },
            {
                'name': 'LED Desk Lamp',
                'description': 'Adjustable LED desk lamp with touch controls and USB charging port.',
                'price': Decimal('45.99'),
                'category': 'Home & Garden'
            },    
        # Books
            {
                'name': 'Python Programming Guide',
                'description': 'Comprehensive guide to Python programming for beginners and intermediate developers.',
                'price': Decimal('24.99'),
                'category': 'Books'
            },
            {
                'name': 'Science Fiction Novel',
                'description': 'Award-winning science fiction novel about space exploration and artificial intelligence.',
                'price': Decimal('16.99'),
                'category': 'Books'
            },
            {
                'name': 'Cookbook: Healthy Meals',
                'description': 'Collection of 100+ healthy and delicious recipes for everyday cooking.',
                'price': Decimal('19.99'),
                'category': 'Books'
            },
            {
                'name': 'Business Strategy Book',
                'description': 'Essential guide to modern business strategy and entrepreneurship.',
                'price': Decimal('29.99'),
                'category': 'Books'
            },
            {
                'name': 'Art History Textbook',
                'description': 'Comprehensive overview of art history from ancient times to modern day.',
                'price': Decimal('89.99'),
                'category': 'Books'
            },

            # Sports & Outdoors
            {
                'name': 'Yoga Mat',
                'description': 'Non-slip yoga mat with extra cushioning. Perfect for yoga, pilates, and stretching.',
                'price': Decimal('39.99'),
                'category': 'Sports & Outdoors'
            },
            {
                'name': 'Camping Tent',
                'description': '4-person waterproof camping tent with easy setup. Includes carrying bag.',
                'price': Decimal('149.99'),
                'category': 'Sports & Outdoors'
            },
            {
                'name': 'Basketball',
                'description': 'Official size basketball with superior grip and durability for indoor/outdoor play.',
                'price': Decimal('24.99'),
                'category': 'Sports & Outdoors'
            },
            {
                'name': 'Hiking Backpack',
                'description': '40L hiking backpack with multiple compartments and hydration system compatibility.',
                'price': Decimal('89.99'),
                'category': 'Sports & Outdoors'
            },
            {
                'name': 'Resistance Bands Set',
                'description': 'Set of 5 resistance bands with different resistance levels for strength training.',
                'price': Decimal('19.99'),
                'category': 'Sports & Outdoors'
            }
        ]

        # Create products
        created_count = 0
        for product_data in sample_products:
            product = Product.objects.create(**product_data)
            created_count += 1
            self.stdout.write(f'Created product: {product.name}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} sample products')
        )
        
        # Display category summary
        categories = Product.objects.values_list('category', flat=True).distinct()
        self.stdout.write('\nProducts created by category:')
        for category in categories:
            count = Product.objects.filter(category=category).count()
            self.stdout.write(f'  {category}: {count} products')