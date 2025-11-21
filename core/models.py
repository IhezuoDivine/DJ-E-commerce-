from django.conf import settings 
from django.db import models
from django.contrib.auth.models import User
from  django.utils.text import slugify
from django.shortcuts import reverse
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone

CATEGORY_CHOICES = (
    ('A','All'),
    ('MW','Men wear'),
    ('WW','Women wear')
)

LABEL_CHOICES = (
    ('P','primary'),
    ('S','secondary'),
    ('D','danger')
)

class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    image = models.ImageField(upload_to='items/', blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            num = 1
            while Item.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:add_to_cart", kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)

    def get_total_price(self):
        return self.quantity * self.item.price

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

class Order(models.Model):
    STATUS_CHOICES = [
        ("cart", "In Cart"),
        ("paid", "Paid"),
        ("shipped", "Shipped"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(blank=True, null=True)
    ordered = models.BooleanField(default=False)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="cart")
    shipping_address = models.ForeignKey(
        "ShippingAddress", on_delete=models.SET_NULL, null=True, blank=True
    )
    payment = models.ForeignKey(
        "Payment", on_delete=models.SET_NULL, null=True, blank=True
    )

    def get_total_cart_price(self):
        return sum(item.get_total_price() for item in self.items.all())

    def get_total_cart_items(self):
        return sum(item.quantity for item in self.items.all())
    
    @property
    def subtotal(self):
        return self.get_total_cart_price()
    
    @property
    def shipping_fee(self):
        return 0 
    
    @property
    def total(self):
        return self.subtotal + self.shipping_fee
    

    def __str__(self):
        return self.user.username
    
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        if self.full_name:
            parts = self.full_name.strip().split(" ", 1)
            self.first_name = parts[0]
            self.last_name = parts[1] if len(parts) > 1 else ""
        super().save(*args, **kwargs)


class ShippingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    email = models.EmailField() 
    address_line = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default="Nigeria")
    postal_code = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.full_name}  - {self.address_line}, {self.city}"
    
    
class Payment(models.Model):
    METHOD_CHOICES = [
        ("cod", "Cash on Delivery"),
        ("card", "Card (Dummy)"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    reference = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.method} - {self.reference} - #{self.amount}"
