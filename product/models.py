from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse
from datetime import date



class Address(models.Model):
    user = models.ForeignKey(User,null=True,on_delete=models.CASCADE)
    house_number = models.CharField(max_length=100)
    street_address = models.CharField(max_length=100)
    landmark = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    zip = models.CharField(max_length=100)
    mobile_number = models.IntegerField()
    default = models.BooleanField(default=False)


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(User,null=True,on_delete=models.CASCADE)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code
    

    def __str__(self):
        return self.user.username

class Category(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True,null=True)

    def __str__(self) -> str:
        return self.name


class Item(models.Model):
    id=models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    price = models.FloatField(null=True,blank=True)
    discount_price = models.FloatField(blank=True, null=True)
    category = models.ForeignKey( Category,on_delete=models.SET_NULL,blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(blank=True, null=True)

    #   def get_absolute_url(self):
    #     return reverse(":product", kwargs={
    #         'slug': self.slug
    #     })

    def get_add_to_cart_url(self):
        return reverse("product:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("product:remove-from-cart", kwargs={
            'slug': self.slug
        })
    
    def __str__(self) -> str:
        return self.name

class OrderItem(models.Model):
    
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    

    def __str__(self):
        return f"{self.quantity} of {self.item.name}"

    def get_total_item_price(self):
        return self.item.price*self.quantity 

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()
    

class Order(models.Model):
    user = models.ForeignKey(User,null=True,on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    address = models.ForeignKey('Address',on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, blank=True, null=True)
        
    

    

    def __str__(self):
        return self.user.username
    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total




    



