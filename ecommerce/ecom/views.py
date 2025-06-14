from django.shortcuts import render,redirect,reverse,get_object_or_404
import decimal
from . import forms,models
from django.http import HttpResponseRedirect,HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.conf import settings
from django.utils import timezone
from .models import Customer
from django.urls import reverse
from .forms import InventoryForm
from .forms import CustomerLoginForm
from .models import Product
from .models import InventoryItem
from .models import Orders
from django.views.decorators.csrf import csrf_exempt
import requests
import json
import base64
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect

def order_counts(request):
    if request.user.is_authenticated and is_customer(request.user):
        customer = models.Customer.objects.get(user_id=request.user.id)
        context = {
            'pending_count': models.Orders.objects.filter(customer=customer, status='Pending').count(),
            'to_ship_count': models.Orders.objects.filter(customer=customer, status='Processing').count(),
            'to_receive_count': models.Orders.objects.filter(customer=customer, status='Shipping').count(),
            'delivered_count': models.Orders.objects.filter(customer=customer, status='Delivered').count(),
            'cancelled_count': models.Orders.objects.filter(customer=customer, status='Cancelled').count(),
        }
        return context
    return {}


def home_view(request):
    products=models.Product.objects.all()
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'ecom/index.html',{'products':products,'product_count_in_cart':product_count_in_cart})

@login_required(login_url='adminlogin')
def manage_inventory(request):
    inventory_items = InventoryItem.objects.all()
    if request.method == "POST":
        form = InventoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage-inventory')
    else:
        form = InventoryForm()

    return render(request, 'ecom/manage_inventory.html', {'form': form, 'inventory_items': inventory_items})

def update_stock(request, item_id):
    item = get_object_or_404(InventoryItem, id=item_id)
    if request.method == "POST":
        form = InventoryForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('manage-inventory')
    else:
        form = InventoryForm(instance=item)

    return render(request, 'ecom/update_stock.html', {'form': form, 'item': item})




@login_required(login_url='adminlogin')
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return HttpResponseRedirect('adminlogin')


def customer_signup_view(request):
    userForm = forms.CustomerUserForm()
    customerForm = forms.CustomerSignupForm()
    mydict = {'userForm': userForm, 'customerForm': customerForm}
    if request.method == 'POST':
        userForm = forms.CustomerUserForm(request.POST)
        customerForm = forms.CustomerSignupForm(request.POST, request.FILES)
        if userForm.is_valid() and customerForm.is_valid():
            user = userForm.save(commit=False)
            user.set_password(userForm.cleaned_data['password'])
            user.save()
            customer = customerForm.save(commit=False)
            customer.user = user
            customer.save()
            my_customer_group = Group.objects.get_or_create(name='CUSTOMER')
            my_customer_group[0].user_set.add(user)
            login(request, user)  # Log the user in after registration
            # Clear cart cookies after registration
            response = redirect('customer-home')
            response.delete_cookie('product_ids')
            # Remove all product_*_details cookies
            for key in request.COOKIES.keys():
                if key.startswith('product_') and key.endswith('_details'):
                    response.delete_cookie(key)
            return response
        else:
            # Show errors in the template
            mydict = {'userForm': userForm, 'customerForm': customerForm}
    return render(request, 'ecom/customersignup.html', context=mydict)

def customer_login(request):
  if request.method == 'POST':
    form = CustomerLoginForm(request.POST)
    if form.is_valid():
      username = form.cleaned_data['username']
      password = form.cleaned_data['password']
      user = authenticate(request, username=username, password=password)
      if user is not None:
        login(request, user)
        # Clear cart cookies after login
        response = redirect('home')
        response.delete_cookie('product_ids')
        for key in request.COOKIES.keys():
            if key.startswith('product_') and key.endswith('_details'):
                response.delete_cookie(key)
        return response
      else:
        form.add_error(None, 'Account not found, please register')
  else:
    form = CustomerLoginForm()
  return render(request, 'ecom/customerlogin.html', {'form': form})

#-----------for checking user iscustomer
def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()

@login_required
@user_passes_test(is_customer)
def add_custom_jersey_to_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Get the customer
            customer = models.Customer.objects.get(user=request.user)
            
            # Create a new product for the custom jersey
            custom_jersey = models.Product()
            custom_jersey.name = f'Custom Jersey - {customer.user.username}'
            custom_jersey.price = 99.99  # Set your custom jersey price
            custom_jersey.description = f'Custom jersey with name: {data["playerName"]} and number: {data["playerNumber"]}'
            
            # Convert base64 image to file
            if 'designImage' in data:
                format, imgstr = data['designImage'].split(';base64,')
                ext = format.split('/')[-1]
                image_data = ContentFile(base64.b64decode(imgstr), name=f'custom_jersey_{customer.user.username}.{ext}')
                custom_jersey.product_image = image_data
            
            custom_jersey.save()
            
            # Create order for the custom jersey
            order = models.Orders(
                customer=customer,
                product=custom_jersey,
                status='Pending',
                quantity=1
            )
            order.save()
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
            
    return JsonResponse({'success': False, 'error': 'Invalid request method'})



#---------AFTER ENTERING CREDENTIALS WE CHECK WHETHER USERNAME AND PASSWORD IS OF ADMIN,CUSTOMER
def afterlogin_view(request):
    if is_customer(request.user):
        return redirect('customer-home')
    else:
        return redirect('admin-dashboard')

#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    # for cards on dashboard
    customercount = models.Customer.objects.all().count()
    productcount = models.Product.objects.all().count()
    pending_ordercount = models.Orders.objects.filter(status='Pending').count()

    # Calculate sales analytics
    from django.utils import timezone
    from datetime import timedelta
    current_date = timezone.now()
    last_quarter_start = current_date - timedelta(days=90)
    last_month_start = current_date - timedelta(days=30)

    delivered_orders = models.Orders.objects.filter(status='Delivered').order_by('-created_at')[:10]
    recent_orders_products = []
    recent_orders_customers = []
    recent_orders_orders = []

    # Calculate total sales and period-specific sales
    all_delivered_orders = models.Orders.objects.filter(status='Delivered')
    total_sales = 0
    last_quarter_sales = 0
    last_month_sales = 0

    # Create a dictionary to track product sales
    product_sales = {}

    for order in all_delivered_orders:
        if not order.product:
            continue  # Skip orders with missing product
        order_total = order.product.price * order.quantity
        total_sales += order_total

        # Track product-wise sales
        if order.product.id not in product_sales:
            product_sales[order.product.id] = {
                'name': order.product.name,
                'quantity_sold': 0,
                'total_revenue': 0
            }
        product_sales[order.product.id]['quantity_sold'] += order.quantity
        product_sales[order.product.id]['total_revenue'] += order_total

        # Calculate period-specific sales
        order_date = order.created_at
        if order_date >= last_quarter_start:
            last_quarter_sales += order_total
            if order_date >= last_month_start:
                last_month_sales += order_total

    for order in delivered_orders:
        if not order.product:
            continue  # Skip orders with missing product
        order.total_price = order.product.price * order.quantity  # Add total_price attribute
        recent_orders_products.append(order.product)
        recent_orders_customers.append(order.customer)
        recent_orders_orders.append(order)
        # Debug print product image info
        print(f"Product: {order.product.name}, Image: {order.product.product_image}, Size: {order.size}")

    # Sort products by sales performance
    sorted_products = sorted(product_sales.values(), key=lambda x: x['quantity_sold'], reverse=True)
    fast_moving_products = sorted_products[:5] if sorted_products else []
    slow_moving_products = sorted_products[-5:] if len(sorted_products) >= 5 else []

    # Format sales numbers with commas
    formatted_total_sales = '{:,.2f}'.format(total_sales)
    formatted_last_quarter_sales = '{:,.2f}'.format(last_quarter_sales)
    formatted_last_month_sales = '{:,.2f}'.format(last_month_sales)

    mydict = {
        'customercount': customercount,
        'productcount': productcount,
        'ordercount': pending_ordercount,
        'total_sales': formatted_total_sales,
        'last_quarter_sales': formatted_last_quarter_sales,
        'last_month_sales': formatted_last_month_sales,
        'fast_moving_products': fast_moving_products,
        'slow_moving_products': slow_moving_products,
        'data': zip(recent_orders_products, recent_orders_customers, recent_orders_orders),
        'current_date': current_date.strftime('%Y-%m-%d')
    }
    return render(request, 'ecom/admin_dashboard.html', context=mydict)


# admin view customer table
@login_required(login_url='adminlogin')
def view_customer_view(request):
    customers = Customer.objects.all()
    
    # Prepare customer data with profile_pic_url
    customer_data = []
    for customer in customers:
        profile_pic_url = customer.profile_pic.url if customer.profile_pic else None
        customer_data.append({
            'customer': customer,
            'profile_pic_url': profile_pic_url,
        })
    
    context = {
        'customers': customer_data,
    }
    return render(request, 'ecom/view_customer.html', context)

# admin delete customer
@login_required(login_url='adminlogin')
def delete_customer_view(request,pk):
    customer=models.Customer.objects.get(id=pk)
    user=models.User.objects.get(id=customer.user_id)
    user.delete()
    customer.delete()
    return redirect('view-customer')


@login_required(login_url='adminlogin')
def update_customer_view(request,pk):
    customer=models.Customer.objects.get(id=pk)
    user=models.User.objects.get(id=customer.user_id)
    userForm=forms.CustomerUserForm(instance=user)
    customerForm=forms.CustomerForm(request.FILES,instance=customer)
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST,instance=user)
        customerForm=forms.CustomerForm(request.POST,instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return redirect('view-customer')
    return render(request,'ecom/admin_update_customer.html',context=mydict)

# admin view the product
@login_required(login_url='adminlogin')
def admin_products_view(request):
    # Get all products and order them by size
    products = models.Product.objects.all().order_by('size')
    return render(request, 'ecom/admin_products.html', {'products': products})


# admin add product by clicking on floating button
@login_required(login_url='adminlogin')
def admin_add_product_view(request):
    productForm=forms.ProductForm()
    if request.method=='POST':
        productForm=forms.ProductForm(request.POST, request.FILES)
        if productForm.is_valid():
            productForm.save()
        return HttpResponseRedirect('admin-products')
    return render(request,'ecom/admin_add_products.html',{'productForm':productForm})


@login_required(login_url='adminlogin')
def delete_product_view(request,pk):
    product=models.Product.objects.get(id=pk)
    product.delete()
    return redirect('admin-products')


@login_required(login_url='adminlogin')
def update_product_view(request,pk):
    product=models.Product.objects.get(id=pk)
    productForm=forms.ProductForm(instance=product)
    if request.method=='POST':
        productForm=forms.ProductForm(request.POST,request.FILES,instance=product)
        if productForm.is_valid():
            productForm.save()
            return redirect('admin-products')
    return render(request,'ecom/admin_update_product.html',{'productForm':productForm})


@login_required(login_url='adminlogin')
def admin_view_booking_view(request):
    return redirect('admin-view-processing-orders')

@login_required(login_url='adminlogin')
def admin_view_processing_orders(request):
    orders = models.Orders.objects.filter(status__in=['Pending', 'Processing'])
    return prepare_admin_order_view(request, orders, 'Processing', 'ecom/admin_view_orders.html')

@login_required(login_url='adminlogin')
def admin_view_confirmed_orders(request):
    orders = models.Orders.objects.filter(status='Order Confirmed')
    return prepare_admin_order_view(request, orders, 'Order Confirmed', 'ecom/admin_view_orders.html')

@login_required(login_url='adminlogin')
def admin_view_shipping_orders(request):
    orders = models.Orders.objects.filter(status='Out for Delivery')
    return prepare_admin_order_view(request, orders, 'Out for Delivery', 'ecom/admin_view_orders.html')

@login_required(login_url='adminlogin')
def admin_view_delivered_orders(request):
    orders = models.Orders.objects.filter(status='Delivered')
    return prepare_admin_order_view(request, orders, 'Delivered', 'ecom/admin_view_orders.html')

def prepare_admin_order_view(request, orders, status, template):
    # Order the orders by created_at descending to show new orders first
    orders = orders.order_by('-created_at')
    
    # Prepare a list of orders with their customer, shipping address, and order items
    orders_data = []
    for order in orders:
        order_items = models.OrderItem.objects.filter(order=order)
        items = []
        for item in order_items:
            items.append({
                'product': item.product,
                'quantity': item.quantity,
                'size': item.size,
                'price': item.price,
                'product_image': item.product.product_image.url if item.product.product_image else None,
            })
        # Use order.address if available, else fallback to customer's full address
        shipping_address = order.address if order.address else (order.customer.get_full_address if order.customer else '')
        orders_data.append({
            'order': order,
            'customer': order.customer,
            'shipping_address': shipping_address,
            'order_items': items,
            'status': order.status,
            'order_id': order.order_ref,
            'order_date': order.order_date,
        })
    return render(request, template, {
        'orders_data': orders_data,
        'status': status
    })

@login_required(login_url='adminlogin')
def admin_view_cancelled_orders(request):
    orders = models.Orders.objects.filter(status='Cancelled')
    ordered_products = []
    ordered_bys = []
    for order in orders:
        ordered_product = models.Product.objects.all().filter(id=order.product.id)
        ordered_by = models.Customer.objects.all().filter(id=order.customer.id)
        ordered_products.append(ordered_product)
        ordered_bys.append(ordered_by)
    return render(request, 'ecom/admin_view_cancelled_orders.html', {'data': zip(ordered_products, ordered_bys, orders)})


@login_required(login_url='adminlogin')
def delete_order_view(request,pk):
    order=models.Orders.objects.get(id=pk)
    order.delete()
    return redirect('admin-view-booking')

# for changing status of order (pending,delivered...)
@login_required(login_url='adminlogin')
def update_order_view(request,pk):
    order = models.Orders.objects.get(id=pk)
    orderForm = forms.OrderForm(instance=order)
    
    if request.method == 'POST':
        orderForm = forms.OrderForm(request.POST, instance=order)
        if orderForm.is_valid():
            # Save the form but don't commit yet
            updated_order = orderForm.save(commit=False)
            
            # If status has changed, update the status_updated_at timestamp
            if updated_order.status != order.status:
                updated_order.status_updated_at = timezone.now()
                
                # Set estimated delivery date based on status if not manually set
                if not updated_order.estimated_delivery_date:
                    if updated_order.status == 'Processing':
                        updated_order.estimated_delivery_date = timezone.now().date() + timezone.timedelta(days=7)
                    elif updated_order.status == 'Order Confirmed':
                        updated_order.estimated_delivery_date = timezone.now().date() + timezone.timedelta(days=5)
                    elif updated_order.status == 'Out for Delivery':
                        updated_order.estimated_delivery_date = timezone.now().date() + timezone.timedelta(days=1)
                
                # Reduce inventory when order is marked as delivered
                if updated_order.status == 'Delivered':
                    try:
                        inventory_item = models.InventoryItem.objects.get(product=updated_order.product)
                        if inventory_item.quantity >= updated_order.quantity:
                            inventory_item.quantity -= updated_order.quantity
                            inventory_item.save()
                            messages.success(request, f'Inventory updated: {inventory_item.product.name} quantity reduced by {updated_order.quantity}')
                        else:
                            messages.error(request, f'Insufficient inventory for {inventory_item.product.name}')
                            return render(request, 'ecom/update_order.html', {'orderForm': orderForm, 'order': order})
                    except models.InventoryItem.DoesNotExist:
                        messages.warning(request, f'No inventory item found for {updated_order.product.name}')
            
            updated_order.save()
            messages.success(request, f'Order status updated to {updated_order.get_status_display()}')
            return redirect('admin-view-booking')
    
    context = {
        'orderForm': orderForm,
        'order': order,
        'status_history': f"Last status update: {order.status_updated_at.strftime('%Y-%m-%d %H:%M:%S') if order.status_updated_at else 'Not available'}"
    }
    return render(request, 'ecom/update_order.html', context)


@login_required(login_url='adminlogin')
def delete_inventory(request, item_id):
    item = get_object_or_404(InventoryItem, id=item_id)
    item.delete()
    return redirect('manage-inventory')

@login_required(login_url='adminlogin')
def bulk_update_orders(request):
    if request.method == 'POST':
        order_ids = request.POST.getlist('order_ids')
        new_status = request.POST.get('bulk_status')
        
        if order_ids and new_status:
            orders = models.Orders.objects.filter(id__in=order_ids)
            current_time = timezone.now()
            
            # Calculate estimated delivery date based on new status
            delivery_date = None
            if new_status == 'Processing':
                delivery_date = current_time.date() + timezone.timedelta(days=7)
            elif new_status == 'Order Confirmed':
                delivery_date = current_time.date() + timezone.timedelta(days=5)
            elif new_status == 'Out for Delivery':
                delivery_date = current_time.date() + timezone.timedelta(days=1)
            
            # If marking as delivered, check and update inventory first
            if new_status == 'Delivered':
                inventory_updates = {}
                
                # First pass: Calculate total quantities needed for each product
                for order in orders:
                    product = order.product
                    if product.id in inventory_updates:
                        inventory_updates[product.id]['quantity_needed'] += order.quantity
                    else:
                        inventory_updates[product.id] = {
                            'quantity_needed': order.quantity,
                            'orders': [],
                            'product': product
                        }
                    inventory_updates[product.id]['orders'].append(order)
                
                # Second pass: Check inventory availability
                for product_id, update_info in inventory_updates.items():
                    try:
                        inventory_item = models.InventoryItem.objects.get(product=update_info['product'])
                        if inventory_item.quantity >= update_info['quantity_needed']:
                            inventory_item.quantity -= update_info['quantity_needed']
                            inventory_item.save()
                            messages.success(request, f'Inventory updated: {update_info["product"].name} quantity reduced by {update_info["quantity_needed"]}')
                        else:
                            messages.error(request, f'Insufficient inventory for {update_info["product"].name}')
                            return redirect('admin-view-booking')
                    except models.InventoryItem.DoesNotExist:
                        messages.warning(request, f'No inventory item found for {update_info["product"].name}')
            
            # Update all selected orders
            orders.update(
                status=new_status,
                status_updated_at=current_time,
                estimated_delivery_date=delivery_date
            )
            
            messages.success(request, f'Successfully updated {len(order_ids)} orders to {new_status}')
        else:
            messages.error(request, 'Please select orders and status to update')
            
    return redirect('admin-view-booking')

@login_required(login_url='adminlogin')
def edit_inventory(request, item_id):
    item = get_object_or_404(InventoryItem, id=item_id)
    
    if request.method == "POST":
        form = InventoryForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('manage-inventory')  # Redirect after saving
    else:
        form = InventoryForm(instance=item)

    return render(request, 'ecom/edit_inventory.html', {'form': form, 'item': item})


# admin view the feedback
@login_required(login_url='adminlogin')
def view_feedback_view(request):
    feedbacks=models.Feedback.objects.all().order_by('-id')
    return render(request,'ecom/view_feedback.html',{'feedbacks':feedbacks})



#---------------------------------------------------------------------------------
#------------------------ PUBLIC CUSTOMER RELATED VIEWS START ---------------------
#---------------------------------------------------------------------------------

@login_required(login_url='customerlogin')
def pending_orders_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    orders = models.Orders.objects.filter(customer=customer, status='Pending').order_by('-order_date', '-created_at')
    orders_with_items = []
    for order in orders:
        order_items = models.OrderItem.objects.filter(order=order)
        total_price = 0
        for item in order_items:
            total_price += item.price * item.quantity
        order.total = total_price
        orders_with_items.append({
            'order': order,
            'items': order_items
        })
    return render(request, 'ecom/order_status_page.html', {'orders_with_items': orders_with_items, 'status': 'Pending', 'title': 'Pending Orders'})

@login_required(login_url='customerlogin')
def to_ship_orders_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    orders = models.Orders.objects.filter(
        customer=customer,
        status__in=['Processing', 'Order Confirmed']
    ).order_by('-order_date')
    orders_with_items = []
    for order in orders:
        order_items = models.OrderItem.objects.filter(order=order)
        total_price = 0
        for item in order_items:
            total_price += item.price * item.quantity
        order.total = total_price
        orders_with_items.append({
            'order': order,
            'items': order_items
        })
    return render(request, 'ecom/order_status_page.html', {'orders_with_items': orders_with_items, 'status': 'To Ship', 'title': 'Orders To Ship'})

@login_required(login_url='customerlogin')
def to_receive_orders_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    orders = models.Orders.objects.filter(customer=customer, status='Out for Delivery').order_by('-order_date')
    orders_with_items = []
    for order in orders:
        order_items = models.OrderItem.objects.filter(order=order)
        total_price = 0
        for item in order_items:
            total_price += item.price * item.quantity
        order.total = total_price
        orders_with_items.append({
            'order': order,
            'items': order_items
        })
    return render(request, 'ecom/order_status_page.html', {'orders_with_items': orders_with_items, 'status': 'To Receive', 'title': 'Orders To Receive'})

@login_required(login_url='customerlogin')
def delivered_orders_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    orders = models.Orders.objects.filter(customer=customer, status='Delivered').order_by('-order_date')
    orders_with_items = []
    for order in orders:
        order_items = models.OrderItem.objects.filter(order=order)
        total_price = 0
        for item in order_items:
            total_price += item.price * item.quantity
        order.total = total_price
        orders_with_items.append({
            'order': order,
            'items': order_items
        })
    return render(request, 'ecom/order_status_page.html', {'orders_with_items': orders_with_items, 'status': 'Delivered', 'title': 'Delivered Orders'})

@login_required(login_url='customerlogin')
def cancelled_orders_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    orders = models.Orders.objects.filter(customer=customer, status='Cancelled').order_by('-status_updated_at')
    orders_with_items = []
    for order in orders:
        order_items = models.OrderItem.objects.filter(order=order)
        total_price = 0
        for item in order_items:
            total_price += item.price * item.quantity
        order.total = total_price
        orders_with_items.append({
            'order': order,
            'items': order_items
        })
    return render(request, 'ecom/order_status_page.html', {'orders_with_items': orders_with_items, 'status': 'Cancelled', 'title': 'Cancelled Orders'})

def cart_page(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    
    # Check if cart is empty
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty!')
        return redirect('customer-home')
        
    paypal_transaction_id = request.GET.get("paypal-payment-id")
    payment_method = request.POST.get("payment_method")
    custid = request.GET.get("custid")

    try:
        customer = Customer.objects.get(id=custid)
    except Customer.DoesNotExist:
        return HttpResponse("Invalid Customer ID")

    cart_items = Cart.objects.filter(user=user)

    # Check if the payment was made with PayPal
    if paypal_transaction_id:
        for cart in cart_items:
            OrderPlaced.objects.create(
                user=user,
                customer=customer,
                product=cart.product,
                quantity=cart.quantity,
                transaction_id=paypal_transaction_id,
            )
            cart.delete()  # Clear the cart after placing the order
        
        return redirect("orders")  # Redirect to order history page
    else:
        return HttpResponse("Invalid payment information")


def search_view(request):
    query = request.GET.get('query')
    if query is not None and query != '':
        products = models.Product.objects.all().filter(name__icontains=query)
    else:
        products = models.Product.objects.all()

    word = "Search Results for: " + query if query else ("Welcome, Guest" if not request.user.is_authenticated else "Welcome, " + request.user.username)

    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0

    return render(request,'ecom/customer_home.html',{'products':products,'word':word,'product_count_in_cart':product_count_in_cart, 'search_text': query})


# any one can add product to cart, no need of signin
def add_to_cart_view(request, pk):
    products = models.Product.objects.all()
    
    # Get size and quantity from form if available
    size = request.POST.get('size', 'M')  # Default to M if not provided
    quantity = int(request.POST.get('quantity', 1))  # Default to 1 if not provided
    
    # Check if product with given id and size exists
    try:
        product = models.Product.objects.get(id=pk, size=size)
    except models.Product.DoesNotExist:
        messages.error(request, f'Sorry, size {size} is not available for this product.')
        return redirect('customer-home')
    
    # Check if product quantity is sufficient
    if product.quantity < quantity:
        messages.error(request, f'Sorry, only {product.quantity} pcs available for {product.name} (Size: {size}).')
        return redirect('customer-home')
    
    # For cart counter, fetching products ids added by customer from cookies
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        product_keys = product_ids.split('|')
        product_count_in_cart = len(set(product_keys))
    else:
        product_count_in_cart = 0
    
    # Get next_page from POST or GET with a fallback to home page
    next_page = request.POST.get('next_page') or request.GET.get('next_page', '/')

    # Use consistent cookie key with size
    cookie_key = f'product_{pk}_{size}_details'
    existing_quantity = 0
    if cookie_key in request.COOKIES:
        details = request.COOKIES[cookie_key].split(':')
        if len(details) == 2:
            existing_quantity = int(details[1])

    new_quantity = existing_quantity + quantity

    response = render(request, 'ecom/index.html', {
        'products': products,
        'product_count_in_cart': product_count_in_cart,
        'redirect_to': next_page
    })
    response.set_cookie(cookie_key, f"{size}:{new_quantity}")

    # Update product_ids cookie to include product_{pk}_{size}
    product_key = f'product_{pk}_{size}'
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        product_keys = product_ids.split('|')
        if product_key not in product_keys:
            product_keys.append(product_key)
        updated_product_ids = '|'.join(product_keys)
    else:
        updated_product_ids = product_key
    response.set_cookie('product_ids', updated_product_ids)

    messages.info(request, product.name + f' (Size: {size}) added to cart successfully!')

    return response

def cart_view(request):
    region_choices = Customer.REGION_CHOICES  # <-- No extra indentation here!

    # For cart counter
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        product_keys = product_ids.split('|')
        product_count_in_cart = len(set(product_keys))
    else:
        product_count_in_cart = 0

    products = []
    total = 0
    delivery_fee = 0
    region = None
    if request.user.is_authenticated:
        try:
            customer = models.Customer.objects.get(user=request.user)
            region = customer.region
        except models.Customer.DoesNotExist:
            region = None
    # Set delivery fee based on region
    if region == 'NCR':
        delivery_fee = 49
    elif region == 'CAR':
        delivery_fee = 59
    elif region:
        delivery_fee = 69
    else:
        delivery_fee = 0

    vat_rate = 12
    vat_multiplier = 1 + (vat_rate / 100)

    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        product_keys = product_ids.split('|')
        product_ids_only = set()
        for key in product_keys:
            # key format: product_{pk}_{size}
            parts = key.split('_')
            if len(parts) >= 3:
                product_id = parts[1]
                size = '_'.join(parts[2:])
                product_ids_only.add(product_id)
            else:
                product_id = parts[1]
                size = 'M'
                product_ids_only.add(product_id)

        db_products = models.Product.objects.filter(id__in=product_ids_only)

        for p in db_products:
            # For each product, find all sizes in product_keys
            for key in product_keys:
                if key.startswith(f'product_{p.id}_'):
                    size = key[len(f'product_{p.id}_'):]
                    cookie_key = f'{key}_details'
                    if cookie_key in request.COOKIES:
                        details = request.COOKIES[cookie_key].split(':')
                        if len(details) == 2:
                            size = details[0]
                            quantity = int(details[1])
                            # Calculate VAT-exclusive unit price
                            unit_price_vat_ex = p.price / vat_multiplier
                            total += unit_price_vat_ex * quantity
                            products.append({
                                'product': p,
                                'size': size,
                                'quantity': quantity,
                                'unit_price_vat_ex': unit_price_vat_ex
                            })

    vat_amount = total * (vat_rate / 100)
    grand_total = total + delivery_fee + vat_amount
    return render(request, 'ecom/cart.html', {
        'products': products,
        'total': total,
        'delivery_fee': delivery_fee,
        'vat_rate': vat_rate,
        'vat_amount': vat_amount,
        'grand_total': grand_total,
        'product_count_in_cart': product_count_in_cart
    })

def remove_from_cart_view(request, pk):
    size = request.GET.get('size', 'M')  # Get size from request, default to M
    
    # For counter in cart
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        product_keys = product_ids.split('|')
        product_count_in_cart = len(set(product_keys))
    else:
        product_count_in_cart = 0

    # Remove only the specific product with the matching size
    specific_key = f'product_{pk}_{size}'
    product_keys_remaining = [key for key in product_keys if key != specific_key]

    products = []
    total = 0

    # Fetch remaining products
    product_ids_only = set()
    for key in product_keys_remaining:
        parts = key.split('_')
        if len(parts) >= 3:
            product_id = parts[1]
            product_ids_only.add(product_id)
        elif len(parts) == 2:
            product_id = parts[1]
            product_ids_only.add(product_id)

    db_products = models.Product.objects.filter(id__in=product_ids_only)

    for p in db_products:
        for key in product_keys_remaining:
            if key.startswith(f'product_{p.id}_'):
                size = key[len(f'product_{p.id}_'):]
                cookie_key = f'{key}_details'
                if cookie_key in request.COOKIES:
                    details = request.COOKIES[cookie_key].split(':')
                    if len(details) == 2:
                        size = details[0]
                        quantity = int(details[1])
                        total += p.price * quantity
                        products.append({
                            'product': p,
                            'size': size,
                            'quantity': quantity
                        })

    # Get next_page from GET with a fallback
    next_page = request.GET.get('next_page', '/')

    response = render(request, 'ecom/cart.html', {
        'products': products,
        'total': total,
        'delivery_fee': delivery_fee,
        'vat_rate': vat_rate,
        'vat_amount': vat_amount,
        'grand_total': grand_total,
        'product_count_in_cart': product_count_in_cart,
        'user_address': customer,  # Make sure this is passed!
        'region_choices': region_choices,  # <-- Add this line
    })

    # Remove cookie for the specific product-size combination
    cookie_key = f'{specific_key}_details'
    response.delete_cookie(cookie_key)

    # Update product_ids cookie
    if product_keys_remaining:
        response.set_cookie('product_ids', '|'.join(product_keys_remaining))
    else:
        response.delete_cookie('product_ids')

    return response



def send_feedback_view(request):
    feedbackForm=forms.FeedbackForm()
    if request.method == 'POST':
        feedbackForm = forms.FeedbackForm(request.POST)
        if feedbackForm.is_valid():
            feedbackForm.save()
            return render(request, 'ecom/feedback_sent.html')
    return render(request, 'ecom/send_feedback.html', {'feedbackForm':feedbackForm})


#---------------------------------------------------------------------------------
#------------------------ CUSTOMER RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_home_view(request):
    products=models.Product.objects.all()
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0
    return render(request,'ecom/customer_home.html',{'products':products,'product_count_in_cart':product_count_in_cart})



# shipment address before placing order
@login_required(login_url='customerlogin')
def customer_address_view(request):
    # Check if product is present in cart
    product_in_cart = False
    product_count_in_cart = 0
    total = 0

    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_in_cart = True
            counter = product_ids.split('|')
            product_count_in_cart = len(set(counter))
            
            # Calculate total price
            product_id_in_cart = product_ids.split('|')
            products = models.Product.objects.all().filter(id__in=product_id_in_cart)
            for p in products:
                # Calculate quantity from cookies for each product
                quantity = 1
                for key in product_ids.split('|'):
                    if key.startswith(f'product_{p.id}_'):
                        cookie_key = f'{key}_details'
                        if cookie_key in request.COOKIES:
                            details = request.COOKIES[cookie_key].split(':')
                            if len(details) == 2:
                                quantity = int(details[1])
                total += p.price * quantity

    # Get payment method from query parameter
    payment_method = request.GET.get('method', 'cod')

    # For COD, skip address form and use profile address
    if payment_method == 'cod':
        if not product_in_cart:
            return render(request, 'ecom/customer_address.html', {
                'product_in_cart': product_in_cart,
                'product_count_in_cart': product_count_in_cart
            })
        
        # Redirect directly to payment success for COD
        return redirect(f'/payment-success?method=cod')

    # For other payment methods, show address form
    addressForm = forms.AddressForm()
    if request.method == 'POST':
        addressForm = forms.AddressForm(request.POST)
        if addressForm.is_valid():
            email = addressForm.cleaned_data['Email']
            mobile = addressForm.cleaned_data['Mobile']
            address = addressForm.cleaned_data['Address']

            response = render(request, 'ecom/payment.html', {'total': total})
            response.set_cookie('email', email)
            response.set_cookie('mobile', mobile)
            response.set_cookie('address', address)
            return response

    return render(request, 'ecom/customer_address.html', {
        'addressForm': addressForm,
        'product_in_cart': product_in_cart,
        'product_count_in_cart': product_count_in_cart,
        'payment_method': payment_method
    })

@login_required(login_url='customerlogin')
def payment_success_view(request):
    import uuid
    customer = models.Customer.objects.get(user_id=request.user.id)
    products = None
    payment_method = request.GET.get('method', 'cod')  # Default to COD if not specified

    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_keys = request.COOKIES['product_ids'].split('|')
            product_ids_only = set()
            for key in product_keys:
                parts = key.split('_')
                if len(parts) >= 3:
                    product_id = parts[1]
                    product_ids_only.add(product_id)
            products = models.Product.objects.filter(id__in=product_ids_only)

    # For COD, use customer's profile information
    if payment_method == 'cod':
        email = customer.user.email
        mobile = str(customer.mobile)
        address = customer.get_full_address
    else:
        # For other payment methods (e.g., PayPal), use provided address
        email = request.COOKIES.get('email', customer.user.email)
        mobile = request.COOKIES.get('mobile', str(customer.mobile))
        address = request.COOKIES.get('address', customer.get_full_address)

    # Generate a unique short order reference ID
    import random
    import string
    def generate_order_ref(length=12):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    order_ref = generate_order_ref()

    # Create the parent order entry with order_ref
    initial_status = 'Processing' if payment_method == 'paypal' else 'Pending'
    parent_order = models.Orders.objects.create(
        customer=customer,
        status=initial_status,
        email=email,
        mobile=mobile,
        address=address,
        size='',
        quantity=0,
        payment_method=payment_method,
        order_date=timezone.now(),
        status_updated_at=timezone.now(),
        notes=f"Order Group ID: {order_ref}",
        order_ref=order_ref
    )

    # Create order items linked to the parent order
    for product in products:
        quantity = 1  # Default quantity to 1
        size = 'M'  # Default size
        for key in product_keys:
            if key.startswith(f'product_{product.id}_'):
                cookie_key = f'{key}_details'
                if cookie_key in request.COOKIES:
                    details = request.COOKIES[cookie_key].split(':')
                    if len(details) == 2:
                        size = details[0]
                        quantity = int(details[1])

                # Create order item linked to parent order with size
                models.OrderItem.objects.create(
                    order=parent_order,
                    product=product,
                    quantity=quantity,
                    price=product.price,
                    size=size
                )

                # Decrease product quantity
                product.quantity = max(0, product.quantity - quantity)
                product.save()
                print(f"Product {product.id} quantity decreased by {quantity}. New quantity: {product.quantity}")

                # Update inventory item quantity
                try:
                    inventory_item = models.InventoryItem.objects.get(name=product.name)
                    if inventory_item.quantity >= quantity:
                        inventory_item.quantity = max(0, inventory_item.quantity - quantity)
                        inventory_item.save()
                        print(f"Inventory item {inventory_item.name} quantity decreased by {quantity}. New quantity: {inventory_item.quantity}")
                    else:
                        print(f"Warning: Insufficient inventory for {inventory_item.name}")
                except models.InventoryItem.DoesNotExist:
                    print(f"Warning: No inventory item found for product {product.name}")

    # Clear cookies after order placement
    response = render(request, 'ecom/payment_success.html')
    response.delete_cookie('product_ids')

    # Only clear address cookies for non-COD payments
    if payment_method != 'cod':
        response.delete_cookie('email')
        response.delete_cookie('mobile')
        response.delete_cookie('address')

    # Clear product-specific cookies
    for product in products:
        for key in product_keys:
            if key.startswith(f'product_{product.id}_'):
                cookie_key = f'{key}_details'
                response.delete_cookie(cookie_key)

    return response

def place_order(request):
    print('Place Order view function executed')
    if request.method == 'POST':
        print('POST request received')
        customer = models.Customer.objects.get(user_id=request.user.id)
        
        # Get address from cookies if available, otherwise use customer's profile address
        address = request.COOKIES.get('address', customer.get_full_address)
        mobile = request.COOKIES.get('mobile', customer.mobile)
        
        # Create the order with the appropriate address
        order = Orders.objects.create(
            customer=customer,
            email=request.user.email,
            address=address,
            mobile=mobile,
            status='Pending',
            order_date=timezone.now()
        )
        
        design_data = request.POST.get('design_data')
        if design_data:
            # Handle custom design data if present
            print('Design data:', design_data)
            # Add custom design processing logic here
            
        print('Order created:', order)
        return JsonResponse({'message': 'Order placed successfully'})
    else:
        print('Invalid request method')
        return JsonResponse({'message': 'Invalid request method'}, status=400)

@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def cancel_order_view(request, order_id):
    try:
        customer = models.Customer.objects.get(user_id=request.user.id)
        order = models.Orders.objects.get(id=order_id, customer=customer)
        
        if order.status == 'Pending':
            order.status = 'Cancelled'
            order.status_updated_at = timezone.now()
            order.save()
            messages.success(request, 'Order cancelled successfully!')
        else:
            messages.error(request, 'Order cannot be cancelled at this time.')
    except models.Orders.DoesNotExist:
        messages.error(request, 'Order not found.')
    except models.Customer.DoesNotExist:
        messages.error(request, 'Customer not found.')
    
    return redirect('cancelled-orders')




@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def my_order_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    orders = models.Orders.objects.filter(customer=customer).order_by('-order_date')
    orders_with_items = []
    for order in orders:
        order_items = models.OrderItem.objects.filter(order=order)
        total_price = 0
        for item in order_items:
            total_price += item.price * item.quantity
        order.total = total_price
        orders_with_items.append({
            'order': order,
            'items': order_items
        })
    return render(request, 'ecom/my_order.html', {'orders_with_items': orders_with_items})

@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def my_order_view_pk(request, pk):
    customer = models.Customer.objects.get(user_id=request.user.id)
    order = get_object_or_404(models.Orders, id=pk, customer=customer)
    return render(request, 'ecom/order_detail.html', {'order': order, 'product': order.product})

def my_view(request):
    facebook_url = reverse('facebook')
    
def my_view(request):
    instagram_url = reverse('instagram')


import io
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result, encoding='UTF-8')
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None



def download_invoice_view(request, orderID):
    order = models.Orders.objects.get(id=orderID)
    order_items = models.OrderItem.objects.filter(order=order)

    # Use the stored shipment address from the order
    shipment_address = order.address if order.address else order.customer.address

    # Calculate item totals and order totals
    for item in order_items:
        item.unit_price = item.price  # Add unit price for display
        item.total = item.price * item.quantity

    subtotal = sum(item.total for item in order_items)
    
    # --- Delivery Fee Logic ---
    delivery_fee = 0
    region = None
    if order.customer and hasattr(order.customer, 'region'):
        region = order.customer.region
    if region == 'NCR':
        delivery_fee = 49
    elif region == 'CAR':
        delivery_fee = 59
    elif region:
        delivery_fee = 69
    else:
        delivery_fee = 0
    # --- End Delivery Fee Logic ---

    vat_rate = decimal.Decimal('12')  # Convert VAT rate to Decimal
    vat_amount = subtotal * (vat_rate / decimal.Decimal('100'))  # All calculations use Decimal
    total_price = subtotal + vat_amount + delivery_fee

    mydict = {
        'orderDate': order.order_date,
        'customerName': request.user,
        'customerEmail': order.email,
        'customerMobile': order.mobile,
        'shipmentAddress': shipment_address,
        'orderStatus': order.status,
        'orderItems': order_items,
        'subtotal': subtotal,
        'vat_rate': vat_rate,
        'vat_amount': vat_amount,
        'delivery_fee': delivery_fee,
        'totalPrice': total_price
    }
    return render_to_pdf('ecom/download_invoice.html', mydict)

def pre_order(request):
    return render(request, 'ecom/pre_order.html')


@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def my_profile_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    return render(request,'ecom/my_profile.html',{'customer':customer})


@user_passes_test(is_customer)
def edit_profile_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    user = models.User.objects.get(id=customer.user_id)
    
    if request.method == 'POST':
        userForm = forms.CustomerUserForm(request.POST, instance=user)
        customerForm = forms.CustomerForm(request.POST, request.FILES, instance=customer)
        
        if userForm.is_valid() and customerForm.is_valid():
            # Save user without changing password if it's empty
            if not userForm.cleaned_data['password']:
                del userForm.cleaned_data['password']
                user = userForm.save(commit=False)
            else:
                user = userForm.save(commit=False)
                user.set_password(userForm.cleaned_data['password'])
            user.save()
            
            # Save customer form
            customer = customerForm.save(commit=False)
            customer.user = user
            customer.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('my-profile')
        else:
            # Add specific error messages for each form
            for field, errors in userForm.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
            for field, errors in customerForm.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        userForm = forms.CustomerUserForm(instance=user)
        customerForm = forms.CustomerForm(instance=customer)
    
    return render(request, 'ecom/edit_profile.html', {
        'userForm': userForm,
        'customerForm': customerForm
    })




#---------------------------------------------------------------------------------
#------------------------ ABOUT US AND CONTACT US VIEWS START --------------------
#---------------------------------------------------------------------------------
def aboutus_view(request):
    return render(request,'ecom/about.html')

def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name)+' || '+str(email),message, settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER, fail_silently = False)
            return render(request, 'ecom/contactussuccess.html')
    return render(request, 'ecom/contactus.html', {'form':sub})

def jersey_customizer(request):
    return render(request, 'ecom/customizer.html')


def home(request):
    return render(request, 'ecom/home.html')

def manage_profile(request):
    return render(request, 'ecom/manage_profile.html')

def create(request):
    return render(request, 'ecom/create.html')

def jersey_customizer_advanced(request):
    return render(request, 'ecom/jersey_customizer_advanced.html')

def jersey_customizer(request):
    return render(request, 'ecom/jersey_customizer.html')

def jersey_template(request):
    return render(request, 'ecom/jersey_template.html')

def interactive_jersey(request):
    return render(request, 'ecom/interactive_jersey.html')


#-----------------------------------------------------------
#------------------------ PAYMONGO -------------------------
#-----------------------------------------------------------

# Replace with your own PayMongo test key
PAYMONGO_SECRET_KEY = 'sk_test_FFfnvsMb2YQSctcZ3NY8wThb'

def create_gcash_payment(request):
    url = "https://api.paymongo.com/v1/checkout_sessions"
    headers = {
        "Authorization": f"Basic {PAYMONGO_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    # Extract product details from cookies or session (example using cookies)
    product_ids = request.COOKIES.get('product_ids', '')
    if not product_ids:
        return JsonResponse({"error": "No products in cart"}, status=400)

    product_keys = product_ids.split('|')
    product_details = []
    total_amount = 0

    # Use a list to preserve order of products as in cart
    for key in product_keys:
        cookie_key = f"{key}_details"
        if cookie_key in request.COOKIES:
            details = request.COOKIES[cookie_key].split(':')
            if len(details) == 2:
                size = details[0]
                quantity = int(details[1])
                # Extract product id from key format: product_{id}_{size}
                parts = key.split('_')
                if len(parts) >= 2:
                    product_id = parts[1]
                    try:
                        product = models.Product.objects.get(id=product_id)
                        # Ensure product.price is decimal or float, convert to int cents properly
                        unit_price_cents = int(round(float(product.price) * 100))
                        total_amount += unit_price_cents * quantity
                        print(f"DEBUG: Product: {product.name}, Unit Price: {product.price}, Quantity: {quantity}, Amount (cents): {unit_price_cents * quantity}")
                        product_details.append({
                            "currency": "PHP",
                            "amount": unit_price_cents,
                            "name": f"{product.name} (Size: {size})",
                            "quantity": quantity
                        })
                    except models.Product.DoesNotExist:
                        continue

    if not product_details:
        return JsonResponse({"error": "No valid products found"}, status=400)

    payload = {
        "data": {
            "attributes": {
                "billing": {
                    "name": "Juan Dela Cruz",
                    "email": "juan@example.com",
                    "phone": "+639171234567"
                },
                "send_email_receipt": False,
                "show_line_items": True,
                "line_items": product_details,
                "payment_method_types": ["gcash"],
                "description": f"GCash Payment for {len(product_details)} item(s)",
                "success_url": "http://127.0.0.1:8000/payment-success/",
                "cancel_url": "http://127.0.0.1:8000/payment-cancel/"
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload, auth=(PAYMONGO_SECRET_KEY, ''))
    data = response.json()

    try:
        checkout_url = data['data']['attributes']['checkout_url']
        return redirect(checkout_url)
    except KeyError:
        return JsonResponse({"error": "Payment creation failed", "details": data}, status=400)

def payment_cancel(request):
    return HttpResponse("❌ Payment canceled.")

@login_required
def update_address(request):
    if request.method == 'POST':
        customer = Customer.objects.get(user=request.user)
        customer.full_name = request.POST.get('full_name')
        customer.region = request.POST.get('region')  # <-- Add this line
        customer.city = request.POST.get('city')
        customer.barangay = request.POST.get('brgy')
        customer.street_address = request.POST.get('street')
        customer.postal_code = request.POST.get('postal_code')
        customer.save()
        return redirect('cart')
    return redirect('cart')
