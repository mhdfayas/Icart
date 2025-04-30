from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'discount_percentage', 'discounted_price', 
                   'stock', 'available', 'created', 'updated')
    list_filter = ('available', 'created', 'updated', 'category')
    list_editable = ('price', 'stock', 'available', 'discount_percentage')
    prepopulated_fields = {'slug': ('name',)}
    
    def discounted_price(self, obj):
        if obj.discount_percentage > 0:
            return f"₹{obj.discounted_price}"
        return "-"
    discounted_price.short_description = "Final Price"

class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')
    list_filter = ('created_at', 'user')

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'total_price')
    list_filter = ('cart', 'product')

    def total_price(self, obj):
        return obj.total_price
    total_price.short_description = 'Total Price'

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'user')
    search_fields = ('id', 'user__username')

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'price', 'quantity', 'total_price')
    list_filter = ('order', 'product')

    def total_price(self, obj):
        return obj.total_price
    total_price.short_description = 'Total Price'

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)