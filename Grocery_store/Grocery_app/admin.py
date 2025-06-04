from django.contrib import admin
from Grocery_app.models import Product,Category,Cart

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display =['id','name','Cimage']
admin.site.register(Category,CategoryAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = ['id','name','category','stock','description','Pimage','measures','discount_percentage']
    list_filter = ['category','price']
admin.site.register(Product,ProductAdmin)

class CartAdmin(admin.ModelAdmin):
    list_display = ['id','uid','productid','quantity']
    list_filter = ['uid']
admin.site.register(Cart, CartAdmin)