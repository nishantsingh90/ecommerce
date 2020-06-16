from django.contrib import admin

from .models import Item,Category,Order,OrderItem,Coupon,Payment,Address
admin.site.register(Item)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Coupon)
admin.site.register(Payment)
admin.site.register(Address)
