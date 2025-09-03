from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from .models import Item, OrderItem, Order
from django.contrib.auth.decorators import login_required
from django.utils import timezone



def item_list(request):
    men_wear = Item.objects.filter(category='MW')
    women_wear = Item.objects.filter(category='WW')
    all_items = Item.objects.filter(category='A')
    
    order = None
    if request.user.is_authenticated:
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]

    context = {
        'all': all_items,
        'men_wear': men_wear,
        'women_wear': women_wear,
        'order': order,
    }
    return render(request, "Main.html", context)


def add_to_cart(request, slug):
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login if not logged in

    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )

    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
        else:
            order.items.add(order_item)
    else:
        order = Order.objects.create(user=request.user, ordered=False)
        order.items.add(order_item)

    return redirect("core:cart")  # Redirect to cart page after adding

def view_cart(request):
     # Just show the current order; do NOT add anything
    order = Order.objects.filter(user=request.user, ordered=False).first()
    return render(request, "cart.html", {"order": order})


def remove_from_cart(request, slug):
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login if not logged in

    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]

        # Check if the item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = order.items.get(item__slug=item.slug)
            order.items.remove(order_item)
            order_item.delete()  # Delete the OrderItem instance

    return redirect('core:cart')  # Go back to cart page

def cart_view(request):
    order = None
    if request.user.is_authenticated:
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
    return render(request, "cart.html", {"order": order})