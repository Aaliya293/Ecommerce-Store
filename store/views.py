from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User

from django.contrib.auth import authenticate, login, logout

from .models import Product, Cart, Order, OrderItem


def home(request):

    query = request.GET.get('q')

    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()

    return render(request, 'home.html', {
        'products': products
    })


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'product_detail.html', {'product': product})


@login_required
def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')


@login_required
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)

    total = 0

    for item in cart_items:
        total += item.product.price * item.quantity

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
    })


@login_required
def remove_from_cart(request, id):
    item = get_object_or_404(Cart, id=id)
    item.delete()

    return redirect('cart')


def register(request):

    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['password']

        user = User.objects.create_user(
            username=username,
            password=password
        )

        user.save()

        return redirect('login')


    return render(request, 'register.html')


def login_user(request):

    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:

            login(request, user)

            return redirect('home')


    return render(request, 'login.html')


def logout_user(request):

    logout(request)

    return redirect('home')



@login_required
def my_orders(request):

    orders = Order.objects.filter(user=request.user).order_by('-order_date')

    return render(request, 'my_orders.html', {
        'orders': orders
    })

@login_required
def checkout(request):

    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():

        return redirect('cart')


    total = 0

    for item in cart_items:

        total += item.product.price * item.quantity


    order = Order.objects.create(

        user=request.user,

        total_amount=total

    )


    for item in cart_items:

        OrderItem.objects.create(

            order=order,

            product=item.product,

            quantity=item.quantity,

            price=item.product.price

        )


    cart_items.delete()


    return render(request, 'order_success.html', {
        'order': order
    })

    
