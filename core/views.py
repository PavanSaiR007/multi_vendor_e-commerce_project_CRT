from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import UserProfile, Product, Cart, CartItem, Suggestion


@api_view(['POST'])
def api_register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    role = request.data.get('role', 'customer')  # defaults to customer if empty

    user = User.objects.create_user(username=username, password=password)
    UserProfile.objects.create(user=user, role=role)
    Cart.objects.create(user=user)  # Every user gets an empty cart!

    return Response({"message": f"Success! {role.capitalize()} '{username}' created."})


def login_view(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            auth_login(request, user)
            return redirect('/dashboard/')
        return render(request, 'core/login.html', {"error": "Invalid credentials"})
    return render(request, 'core/login.html')


def logout_view(request):
    auth_logout(request)
    return redirect('/login/')


@login_required(login_url='/login/')
def dashboard_view(request):
    profile = request.user.userprofile

    # SELLER DASHBOARD LOGIC
    if profile.role == 'seller':
        if request.method == 'POST':
            Product.objects.create(
                seller=request.user,
                name=request.POST['name'],
                price=request.POST['price'],
                stock=request.POST['stock']
            )
            return redirect('/dashboard/')
        products = Product.objects.filter(seller=request.user)  # Sellers only see their own products

    # CUSTOMER DASHBOARD LOGIC
    else:
        if request.method == 'POST' and 'add_to_cart' in request.POST:
            product = Product.objects.get(id=request.POST['product_id'])
            cart = request.user.cart
            # Check if product is already in cart, if so, increase quantity
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            if not created:
                cart_item.quantity += 1
                cart_item.save()
            return redirect('/dashboard/')
        products = Product.objects.all()  # Customers see all products

    return render(request, 'core/dashboard.html', {'role': profile.role, 'products': products})


@login_required(login_url='/login/')
def cart_view(request):
    cart = request.user.cart

    if request.method == 'POST':
        # Logic to DELETE an item
        if 'remove_item' in request.POST:
            item_id = request.POST.get('item_id')
            CartItem.objects.filter(id=item_id, cart=cart).delete()

        # Logic to UPDATE quantity
        elif 'update_qty' in request.POST:
            item_id = request.POST.get('item_id')
            new_qty = int(request.POST.get('quantity', 1))
            item = CartItem.objects.get(id=item_id, cart=cart)
            if new_qty > 0:
                item.quantity = new_qty
                item.save()
            else:
                item.delete()  # If they set qty to 0, just remove it

        return redirect('/cart/')

    cart_items = cart.items.all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'core/cart.html', {'cart_items': cart_items, 'total': total})

@login_required(login_url='/login/')
def suggestions_view(request):
    if request.method == 'POST':
        Suggestion.objects.create(user=request.user, message=request.POST['message'])
        return redirect('/suggestions/')

    suggestions = Suggestion.objects.all().order_by('-created_at')
    return render(request, 'core/suggestions.html', {'suggestions': suggestions})