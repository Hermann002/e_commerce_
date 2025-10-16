from django.test import TestCase

# Create your tests here.

class TestCategoryModel(TestCase):
    def setUp(self):
        from .models import Category
        self.category = Category.objects.create(name="Electronics")

    def test_category_creation(self):
        self.assertEqual(self.category.name, "Electronics")
        self.assertIsNotNone(self.category.category_id)
    
class TestProductModel(TestCase):
    def setUp(self):
        from .models import Category, Product
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="Laptop",
            description="A high-end laptop",
            price=1500.00,
            stock=10,
            category=self.category,
            image_url="http://example.com/laptop.jpg",
            is_published=True
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, "Laptop")
        self.assertEqual(self.product.description, "A high-end laptop")
        self.assertEqual(self.product.price, 1500.00)
        self.assertEqual(self.product.stock, 10)
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(self.product.image_url, "http://example.com/laptop.jpg")
        self.assertTrue(self.product.is_published)
        self.assertIsNotNone(self.product.product_id)