from .cart import CartManager

def cart_processor(request):
    cart_manager = CartManager(request)
    cart = cart_manager.get_cart()
    cart_count = cart.items.count() if cart else 0
    return {'cart_count': cart_count}
