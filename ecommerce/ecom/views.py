from django.shortcuts import render,redirect,reverse,get_object_or_404
from . import forms,models
from django.http import HttpResponseRedirect,HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.conf import settings
from .models import Customer
from django.urls import reverse
from .forms import InventoryForm
from .forms import CustomerLoginForm
from .models import Product
from .models import InventoryItem
from .models import Orders
import json


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
    userForm=forms.CustomerUserForm()
    customerForm=forms.CustomerForm()
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST)
        customerForm=forms.CustomerForm(request.POST,request.FILES)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customer=customerForm.save(commit=False)
            customer.user=user
            customer.save()
            my_customer_group = Group.objects.get_or_create(name='CUSTOMER')
            my_customer_group[0].user_set.add(user)
        return HttpResponseRedirect('customerlogin')
    return render(request,'ecom/customersignup.html',context=mydict)

def customer_login(request):
  if request.method == 'POST':
    form = CustomerLoginForm(request.POST)
    if form.is_valid():
      username = form.cleaned_data['username']
      password = form.cleaned_data['password']
      user = authenticate(request, username=username, password=password)
      if user is not None:
        login(request, user)
        return redirect('home')
      else:
        form.add_error(None, 'Account not found, please register')
  else:
    form = CustomerLoginForm()
  return render(request, 'ecom/customerlogin.html', {'form': form})

#-----------for checking user iscustomer
def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()



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

    # Calculate total sales for successful orders only
    delivered_orders = models.Orders.objects.filter(status='Delivered').order_by('-created_at')[:10]  # only delivered orders for recent orders
    total_sales = 0
    recent_orders_products = []
    recent_orders_customers = []
    recent_orders_orders = []

    all_delivered_orders = models.Orders.objects.filter(status='Delivered')
    for order in all_delivered_orders:
        total_sales += order.product.price * order.quantity

    for order in delivered_orders:
        order.total_price = order.product.price * order.quantity  # Add total_price attribute
        recent_orders_products.append(order.product)
        recent_orders_customers.append(order.customer)
        recent_orders_orders.append(order)
        # Debug print product image info
        print(f"Product: {order.product.name}, Image: {order.product.product_image}, Size: {order.size}")

    mydict = {
        'customercount': customercount,
        'productcount': productcount,
        'ordercount': pending_ordercount,
        'total_sales': total_sales,
        'data': zip(recent_orders_products, recent_orders_customers, recent_orders_orders),
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
    products=models.Product.objects.all()
    return render(request,'ecom/admin_products.html',{'products':products})


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
    orders=models.Orders.objects.all()
    ordered_products=[]
    ordered_bys=[]
    for order in orders:
        ordered_product=models.Product.objects.all().filter(id=order.product.id)
        ordered_by=models.Customer.objects.all().filter(id = order.customer.id)
        ordered_products.append(ordered_product)
        ordered_bys.append(ordered_by)
    return render(request,'ecom/admin_view_booking.html',{'data':zip(ordered_products,ordered_bys,orders)})


@login_required(login_url='adminlogin')
def delete_order_view(request,pk):
    order=models.Orders.objects.get(id=pk)
    order.delete()
    return redirect('admin-view-booking')

# for changing status of order (pending,delivered...)
@login_required(login_url='adminlogin')
def update_order_view(request,pk):
    order=models.Orders.objects.get(id=pk)
    orderForm=forms.OrderForm(instance=order)
    if request.method=='POST':
        orderForm=forms.OrderForm(request.POST,instance=order)
        if orderForm.is_valid():
            orderForm.save()
            return redirect('admin-view-booking')
    return render(request,'ecom/update_order.html',{'orderForm':orderForm})


@login_required(login_url='adminlogin')
def delete_inventory(request, item_id):
    item = get_object_or_404(InventoryItem, id=item_id)
    item.delete()
    return redirect('manage-inventory')

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

    product = models.Product.objects.get(id=pk)
    messages.info(request, product.name + f' (Size: {size}) added to cart successfully!')

    return response

def cart_view(request):
    # For cart counter
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        product_keys = product_ids.split('|')
        product_count_in_cart = len(set(product_keys))
    else:
        product_count_in_cart = 0

    products = []
    total = 0

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
                            total += p.price * quantity
                            products.append({
                                'product': p,
                                'size': size,
                                'quantity': quantity
                            })

    return render(request, 'ecom/cart.html', {
        'products': products,
        'total': total,
        'product_count_in_cart': product_count_in_cart
    })

def remove_from_cart_view(request, pk):
    # For counter in cart
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        product_keys = product_ids.split('|')
        product_count_in_cart = len(set(product_keys))
    else:
        product_count_in_cart = 0

    # We need to remove all sizes of product with id=pk
    product_keys_to_remove = [key for key in product_keys if key.startswith(f'product_{pk}_')]
    product_keys_remaining = [key for key in product_keys if not key.startswith(f'product_{pk}_')]

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
        'product_count_in_cart': product_count_in_cart,
        'redirect_to': next_page
    })

    # Remove cookies for the removed product sizes
    for key in product_keys_to_remove:
        cookie_key = f'{key}_details'
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
    # this is for checking whether product is present in cart or not
    # if there is no product in cart we will not show address form
    product_in_cart=False
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_in_cart=True
    #for counter in cart
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0

    addressForm = forms.AddressForm()
    if request.method == 'POST':
        addressForm = forms.AddressForm(request.POST)
        if addressForm.is_valid():
            # here we are taking address, email, mobile at time of order placement
            # we are not taking it from customer account table because
            # these thing can be changes
            email = addressForm.cleaned_data['Email']
            mobile=addressForm.cleaned_data['Mobile']
            address = addressForm.cleaned_data['Address']
            #for showing total price on payment page.....accessing id from cookies then fetching  price of product from db
            total=0
            if 'product_ids' in request.COOKIES:
                product_ids = request.COOKIES['product_ids']
                if product_ids != "":
                    product_id_in_cart=product_ids.split('|')
                    products=models.Product.objects.all().filter(id__in = product_id_in_cart)
                    for p in products:
                        total=total+p.price

            response = render(request, 'ecom/payment.html',{'total':total})
            response.set_cookie('email',email)
            response.set_cookie('mobile',mobile)
            response.set_cookie('address',address)
            return response
    return render(request,'ecom/customer_address.html',{'addressForm':addressForm,'product_in_cart':product_in_cart,'product_count_in_cart':product_count_in_cart})

@login_required(login_url='customerlogin')
def payment_success_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    products = None
    email = None
    mobile = None
    address = customer.address  # Default to profile address

    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_keys = product_ids.split('|')
            product_ids_only = set()
            for key in product_keys:
                parts = key.split('_')
                if len(parts) >= 3:
                    product_id = parts[1]
                    product_ids_only.add(product_id)
            products = models.Product.objects.filter(id__in=product_ids_only)

    # Check if the PayPal response contains address and contact details
    if 'email' in request.COOKIES:
        email = request.COOKIES['email']
    if 'mobile' in request.COOKIES:
        mobile = request.COOKIES['mobile']
    if 'address' in request.COOKIES:
        address = request.COOKIES['address']  # Override with PayPal address if available

    # Create orders for each product in the cart
    for product in products:
        quantity = 1  # Default quantity to 1
        size = 'M'  # Default size
        # Find all sizes for this product in product_keys
        for key in product_keys:
            if key.startswith(f'product_{product.id}_'):
                cookie_key = f'{key}_details'
                if cookie_key in request.COOKIES:
                    details = request.COOKIES[cookie_key].split(':')
                    if len(details) == 2:
                        size = details[0]
                        quantity = int(details[1])

                order, created = models.Orders.objects.get_or_create(
                    customer=customer,
                    product=product,
                    status='Pending',
                    email=email,
                    mobile=mobile,
                    address=address,
                    quantity=quantity,  # Set the quantity field
                    size=size,  # Set the size field
                )

                # Log the order creation
                print(f"Order created: {order.id}")

    # Clear cookies after order placement
    response = render(request, 'ecom/payment_success.html')
    response.delete_cookie('product_ids')
    response.delete_cookie('email')
    response.delete_cookie('mobile')
    response.delete_cookie('address')

    for product in products:
        # Delete all size cookies for this product
        for key in product_keys:
            if key.startswith(f'product_{product.id}_'):
                cookie_key = f'{key}_details'
                response.delete_cookie(cookie_key)

    return response

def place_order(request):
  print('Place Order view function executed')
  if request.method == 'POST':
    print('POST request received')
    design_data = request.POST.get('design_data')
    print('Design data:', design_data)
    # Process the design data and create a new order
    order = Orders.objects.create(
      # Add the order details here
    )
    print('Order created:', order)
    return JsonResponse({'message': 'Order placed successfully'})
  else:
    print('Invalid request method')
    return JsonResponse({'message': 'Invalid request method'})

def cancel_order_view(request, order_id):
    order = Orders.objects.get(id=order_id)
    if order.status == 'Pending':
        order.status = 'Cancelled'
        order.save()
        messages.success(request, 'Order cancelled successfully!')
    else:
        messages.error(request, 'Order cannot be cancelled at this time.')
    return redirect('home')




@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def my_order_view(request):
    
    customer = models.Customer.objects.get(user_id=request.user.id)
    orders = models.Orders.objects.filter(customer=customer)
    data = []
    for order in orders:
        product = order.product
        data.append((product, order))
    return render(request, 'ecom/my_order.html', {'data': data})

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



def download_invoice_view(request, orderID, productID):
    order = models.Orders.objects.get(id=orderID)
    product = models.Product.objects.get(id=productID)

    # Use the stored shipment address from the order
    shipment_address = order.address if order.address else order.customer.address

    total_price = product.price * order.quantity

    mydict = {
        'orderDate': order.order_date,
        'customerName': request.user,
        'customerEmail': order.email,
        'customerMobile': order.mobile,
        'shipmentAddress': shipment_address,  # Ensure this is used
        'orderStatus': order.status,

        'productName': product.name,
        'productImage': product.product_image,
        'productPrice': product.price,
        'productDescription': product.description,
        'quantity': order.quantity,
        'totalPrice': total_price,
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
    customer=models.Customer.objects.get(user_id=request.user.id)
    user=models.User.objects.get(id=customer.user_id)
    userForm=forms.CustomerUserForm(instance=user)
    customerForm=forms.CustomerForm(request.FILES,instance=customer)
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST,instance=user)
        customerForm=forms.CustomerForm(request.POST,request.FILES,instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            messages.success(request, 'Account Information saved!')
            return render(request,'ecom/edit_profile.html',context=mydict)
    return render(request,'ecom/edit_profile.html',context=mydict)




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