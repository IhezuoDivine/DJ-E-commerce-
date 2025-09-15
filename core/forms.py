from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from .models import ShippingAddress, Payment

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=100, required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'full_name', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        full_name = self.cleaned_data['full_name']
        parts = full_name.strip().split(" ", 1)
        user.first_name = parts[0]
        if len(parts) > 1:
            user.last_name = parts[1]

        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email")

class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=120)
    phone = forms.CharField(max_length=30)
    address_line = forms.CharField(max_length=300, label ="Address")
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=100, required=False)
    country = forms.CharField(max_length=100, initial="Nigeria")
    postal_code = forms.CharField(max_length=20, required=False)

    payment_method = forms.ChoiceField(choices=Payment.METHOD_CHOICES, widget=forms.RadioSelect)

