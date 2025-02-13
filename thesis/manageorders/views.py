from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, Product

# List all orders
def order_list(request):
    orders = Order.objects.all()
    return render(request, 'inventory/order_list.html', {'orders': orders})

# Add a new order
def add_order(request):
    if request.method == 'POST':
        product_id = request.POST.get('product')
        customer_name = request.POST.get('customer_name')
        quantity = request.POST.get('quantity')
        product = get_object_or_404(Product, id=product_id)
        Order.objects.create(product=product, customer_name=customer_name, quantity=quantity)
        return redirect('order_list')
    else:
        products = Product.objects.all()
    return render(request, 'accounts/preorder.html', {'products': products})

# Edit an order
def edit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('order_list')
    else:
        form = OrderForm(instance=order)
    return render(request, 'inventory/edit_order.html', {'form': form})