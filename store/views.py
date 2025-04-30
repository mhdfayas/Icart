from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Product, Cart, CartItem, Order, OrderItem
from .models import ProductImage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

def home(request):
    products = Product.objects.filter(available=True)[:8]  # Get the latest 8 products
    categories = Category.objects.all()
    return render(request, 'store/home.html', {
        'products': products,
        'categories': categories
    })
def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    # Category filtering
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    # Price range filtering
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price and max_price:
        products = products.filter(price__gte=min_price, price__lte=max_price)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query))
    
    # Sorting
    sort_by = request.GET.get('sort_by')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created')
    else:
        products = products.order_by('name')
    
    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page_number = request.GET.get('page')
    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    return render(request, 'store/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products,
        'min_price': min_price,
        'max_price': max_price,
        'search_query': search_query,
        'sort_by': sort_by,
    })

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Review
from .forms import ReviewForm
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    reviews = product.reviews.all()
    product_images = product.images.all()
    
    # Get related products from the same category (excluding current product)
    related_products = Product.objects.filter(
        category=product.category, 
        available=True
    ).exclude(id=product.id)[:4]  # Limit to 4 products
    
    # Calculate average rating
    if reviews:
        avg_rating = sum(review.rating for review in reviews) / len(reviews)
    else:
        avg_rating = 0
    
    # Handle review submission
    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            new_review = review_form.save(commit=False)
            new_review.product = product
            new_review.user = request.user
            
            # Check if user has already reviewed this product
            existing_review = reviews.filter(user=request.user).first()
            if existing_review:
                # Update existing review
                existing_review.rating = new_review.rating
                existing_review.comment = new_review.comment
                existing_review.save()
            else:
                # Save new review
                new_review.save()
                
            return redirect('product_detail', slug=slug)
    else:
        review_form = ReviewForm()
    
    return render(request, 'store/product_detail.html', {
        'product': product,
        'product_images': product_images,
        'reviews': reviews,
        'review_form': review_form,
        'avg_rating': avg_rating,
        'review_count': reviews.count(),
        'related_products': related_products,
    })

    
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        CartItem.objects.create(cart=cart, product=product)
    
    # return redirect('product_detail', slug=slug)
    messages.success(request, 'Item added to cart successfully')    
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from .models import Cart, CartItem, Product

@login_required
@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    
    # Calculate total considering discounts
    total = sum(
        (item.product.discounted_price if item.product.has_discount else item.product.price) * item.quantity 
        for item in cart_items
    )
    
    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        # Ensure quantity is valid
        if quantity > 0 and quantity <= cart_item.product.stock:
            cart_item.quantity = quantity
            cart_item.save()
        
            
    return HttpResponseRedirect(reverse('cart_detail'))

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if request.method == 'POST':
        product_name = cart_item.product.name
        cart_item.delete()
        
    return HttpResponseRedirect(reverse('cart_detail'))

# @login_required
# def checkout(request):
#     # Handle checkout process
#     if request.method == 'POST':
#         address = request.POST.get('address')
#         phone = request.POST.get('phone')
        
#         cart, created = Cart.objects.get_or_create(user=request.user)
#         cart_items = CartItem.objects.filter(cart=cart)
        
#         if not cart_items:
#             return redirect('cart_detail')
            
#         total = sum(item.product.price * item.quantity for item in cart_items)
        
#         # Create order
#         order = Order.objects.create(
#             user=request.user,
#             address=address,
#             phone=phone,
#             total_price=total
#         )
        
#         # Create order items
#         for item in cart_items:
#             OrderItem.objects.create(
#                 order=order,
#                 product=item.product,
#                 price=item.product.price,
#                 quantity=item.quantity
#             )
            
#         # Clear cart
#         cart_items.delete()
        
#         return redirect('order_complete', order_id=order.id)
    
#     cart, created = Cart.objects.get_or_create(user=request.user)
#     cart_items = CartItem.objects.filter(cart=cart)
#     total = sum(item.product.price * item.quantity for item in cart_items)
    
#     return render(request, 'store/checkout.html', {
#         'cart_items': cart_items,
#         'total': total
#     })

#  razorpay integration

import razorpay
from django.conf import settings
from django.shortcuts import render, redirect
from .models import Cart, CartItem, Order, OrderItem

@login_required
def checkout(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    
    # Calculate item totals
    for item in cart_items:
        if item.product.has_discount:
            item.total = item.product.discounted_price * item.quantity
        else:
            item.total = item.product.price * item.quantity
    
    # Calculate subtotal and total
    subtotal = sum(item.total for item in cart_items)
    total = subtotal  # Add shipping cost here if needed
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total': total,
    }
    
    if request.method == 'POST':
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        payment_method = request.POST.get('payment_method')

        if not cart_items:
            return redirect('cart_detail')

        # Use the calculated total for payment processing
        if payment_method == 'online':
            # Initialize Razorpay client
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

            # Create Razorpay order
            razorpay_order = client.order.create({
                'amount': int(total * 100),  # Amount in paise
                'currency': 'INR',
                'payment_capture': '1'
            })

            # Pass Razorpay order details to the template
            return render(request, 'store/razorpay_payment.html', {
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'amount': int(total * 100),
                'address': address,
                'phone': phone,
            })

        else:
            # Handle Cash on Delivery
            order = Order.objects.create(
                user=request.user,
                address=address,
                phone=phone,
                total_price=total
            )

            for item in cart_items:
                price = item.product.discounted_price if item.product.has_discount else item.product.price
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=price,  
                    quantity=item.quantity
                )

    

            # for item in cart_items:
            #     OrderItem.objects.create(
            #         order=order,
            #         product=item.product,
            #         price=item.product.price,
            #         quantity=item.quantity
            #     )

            cart_items.delete()

            return redirect('order_complete', order_id=order.id)

    return render(request, 'store/checkout.html', context)

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
@login_required
def razorpay_success(request):
    if request.method == 'POST':
        payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        
        # Calculate total with discounts - same as cash on delivery
        total = sum(
            (item.product.discounted_price if item.product.has_discount else item.product.price) * item.quantity 
            for item in cart_items
        )

        # Create order with proper total
        order = Order.objects.create(
            user=request.user,
            address=address,
            phone=phone,
            total_price=total,
            razorpay_order_id=razorpay_order_id,
            razorpay_payment_id=payment_id,
            status='processing'
        )

        # Create order items with correct prices
        for item in cart_items:
            price = item.product.discounted_price if item.product.has_discount else item.product.price
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=price,  # Use discounted price if available
                quantity=item.quantity
            )

        cart_items.delete()
        messages.success(request, 'Order placed successfully!')
        return JsonResponse({'success': True, 'order_id': order.id})

    else:
        messages.error(request, 'Payment failed. Please try again.')
        return JsonResponse({'success': False})

##################################################################################
@login_required
def order_complete(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_complete.html', {'order': order})

@login_required
def orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/orders.html', {'orders': orders})

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, available=True)
    return render(request, 'store/category_detail.html', {
        'category': category,
        'products': products
    })

def about(request):
    return render(request, 'store/about.html')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def profile(request):
    if request.method == 'POST':
        user = request.user
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    return render(request, 'store/profile.html')

def shipping(request):
    return render(request, 'store/shipping.html')

from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Send email
        send_mail(
            subject=f"Contact Form Submission from {name}",
            message=message,
            from_email=email,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('contact')
    
    return render(request, 'store/contact.html')

def faq(request):
    faqs = [
        {"question": "How do I place an order?", "answer": "You can place an order by browsing our products and adding them to your cart."},
        {"question": "What payment methods do you accept?", "answer": "We accept Visa, MasterCard, American Express, and PayPal."},
        {"question": "How can I track my order?", "answer": "You can track your order by logging into your account and visiting the 'Orders' page."},
    ]
    return render(request, 'store/faq.html', {'faqs': faqs})

from django.contrib import messages

def newsletter_subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        # Save email to database or send to email service
        messages.success(request, 'Thank you for subscribing to our newsletter!')
        return redirect('home')
    return redirect('home')

from django import template
register = template.Library()

from django.db.models import Q

def search(request):
    query = request.GET.get('q', '').strip()
    products = []
    
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()
        
        if not products:
            messages.info(request, f'No products found matching "{query}"')
    
    return render(request, 'store/search_results.html', {
        'products': products,
        'query': query
    })

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    # Check if the user is authorized to delete the review
    if request.user == review.user:
        # Get the product before deleting the review
        product = review.product
        # Delete the review
        review.delete()
        messages.success(request, 'Review deleted successfully.')
        # Redirect back to the product detail page
        return redirect('product_detail', slug=product.slug)
    else:
        messages.error(request, 'You are not authorized to delete this review.')
        return redirect('home')
