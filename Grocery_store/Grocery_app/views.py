from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login,logout
from Grocery_app.models import Product,Cart,Order,Profile
from django.contrib import messages
from django.db.models import Q
import razorpay
import uuid
from django.core.mail import send_mail
from django.contrib import messages
import random



# Create your views here.
def index(request):
    query = request.GET.get('q', '')
    products = Product.objects.all()

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(category__icontains=query) |
            Q(price__icontains=query)
        )

    context = {
        'products': products,
        'query': query
    }
    return render(request, 'index.html', context)

def Products(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(category__icontains=query) |
            Q(price__icontains=query) 
        )
    else:
        products = Product.objects.all()

    context = {
        'products': products,
        'query': query
    }
    return render(request, 'Products.html', context)

    

def UserLogin(request):
    if request.method=="GET":
        return render(request,'login.html')
    else:
        u=request.POST['username']
        p=request.POST['password']

        user=authenticate(username=u,password=p)
        if user is not None:
            login(request,user)
            return redirect("/")
        else:
            context={}
            context['error']="Please enter a valid username & password"
            return render(request,'login.html',context)

def UserLogout(request):
    logout(request)
    return redirect('/')


def UserRegister(request,):
    if request.method=="GET":
        return render(request,'register.html')
    else:
        f=request.POST['first_name']
        l=request.POST['last_name']
        u=request.POST['username']
        e=request.POST['email']
        p=request.POST['password']
        cp=request.POST['c_password']

        context={}

        if f=="" or l=="" or u=="" or e=="" or p=="" or cp=="":
            context['error']="All fields are compulsary"
            return render(request,'register.html',context)
            
        elif p!=cp:
            context['error']="password & cinfirm password must be same"
            return render (request,'register.html',context)
        else:
            user=User.objects.create(first_name=f,last_name=l,username=u,email=e)
            user.set_password(p)
            user.save()
            return redirect('/login')
        
def ContactUs(request):
    if request.method=="GET":
        return render(request,'Contact_Us.html')
    
def about_us(request):
    if request.method=="GET":
        return render(request, 'about_us.html')

    
def GetById(request,prodid):
    context={}
    productobj=Product.objects.get(id=prodid)
    context['products']=productobj
    return render(request,'details.html',context)

def GetByCategory(request,catName):
    context={}
    allproducts=Product.objects.filter(category=catName)
    context['products']=allproducts
    return render(request,'Products.html',context)

def search(request):
    query = request.GET.get('q')
    results = Product.objects.filter(name__icontains=query)
    return render(request, 'search_results.html', {'results': results})


def addToCart(request, productid):
    if not request.user.is_authenticated:
        return redirect('/login')

    selected_product = Product.objects.get(id=productid)
    loggedin_user = request.user

    # Check if the product already exists in the user's cart
    existing_cart = Cart.objects.filter(uid=loggedin_user, productid=selected_product).first()

    if existing_cart:
        # If product is already in the cart, increase quantity and update total
        existing_cart.quantity += 1
        existing_cart.total_price = existing_cart.quantity * selected_product.discounted_price
        existing_cart.save()
    else:
        # Otherwise, create a new cart item
        cart = Cart.objects.create(
            uid=loggedin_user,
            productid=selected_product,
            quantity=1,
            total_price=selected_product.discounted_price
        )
        cart.save()

    return redirect('/Products')
    
def showMyCart(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    userid = request.user.id
    user=User.objects.get(id = userid)
    myCart=Cart.objects.filter(uid=user)
    context={'mycart':myCart}
    print(myCart)
    count=len(myCart)
    TotalBill=0
    for cart in myCart:
        TotalBill+=cart.productid.discounted_price * cart.quantity
    context['count']=count
    context['Totalbill']=TotalBill
    return render(request,'mycart.html',context)

def removeCart(request,cartid):
    c = Cart.objects.filter(id=cartid)
    c.delete()
    return redirect('/mycart')

def updateQuantity(request,cartid,operation):
    ucart=Cart.objects.filter(id=cartid)

    if operation =='incr':
        q=ucart[0].quantity
        ucart.update(quantity=q+1)
        return redirect('/mycart')
    else:
        q=ucart[0].quantity
        ucart.update(quantity=q-1)
        return redirect('/mycart')

def checkout_selected(request):
    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_items')
        if not selected_ids:
            messages.error(request, "Please select at least one item to proceed to checkout.")
            return redirect('/mycart')

    # select cart for current user
    selected_items = Cart.objects.filter(id__in=selected_ids, uid=request.user)

    # Add final_price to each item
    for item in selected_items:
        item.final_price = item.quantity * item.productid.discounted_price

    # add final prices for selected products
    total = sum(item.final_price for item in selected_items)

    return render(request, 'checkout.html', {
        'cart_items': selected_items,
        'total': total,
    })


def checkout_all(request):
    # get all the cart item for current user
        cart_items = Cart.objects.filter(uid=request.user)

    #  calculate the final price for each item
        for item in cart_items:
            item.final_price = item.quantity * item.productid.discounted_price

    # total amount for all item
        total = sum(item.final_price for item in cart_items)

    # get the user profile or to create if not exist
        profile, created = Profile.objects.get_or_create(user=request.user)

        return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'profile': profile,
    })


def makepayment(request):
        selected_ids = request.POST.getlist('selected_items')
        user = request.user

        if selected_ids:
            cart_items = Cart.objects.filter(id__in=selected_ids, uid=user)
        else:
            cart_items = Cart.objects.filter(uid=user)

        total = sum(item.quantity * item.productid.discounted_price for item in cart_items)

        client = razorpay.Client(auth=("rzp_test_rMwZicGe9ePAbb", "cTqU3gbw5rZFDf08pml4dLVd"))
        data = { "amount":total*100, "currency": "INR", "receipt": " " }
        payment = client.order.create(data=data)

        context = {
            'data': payment,
            'total_price': total,
            'user': user,
        }
        return render(request,'order.html',context)

def placeOrder(request):
    if request.method == 'POST':
        # Get shipping data
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        pincode = request.POST.get("pincode")

        # Save to profile if needed
        profile = request.user.profile  # Assuming you have OneToOne relation
        profile.phone = phone
        profile.address = address
        profile.pincode = pincode
        profile.save()

        # Order creation

        ordid = str(uuid.uuid4())  # convert UUID to string
        userid = request.user.id
        cartlist = Cart.objects.filter(uid=userid)

        order_items=[]
        
        for cart in cartlist:
            total_price = cart.quantity * cart.productid.discounted_price
            order = Order.objects.create(
                orderid=ordid,
                userid=cart.uid,
                Productid=cart.productid,
                quantity=cart.quantity,
                total_amount=total_price
            )
            order_items.append(order)

        cartlist.delete()

        msg = (
            "Thank You for Shopping with Us! We truly appreciate your purchase and your trust in us. "
            "We hope you enjoy your order and look forward to serving you again soon! Your order id is : "
            + ordid
        )
        send_mail(
            "Order Placed Successfully !!",
            msg,
            "saurabhdhelar@gmail.com",
            [request.user.email],
            fail_silently=False,
        )

        return redirect('/')
    
def myOrders(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(userid=request.user).order_by('-created_at')
        return render(request, 'myorders.html', {'order_items': orders})
    else:
        return redirect('/login')

otp_storage = {}

def forgetPassword(request):
    context = {}

    if request.method == 'POST':
        username = request.POST.get('username')
        context['username'] = username
        user_qs = User.objects.filter(username=username)

        if not user_qs.exists():
            context['error'] = 'Invalid username'
            return render(request, 'reset_password.html', context)

        user = user_qs.first()
        action = request.POST.get('action')

        if action == 'send_otp':
            otp = str(random.randint(100000, 999999))
            otp_storage[username] = otp  # Store OTP in memory

            send_mail(
                'Your OTP for Password Reset',
                f'Hello {user.username}, your OTP is: {otp}',
                'admin@example.com',
                [user.email],
            )

            context['message'] = 'OTP sent to your email.'
            context['otp_sent'] = True
            return render(request, 'forgetpassword.html', context)

        elif action == 'verify':
            entered_otp = request.POST.get('otp')
            new_password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            real_otp = otp_storage.get(username)

            if entered_otp != real_otp:
                context['error'] = 'Incorrect OTP.'
                context['otp_sent'] = True
                return render(request, 'forgetpassword.html', context)

            if new_password != confirm_password:
                context['error'] = 'Passwords do not match.'
                context['otp_sent'] = True
                return render(request, 'foegetpassword.html', context)

            user.set_password(new_password)
            user.save()
            del otp_storage[username]  # Clear OTP
            context['message'] = 'Password reset successfully.'
            return render(request, 'login.html', context)

    return render(request, 'forgetpassword.html')
   
def profile_view(request):
    user = request.user
    profile = Profile.objects.get(user=user)
  # assuming a OneToOne relationship

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name') 
        profile.phone = request.POST.get('phone')
        profile.address = request.POST.get('address')
        profile.pincode = request.POST.get('pincode')
        if len(profile.phone) > 11:
            return redirect('/profile', {
            'user': user,
            'profile': profile,
            'error': 'Phone number is too long'
            })
        profile.phone = profile.phone
        
        if 'image' in request.FILES:
            profile.image = request.FILES['image']
            
        user.save()
        profile.save()

        return render(request, 'profile.html', {'user': user, 'profile': profile, 'message': 'Profile updated successfully'})

    return render(request, 'profile.html', {'user': user, 'profile': profile})
