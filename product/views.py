from django.shortcuts import render,redirect
from django.views.generic import View
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout
from .decorators import unauthenticated_user
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import reverse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from datetime import date
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from .forms import CheckoutForm
from django.views.generic.edit import FormView
from django import forms
import stripe
from django.conf import settings

from .models import Item,Category,Order,OrderItem,Address,Payment,Coupon
stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required(login_url='/login/')
def index(request):
    items=Item.objects.all()
    order_qs=Order.objects.filter(user=request.user, ordered=False)
    order = order_qs[0]
    context={'items':items,'order':order}
    return render(request,'item.html',context)
    
    

def registerPage(request):
    if request.user.is_authenticated:
        return redirect('/')
    form=UserCreationForm()
    if request.method=='POST':
        form=UserCreationForm(request.POST)
        if form.is_valid():
            user=form.save()
            username=form.cleaned_data.get('username')
            group=Group.objects.get(name='Customer')
            user.groups.add(group)
            
            return redirect('/login/')
            
            
    context={'form':form}
    return render(request,'register.html',context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('/')
            
    context={}
    return render(request,'login.html',context)
def logoutUser(request):
    logout(request)
    return redirect('/login/')

@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    
    order_item,create= OrderItem.objects.get_or_create(item=item,ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            
            
            return redirect("product:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            
            return redirect("/")
    else:
        ordered_date = timezone.now()
        today = date.today()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
            
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        
        return redirect("/")

class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'ordersummary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")

@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item,ordered=False)
                
                
                
            order_item.delete()
            # order.items.remove(order_item)
            
            messages.info(request, "This item was removed from your cart.")
            return redirect("product:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("/")
    else:
        messages.info(request, "You do not have an active order")
        return redirect("/")


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item,ordered=False)[0]
                
                
                
            
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("product:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("/")
    else:
        messages.info(request, "You do not have an active order")
        return redirect("/")
# @login_required
# def checkout(request):
#     customer=request.user.address
    
#     if request.method == "POST":
#         form = AddressForm(request.POST, instance=customer)
#         if form.is_valid():
#             form.save()
#             return redirect('/')
#     else:
#         form = AddressForm(instance=customer)

#         return render(request, 'checkout.html', {'form': form})

# class AddressSelectionView(LoginRequiredMixin, FormView):
#     template_name = "address_select.html"
#     form_class = forms.AddressSelectionForm
#     success_url = reverse_lazy('checkout_done')

# def get_form_kwargs(self):
#     kwargs = super().get_form_kwargs()
#     kwargs['user'] = self.request.user
#     return kwargs
# def form_valid(self, form):
#     order = Order.objects.get(user=self.request.user, ordered=False)


#     order.address=form.cleaned_data['shipping_address']


#     return super().form_valid(form)
# @login_required
# def checkout(request):
    
    
#     if request.method == "POST":
#         form =AddressSelectionForm(request.POST)
#         if form.is_valid():
#             form.save()
#             order.address=form.cleaned_data['shipping_address']
#             return redirect('/')
#     else:
#         form = AddressSelectionForm(user=user)

#         return render(request, 'checkout.html', {'form': form})


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                
                'order': order,
                
            }

            address_qs = Address.objects.filter(
                user=self.request.user,
                
                default=True
            )
            if address_qs.exists():
                context.update(
                    {'default_address': address_qs[0]})

            billing_address_qs = Address.objects.filter(
                user=self.request.user,
                
                default=True
            )
            

            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("product:checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():

                use_default_address = form.cleaned_data.get(
                    'use_default_address')
                if use_default_address:
                    print("Using the defualt  address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        
                        default=True
                    )
                    if address_qs.exists():
                        address = address_qs[0]
                        order.address = address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default  address available")
                        return redirect('product:checkout')
                else:
                    print("User is entering a new  address")
                    house = form.cleaned_data.get(
                        'house')
                    street = form.cleaned_data.get(
                        'street')
                    landmark = form.cleaned_data.get(
                        'landmark')
                    city = form.cleaned_data.get(
                        'city')
                    zip = form.cleaned_data.get('zip')
                    mobile = form.cleaned_data.get('mobile')
                    set_default_address = form.cleaned_data.get('set_default_address')

                    if set_default_address:
                        address = Address(user=self.request.user,house_number=house,street_address=street,landmark=landmark,city=city,zip=zip,mobile_number=mobile,default =True)
                    else:
                        address = Address(user=self.request.user,house_number=house,street_address=street,landmark=landmark,city=city,zip=zip,mobile_number=mobile)
                    
                    address.save()

                    order.address =address
                    order.save()

                    
                            
                    
                    # address.save()
                        

                    # else:
                    #     messages.info(
                    #         self.request, "Please fill in the required  address fields")

                

                

                
                    
                   
                

                    
                        

                payment_option = form.cleaned_data.get('payment_option')

                if payment_option == 'S':
                    return redirect('product:payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('product:payment', payment_option='paypal')
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('product:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("product:order-summary")


class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.address:
            context = {
                'order': order,
                
            }
            
            return render(self.request, "payment.html", context)
        else:
            messages.warning(
                self.request, "You have not added a billing address")
            return redirect("product:checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        
        token =self.request.POST.get('stripeToken')
            

        amount = int(order.get_total() * 100)

        try:

                
            customer=stripe.Customer.create(email=self.request.POST['email'],name=self.request.user,source=self.request.POST.get('stripeToken'))      
            charge = stripe.Charge.create(customer=customer,amount=amount,currency="usd",description="fea")
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()
            
            order.ordered = True
            order.payment = payment
                
            order.save()

            messages.success(self.request, "Your order was successful!")
            return redirect("/")
        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            messages.warning(self.request, f"{err.get('message')}")
            return redirect("/")

            



      

        


            
                    
                          

                
                                                                                    
                                                                                    
                                                                                    
                                                                                    
                                                