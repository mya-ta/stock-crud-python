from django.db import models

# Model for Color
class Color(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, default="")

    def __str__(self):
        return self.name

# Model for Size
class Size(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=5, default="")

    def __str__(self):
        return self.name

# Model for Product
class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)
    sku = models.CharField(max_length=255, default='', unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name

# Model for Product Variation
class ProductVariation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.product.name}-{self.color.name}-{self.size.name}"

    class Meta:
        unique_together = ('product', 'color', 'size')  # Ensures unique color/size combination
