import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from .models import Item, OrderItem, Order, ShippingAddress, Payment
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import CustomUserCreationForm,  CustomAuthenticationForm, CheckoutForm
from django.contrib.auth import login, authenticate, logout
from .models import CustomUser
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm

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

@login_required
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
    order = get_user_cart(request.user)
    if request.user.is_authenticated:
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
    return render(request, "cart.html", {"order": order})


def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            # Redirect to next page if present
            next_url = request.POST.get('next') or 'core:item-list'
            return redirect(next_url)
    else:
        form = CustomUserCreationForm()

    next_url = request.GET.get('next', '')
    return render(request, "core/signup.html", {"form": form, "next": next_url})


def login_view(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            # Redirect to next page if present
            next_url = request.POST.get('next') or 'core:item-list'
            return redirect(next_url)
    else:
        form = CustomAuthenticationForm()

    next_url = request.GET.get('next', '')
    return render(request, "core/login.html", {"form": form, "next": next_url})


def logout_view(request):
    logout(request)
    return redirect("core:login")

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

def get_user_cart(user):
    order, created = Order.objects.get_or_create(user=user, ordered=False)
    return order

@login_required
def checkout_view(request):
    order = Order.objects.filter(user=request.user, ordered=False).first()
    if not order:
        messages.error(request, "No active order found.")
        return redirect("core:cart")

    if request.method == "POST":
        fullname = request.POST.get("fullname")
        email = request.POST.get("email")
        address = request.POST.get("address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        country = request.POST.get("country")
        zip_code = request.POST.get("zip")
        payment_method = request.POST.get("payment_method")

        # save shipping details
        shipping = ShippingAddress.objects.create(
            user=request.user,
            full_name=fullname,
            email=email,
            address_line=address,
            city=city,
            state=state,
            country=country,
            postal_code=zip_code,
        )
        order.shipping_address = shipping

        # save payment
        payment = Payment.objects.create(
            user=request.user,
            amount=order.total,  # using @property total
            method=payment_method,
            reference=str(uuid.uuid4())[:10].upper(),
        )
        order.payment = payment
        order.ordered = True
        order.status = "paid"
        order.save()

        # clear cart items
        order.items.clear()

        messages.success(request, "Order placed successfully!")
        return redirect("core:checkout_success", ref=payment.reference)

    return render(request, "core/checkout.html", {"order": order})


@login_required
def checkout_success(request, ref):
    payment = get_object_or_404(Payment, reference=ref, user=request.user)
    order = Order.objects.filter(user=request.user, payment=payment).first()

     # mark order as paid/completed
    if order:
        order.status = "paid"
        order.ordered = True
        order.save()
    return render(request, "core/checkout_success.html", {"payment": payment, "order": order})
