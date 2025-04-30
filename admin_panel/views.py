from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from store.models import Category, Product, Order, OrderItem, ProductImage
from django.utils.text import slugify
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

# Check if user is admin
def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Get low stock products (for example, items with stock less than 5)
    low_stock_products = Product.objects.filter(stock__lte=5).select_related('category')
    
    # Get recent orders (last 10 orders)
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
    
    # Get counts for dashboard stats
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='Pending').count()
    total_users = User.objects.filter(is_superuser=False).count()

    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_users': total_users,
        'low_stock_products': low_stock_products,
        'recent_orders': recent_orders,
    }
    
    return render(request, 'admin_panel/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def product_list(request):
    products = Product.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query))
    
    # Category filtering
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category__id=category_id)
    
    # Availability filtering
    availability = request.GET.get('availability')
    if availability == 'true':
        products = products.filter(available=True)
    elif availability == 'false':
        products = products.filter(available=False)
    
    # Sorting
    sort_by = request.GET.get('sort_by')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created')
    elif sort_by == 'stock_low':
        products = products.order_by('stock')
    elif sort_by == 'stock_high':
        products = products.order_by('-stock')
    else:
        products = products.order_by('name')
    
    # Get all categories for filter dropdown
    categories = Category.objects.all()
    
    # Pagination
    paginator = Paginator(products, 25)  # Show 25 products per page
    page_number = request.GET.get('page')
    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    return render(request, 'admin_panel/product_list.html', {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id,
        'selected_availability': availability,
        'sort_by': sort_by,
    })

@login_required
@user_passes_test(is_admin)
def add_product(request):
    categories = Category.objects.all()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        available = request.POST.get('available') == 'on'
        
        # Create product without image first
        product = Product(
            name=name,
            slug=slugify(name),
            category_id=category_id,
            description=description,
            price=price,
            stock=stock,
            available=available
        )
        product.save()
        
        # Handle primary image
        primary_image = request.FILES.get('primary_image')
        if primary_image:
            # Save primary image to Product model for backward compatibility
            product.image = primary_image
            product.save()
            
            # Also create a ProductImage entry for the primary image
            ProductImage.objects.create(
                product=product,
                image=primary_image,
                is_primary=True
            )
        
        # Handle additional images
        for i in range(1, 8):  # 7 additional images
            additional_image = request.FILES.get(f'additional_image_{i}')
            if additional_image:
                ProductImage.objects.create(
                    product=product,
                    image=additional_image,
                    is_primary=False
                )
        
        messages.success(request, 'Product added successfully')
        return redirect('admin_product_list')
        
    return render(request, 'admin_panel/add_product.html', {'categories': categories})

@login_required
@user_passes_test(is_admin)
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()
    product_images = product.images.all()
    
    if request.method == 'POST':
        try:
            # Handle image deletions first
            for i in range(8):  # Check for all possible image deletions (0-7)
                delete_image_id = request.POST.get(f'delete_image_{i}')
                if delete_image_id:
                    try:
                        image_to_delete = ProductImage.objects.get(id=delete_image_id)
                        # Don't delete if it's the only primary image
                        if not (image_to_delete.is_primary and not product.images.filter(is_primary=True).exclude(id=image_to_delete.id).exists()):
                            image_to_delete.delete()
                    except ProductImage.DoesNotExist:
                        pass

            # Rest of your existing edit_product code...
            name = request.POST.get('name')
            category_id = request.POST.get('category')
            description = request.POST.get('description', '').strip()
            price = request.POST.get('price')
            stock = request.POST.get('stock', 0)
            available = request.POST.get('available') == 'on'
            discount_percentage = request.POST.get('discount_percentage', 0)

            # Update product fields
            product.name = name
            product.category_id = category_id
            product.description = description
            product.price = price
            product.stock = stock
            product.available = available
            product.discount_percentage = discount_percentage

            # Handle new image uploads
            # ... rest of your existing image upload code ...

            product.save()
            messages.success(request, 'Product updated successfully')
            return redirect('admin_product_list')

        except Exception as e:
            messages.error(request, f'Error updating product: {str(e)}')
    
    return render(request, 'admin_panel/edit_product.html', {
        'product': product,
        'categories': categories,
        'product_images': product_images
    })

@login_required
@user_passes_test(is_admin)
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully')
        return redirect('admin_product_list')
        
    return render(request, 'admin_panel/delete_product.html', {'product': product})

@login_required
@user_passes_test(is_admin)
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'admin_panel/category_list.html', {'categories': categories})

@login_required
@user_passes_test(is_admin)
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        
        # Create category
        category = Category(
            name=name,
            slug=slugify(name)
        )
        category.save()
        
        messages.success(request, 'Category added successfully')
        return redirect('admin_category_list')
        
    return render(request, 'admin_panel/add_category.html')

@login_required
@user_passes_test(is_admin)
def order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'admin_panel/order_list.html', {'orders': orders})

@login_required
@user_passes_test(is_admin)
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        order.status = status
        order.save()
        messages.success(request, 'Order status updated successfully')
        
    return render(request, 'admin_panel/order_detail.html', {
        'order': order,
        'order_items': order_items
    })

@login_required
@user_passes_test(is_admin)
def user_list(request):
    users = User.objects.filter(is_staff=False)
    return render(request, 'admin_panel/user_list.html', {'users': users})


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

@login_required
@user_passes_test(is_admin)
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Order deleted successfully.')
        return redirect('admin_order_list')
    return render(request, 'admin_panel/delete_order.html', {'order': order})


# delete user 

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User and all related data deleted successfully.')
        return redirect('admin_user_list')
    return redirect('admin_user_list')

@login_required
@user_passes_test(is_admin)
def delete_category(request, category_id):
    if request.method == 'POST':
        category = get_object_or_404(Category, id=category_id)
        try:
            category.delete()
            messages.success(request, 'Category deleted successfully')
        except Exception as e:
            messages.error(request, 'Cannot delete category. It has associated products.')
    return redirect('admin_category_list')

@login_required
@user_passes_test(is_admin)
def edit_category(request, category_id):
    if request.method == 'POST':
        category = get_object_or_404(Category, id=category_id)
        new_name = request.POST.get('name')
        if new_name and new_name != category.name:
            category.name = new_name
            category.slug = slugify(new_name)
            category.save()
            messages.success(request, 'Category updated successfully')
        return redirect('admin_category_list')
    return redirect('admin_category_list')