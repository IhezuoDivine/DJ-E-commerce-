from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path('', views.item_list, name='item-list'),
    path('add_to_cart/<slug:slug>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('remove_from_cart/<slug:slug>/', views.remove_from_cart, name='remove_from_cart'),
    path('view_cart/', views.view_cart, name='view_cart'),
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("customers/", views.customer_list, name="customer"),
    path("customers/delete/<int:user_id>/", views.delete_customer, name="delete-customer"),
    path("checkout/", views.checkout_view, name="checkout"),
    path("checkout/success/<str:ref>/", views.checkout_success, name="checkout_success"),
    path('cancel/', views.cancel, name='cancel'),
]