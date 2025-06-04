from django.urls import path
from Grocery_app import views

from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('',views.index),
    path('Products',views.Products),
    path('register',views.UserRegister),
    path('login',views.UserLogin),
    path('logout',views.UserLogout),
    path('Contact_Us',views.ContactUs),
    path('about_us', views.about_us),
    path('details/<int:prodid>',views.GetById),
    path('filter-by-cat/<catName>',views.GetByCategory),
    path('addtocart/<int:productid>',views.addToCart),
    path('mycart',views.showMyCart),
    path('removecart/<cartid>',views.removeCart),
    path('updatequantity/<cartid>/<operation>',views.updateQuantity),
    path('checkout-selected/', views.checkout_selected, name='checkout_selected'),
    path('checkout/', views.checkout_all, name='checkout_all'),
    path('order',views.checkout_all),
    path('makepayment',views.makepayment),
    path('placeorder',views.placeOrder),
    path('myorders/', views.myOrders, name='myorders'),
    path('forgetPassword',views.forgetPassword),
    path('profile', views.profile_view),


]

urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)