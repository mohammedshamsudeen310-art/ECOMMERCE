from django.shortcuts import render, redirect
from .cart import CartManager
from products.models import Product


def cart_detail(request):
    if request.user.is_authenticated:
        cart = request.user.cart
        items = cart.items.all()
    else:
        items = request.session.get('cart', {}).items()

    return render(request, 'cart/cart_detail.html', {'items': items})


def add_to_cart(request, product_id):
    cart = CartManager(request)
    cart.add(product_id)
    return redirect('cart:cart_detail')


def remove_from_cart(request, product_id):
    if request.user.is_authenticated:
        cart = request.user.cart
        cart.items.filter(product_id=product_id).delete()
    else:
        cart = request.session.get('cart', {})
        cart.pop(str(product_id), None)
        request.session['cart'] = cart

    return redirect('cart:cart_detail')
