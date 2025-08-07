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
            {
                'name': 'iPad Air',
                'description': 'Apple iPad Air with M2 chip, 10.9-inch Liquid Retina display, 256GB storage.',
                'price': Decimal('749.99'),
                'category': 'Electronics'
            },
            {
                'name': 'Gaming Desktop PC',
                'description': 'High-performance gaming PC with RTX 4070, Intel i7, 16GB RAM, 1TB NVMe SSD.',
                'price': Decimal('1899.99'),
                'category': 'Electronics'
            },
            {
                'name': 'Wireless Gaming Mouse',
                'description': 'Ultra-lightweight wireless gaming mouse with 20K DPI sensor and 80-hour battery.',
                'price': Decimal('79.99'),
                'category': 'Electronics'
            },
            {
                'name': 'Smart Home Hub',
                'description': 'Voice-controlled smart home hub compatible with Alexa, Google, and Apple HomeKit.',
                'price': Decimal('129.99'),
                'category': 'Electronics'
            },
            {
                'name': 'Wireless Earbuds',
                'description': 'True wireless earbuds with active noise cancellation and 8-hour battery life.',
                'price': Decimal('179.99'),
                'category': 'Electronics'
            },
            {
                'name': '27" 4K Monitor',
                'description': 'Professional 4K monitor with HDR support, USB-C connectivity, and height adjustment.',
                'price': Decimal('449.99'),
                'category': 'Electronics'
            },
            {
                'name': 'Portable SSD 1TB',
                'description': 'Ultra-fast portable SSD with USB 3.2 Gen 2 interface and shock-resistant design.',
                'price': Decimal('119.99'),
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
            {
                'name': 'Business Suit',
                'description': 'Premium wool business suit with modern slim fit. Includes jacket and matching pants.',
                'price': Decimal('299.99'),
                'category': 'Clothing'
            },
            {
                'name': 'Silk Dress',
                'description': 'Elegant silk evening dress with A-line silhouette. Perfect for special occasions.',
                'price': Decimal('189.99'),
                'category': 'Clothing'
            },
            {
                'name': 'Designer Sunglasses',
                'description': 'Premium sunglasses with UV protection and polarized lenses. Stylish metal frame.',
                'price': Decimal('159.99'),
                'category': 'Clothing'
            },
            {
                'name': 'Cashmere Sweater',
                'description': 'Luxurious cashmere sweater with crew neck. Available in multiple colors.',
                'price': Decimal('129.99'),
                'category': 'Clothing'
            },
            {
                'name': 'Leather Boots',
                'description': 'Handcrafted leather ankle boots with comfort sole and waterproof treatment.',
                'price': Decimal('179.99'),
                'category': 'Clothing'
            },
            {
                'name': 'Summer Dress',
                'description': 'Light and airy summer dress with floral pattern. Perfect for warm weather.',
                'price': Decimal('59.99'),
                'category': 'Clothing'
            },
            {
                'name': 'Athletic Shorts',
                'description': 'Moisture-wicking athletic shorts with built-in compression liner and side pockets.',
                'price': Decimal('34.99'),
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
            {
                'name': 'Dining Table Set',
                'description': 'Modern 6-piece dining table set with solid wood construction and cushioned chairs.',
                'price': Decimal('599.99'),
                'category': 'Home & Garden'
            },
            {
                'name': 'Stand Mixer',
                'description': 'Professional stand mixer with 5-quart bowl and multiple attachments for baking.',
                'price': Decimal('279.99'),
                'category': 'Home & Garden'
            },
            {
                'name': 'Air Purifier',
                'description': 'HEPA air purifier with smart sensors, covers up to 400 sq ft rooms.',
                'price': Decimal('199.99'),
                'category': 'Home & Garden'
            },
            {
                'name': 'Garden Tool Set',
                'description': '10-piece garden tool set with ergonomic handles and carrying tote.',
                'price': Decimal('79.99'),
                'category': 'Home & Garden'
            },
            {
                'name': 'Memory Foam Mattress',
                'description': 'Queen size memory foam mattress with cooling gel layer and 10-year warranty.',
                'price': Decimal('449.99'),
                'category': 'Home & Garden'
            },
            {
                'name': 'Smart Thermostat',
                'description': 'WiFi-enabled smart thermostat with app control and energy saving features.',
                'price': Decimal('189.99'),
                'category': 'Home & Garden'
            },
            {
                'name': 'Outdoor Fire Pit',
                'description': 'Steel fire pit with spark screen and poker tool. Perfect for backyard gatherings.',
                'price': Decimal('149.99'),
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
            {
                'name': 'Mystery Novel Collection',
                'description': 'Box set of 5 bestselling mystery novels by renowned authors.',
                'price': Decimal('39.99'),
                'category': 'Books'
            },
            {
                'name': 'Photography Guide',
                'description': 'Complete guide to digital photography with tips, techniques, and editing.',
                'price': Decimal('32.99'),
                'category': 'Books'
            },
            {
                'name': 'Children\'s Adventure Book',
                'description': 'Illustrated children\'s book about magical adventures. Ages 6-12.',
                'price': Decimal('14.99'),
                'category': 'Books'
            },
            {
                'name': 'Self-Help: Productivity',
                'description': 'Practical guide to improving productivity and time management skills.',
                'price': Decimal('18.99'),
                'category': 'Books'
            },
            {
                'name': 'World History Atlas',
                'description': 'Comprehensive atlas with maps, timelines, and historical information.',
                'price': Decimal('45.99'),
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
            },
            {
                'name': 'Road Bike',
                'description': '21-speed road bike with lightweight aluminum frame and carbon fork.',
                'price': Decimal('899.99'),
                'category': 'Sports & Outdoors'
            },
            {
                'name': 'Swimming Goggles',
                'description': 'Professional swimming goggles with anti-fog coating and UV protection.',
                'price': Decimal('29.99'),
                'category': 'Sports & Outdoors'
            },
            {
                'name': 'Golf Club Set',
                'description': 'Complete golf club set with driver, irons, wedges, putter, and carrying bag.',
                'price': Decimal('549.99'),
                'category': 'Sports & Outdoors'
            },
            {
                'name': 'Tennis Racket',
                'description': 'Professional tennis racket with graphite construction and comfortable grip.',
                'price': Decimal('129.99'),
                'category': 'Sports & Outdoors'
            },
            {
                'name': 'Fishing Rod Kit',
                'description': 'Complete fishing kit with rod, reel, tackle box, and assorted lures.',
                'price': Decimal('89.99'),
                'category': 'Sports & Outdoors'
            },
            {
                'name': 'Rock Climbing Harness',
                'description': 'Safety climbing harness with adjustable leg loops and gear loops.',
                'price': Decimal('79.99'),
                'category': 'Sports & Outdoors'
            },
            {
                'name': 'Kayak Paddle',
                'description': 'Lightweight aluminum kayak paddle with adjustable length and feathering.',
                'price': Decimal('69.99'),
                'category': 'Sports & Outdoors'
            },

            # Health & Beauty
            {
                'name': 'Skincare Set',
                'description': '5-piece skincare routine set with cleanser, toner, serum, moisturizer, and sunscreen.',
                'price': Decimal('89.99'),
                'category': 'Health & Beauty'
            },
            {
                'name': 'Electric Toothbrush',
                'description': 'Rechargeable electric toothbrush with multiple brushing modes and timer.',
                'price': Decimal('79.99'),
                'category': 'Health & Beauty'
            },
            {
                'name': 'Hair Dryer',
                'description': 'Professional ionic hair dryer with multiple heat and speed settings.',
                'price': Decimal('119.99'),
                'category': 'Health & Beauty'
            },
            {
                'name': 'Makeup Palette',
                'description': '30-color eyeshadow palette with mirror and dual-ended brushes.',
                'price': Decimal('49.99'),
                'category': 'Health & Beauty'
            },
            {
                'name': 'Vitamin Supplements',
                'description': 'Daily multivitamin supplements with essential vitamins and minerals.',
                'price': Decimal('24.99'),
                'category': 'Health & Beauty'
            },
            {
                'name': 'Essential Oil Set',
                'description': 'Set of 6 pure essential oils including lavender, eucalyptus, and tea tree.',
                'price': Decimal('39.99'),
                'category': 'Health & Beauty'
            },
            {
                'name': 'Face Mask Set',
                'description': 'Variety pack of 10 different face masks for different skin concerns.',
                'price': Decimal('29.99'),
                'category': 'Health & Beauty'
            },
            {
                'name': 'Massage Gun',
                'description': 'Percussive therapy massage gun with 6 speed settings and multiple attachments.',
                'price': Decimal('149.99'),
                'category': 'Health & Beauty'
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