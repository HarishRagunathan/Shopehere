from django.contrib.auth.forms import UserCreationForm
from .models import User,Material
from django import forms
class CustomUserForm(UserCreationForm):
    username=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter your username'}))
    email=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter your email'}))
    password1=forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Enter your password'}))
    password2=forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Enter your confrim password'}))
    class Meta:
        model=User
        fields=['username','email','password1','password2']

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['category', 'name', 'vendor', 'product_image', 'quantity', 'original_price', 'selling_price', 'description', 'status', 'trending']