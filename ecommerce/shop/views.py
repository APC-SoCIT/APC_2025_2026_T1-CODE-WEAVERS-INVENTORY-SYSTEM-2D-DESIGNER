from django.shortcuts import render

def index(request):
    return render(request, 'shop/index.html')

def product(request, id):
    return render(request, 'shop/product.html', {'product_id': id})

def cart(request):
    return render(request, 'shop/cart.html')