from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from cart.models import Cart, CartItem
from products.models import Product


@receiver(user_logged_in)
def merge_cart(sender, request, user, **kwargs):
    session_cart = request.session.get('cart', {})
    if not session_cart:
        return

    cart, _ = Cart.objects.get_or_create(user=user)

    for pid, data in session_cart.items():
        product = Product.objects.get(id=pid)
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': data['quantity']}
        )
        if not created:
            item.quantity += data['quantity']
        item.save()

    request.session['cart'] = {}
