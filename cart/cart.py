from .models import Cart, CartItem
from products.models import Product
from decimal import Decimal


class CartManager:
    def __init__(self, request):
        self.request = request
        self.user = request.user if request.user.is_authenticated else None

    def get_cart(self):
        if self.user:
            cart, _ = Cart.objects.get_or_create(user=self.user)
            return cart
        return None

    def add(self, product_id, quantity=1, custom_data=None):
        product = Product.objects.get(id=product_id)

        if self.user:
            cart = self.get_cart()
            item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity, 'custom_data': custom_data}
            )
            if not created:
                item.quantity += quantity
            item.save()
        else:
            session = self.request.session
            cart = session.get('cart', {})

            pid = str(product_id)
            if pid in cart:
                cart[pid]['quantity'] += quantity
            else:
                cart[pid] = {
                    'quantity': quantity,
                    'price': str(product.price),
                    'custom_data': custom_data
                }

            session['cart'] = cart
            session.modified = True


    def get_total_price(self):
        cart = self.get_cart()
        if not cart:
            return Decimal('0.00')

        total = Decimal('0.00')
        for item in cart.items.all():
            total += item.product.price * item.quantity
        return total
