from django.shortcuts import render
from products.models import Product, Category

def home_view(request):
    featured_products = Product.objects.filter(
        is_featured=True,
        is_active=True
    )[:8]

    categories = Category.objects.filter(
        is_active=True,
        parent__isnull=True
    )

    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'home.html', context)
