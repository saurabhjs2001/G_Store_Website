from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50 , unique=True)
    description = models.CharField(max_length=100, blank=True)
    Cimage = models.ImageField(upload_to='category_images',default='')


class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.IntegerField()
    discount_percentage = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=100,default='')
    stock = models.PositiveIntegerField()
    description = models.CharField(max_length=250,default='')
    Pimage = models.ImageField(upload_to='image')
    measures=models.CharField(max_length=50,default='')

    @property
    def discounted_price(products):
        if products.discount_percentage:
            discount = (products.discount_percentage / 100) * products.price
            return products.price - discount
        return products.price
    
    def save_amount(products):
        if products.discounted_price < products.price:
            return products.price - products.discounted_price
        return 0
    
class Cart(models.Model):
    uid = models.ForeignKey(User,on_delete=models.CASCADE,db_column='uid')
    productid = models.ForeignKey(Product,on_delete=models.CASCADE,db_column='productid')
    quantity = models.IntegerField(default=1)
    total_price=models.DecimalField(max_digits=10, decimal_places=2, default=0)

class Order(models.Model):
    STATUS_CHOICES = (
        ('Placed', 'Placed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
    )
    orderid = models.CharField(max_length=50)
    userid = models.ForeignKey(User,on_delete=models.CASCADE,db_column='userid')
    Productid = models.ForeignKey(Product,on_delete=models.CASCADE,db_column='Productid')
    quantity = models.IntegerField()
    total_amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=10)
    address = models.TextField()
    pincode = models.CharField(max_length=6)
    image = models.ImageField(upload_to='profile_image', default= ' ')

    def __str__(self):
        return self.user.username