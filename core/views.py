from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from .models import Item, OrderItem, Order
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import CustomUserCreationForm,  CustomAuthenticationForm
from  django.contrib.auth import login, authenticate
from .models import CustomUser
from django.contrib import messages


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


@login_required

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

#signup and signin
def signupandlogin_view(request):
    signup_form = CustomUserCreationForm()
    login_form = CustomAuthenticationForm()

    if request.method == "POST":
        if "signup" in request.POST:
            signup_form = CustomUserCreationForm(request.POST)
            if signup_form.is_valid():
                user = signup_form.save()
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect("core:item-list")
            
        elif "login" in request.POST:
            login_form = CustomAuthenticationForm(request, data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect("core:item-list")

    return render(request, "Main.html", {
        "signup_form": signup_form,
        "login_form": login_form
    })

@login_required 
def customer_list(request):
    users = CustomUser.objects.all()
    return render(request, "core/customers.html", {"users": users})


@login_required
def delete_customer(request, user_id):
    if request.user.is_superuser:  # only superusers can delete
        user = get_object_or_404(CustomUser, id=user_id)
        user.delete()
        messages.success(request, "User deleted successfully.")
    else:
        messages.error(request, "You are not authorized to delete users.")
    return redirect('core:customer-list')