from django.shortcuts import render

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from product.models import Item
from .cart import Cart
from .forms import CartAddProductForm

@require_POST
def cart_add(request, item_id):
    cart = Cart(request)
    item = get_object_or_404(Item, id=item_id)
    # form = CartAddProductForm(request.POST)
    # if form.is_valid():
    #     cd = form.cleaned_data
    cart.add(item=item)
    return redirect('cart:cart_detail')

def cart_remove(request, item_id):
    cart = Cart(request)
    product = get_object_or_404(Item, id=item_id)
    cart.remove(item)
    return redirect('')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'detail.html', {'cart': cart})