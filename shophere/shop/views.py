from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from shop.form import CustomUserForm, MaterialForm
from django.contrib.auth import authenticate, login, logout
import json
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View

def home(request):
    products = Product.objects.filter(trending=1)
    material = Material.objects.filter(trending=1)
    category = Category.objects.all()
    context={
        "products":products,
        "material":material,
        "category":category
    }
    return render(request, "shop/index.html", context)
def profile(request):
    profile = Material.objects.filter(user=request.user)
    return render(request, "shop/profile.html", {'profile':profile})

def delete(request,id):
    product=Material.objects.get(id=id)
    product.delete()
    return redirect('profile')
def edit(request, id):
    product = Material.objects.get(id=id)
    if request.method == 'POST':
        form = MaterialForm(request.POST,request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('profile')  
    else:
        form = MaterialForm(instance=product)
    context = {
        'form': form,
          
    }
    return render(request, 'shop/material_form.html', context)


def cart_page(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user)
        return render(request, "shop/cart.html", {"cart": cart})
    else:
        return redirect('/')

def add_to_cart(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.user.is_authenticated:
            data = json.load(request)
            product_qty = data['product_qty']
            product_id = data['pid']
            product_status = Product.objects.get(id=product_id)
            if product_status:
                if Cart.objects.filter(user=request.user.id, product_id=product_id).exists():
                    return JsonResponse({'status': 'Product Already in Cart'}, status=200)
                else:
                    if product_status.quantity >= product_qty:
                        Cart.objects.create(user=request.user, product_id=product_id, product_qty=product_qty)
                        return JsonResponse({'status': 'Product Added to Cart'}, status=200)
                    else:
                        return JsonResponse({'status': 'Product Stock Not Available'}, status=200)
        else:
            return JsonResponse({'status': 'Login to Add Cart'}, status=200)
    else:
        return JsonResponse({'status': 'Invalid Access'}, status=200)

def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "Logged out successfully!")
    return redirect('/')

def login_page(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method == 'POST':
            name = request.POST.get('username')
            pwd = request.POST.get('password')
            user = authenticate(request, username=name, password=pwd)
            if user is not None:
                login(request, user)
                messages.success(request, "Logged in successfully!")
                return redirect('/') 
            else:
                messages.error(request, "Invalid Username or Password")
                return redirect('/login')  
        return render(request, "shop/login.html")

def register(request):
    form = CustomUserForm()
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registered successfully! You can login now.")
            return redirect('/login')
    return render(request, "shop/register.html", {'form': form})

def collections(request):
    category = Category.objects.filter(status=0)
    return render(request, "shop/collections.html", {"category": category})

def collectionsview(request, name):
    if Category.objects.filter(name=name, status=0).exists():
        products = Product.objects.filter(category__name=name)
        material = Material.objects.filter(category__name=name)  
        context={"products": products,"material" :material, "category__name": name}
        return render(request, "shop/products/index.html", context)
        
    else:
        messages.warning(request, "No item found")
        return redirect('collections')

def product_details(request, cname, pname):
    if Category.objects.filter(name=cname, status=0).exists():
        if Product.objects.filter(name=pname, status=0).exists():
            products = Product.objects.filter(name=pname).first()
            return render(request, "shop/products/productdetails.html", {"products": products})
        elif Material.objects.filter(name=pname, status=0).exists():
            products = Material.objects.filter(name=pname).first()
            return render(request, "shop/products/productdetails.html", {"products": products})
        else:
            messages.error(request, "No such product found")
            return redirect('collections')
    else:
        messages.error(request, "No such Category found")
        return redirect('collections')

def favviewpage(request):
    if request.user.is_authenticated:
        fav = Favourite.objects.filter(user=request.user)
        return render(request, "shop/fav.html", {"fav": fav})
    else:
        return redirect("/")

def remove_fav(request, fid):
    item = Favourite.objects.get(id=fid)
    item.delete()
    return redirect("/favviewpage")

def fav_page(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.user.is_authenticated:
            data = json.load(request)
            product_id = data['pid']
            product_status = Product.objects.get(id=product_id)
            if product_status:
                if Favourite.objects.filter(user=request.user.id, product_id=product_id).exists():
                    return JsonResponse({'status': 'Product Already in Favourite'}, status=200)
                else:
                    Favourite.objects.create(user=request.user, product_id=product_id)
                    return JsonResponse({'status': 'Product Added to Favourite'}, status=200)
        else:
            return JsonResponse({'status': 'Login to Add Favourite'}, status=200)
    else:
        return JsonResponse({'status': 'Invalid Access'}, status=200)

@method_decorator(login_required, name='dispatch')
class MaterialCreateView(View):
    def get(self, request):
        form = MaterialForm()
        return render(request, 'shop/material_form.html', {'form': form})

    def post(self, request):
        form = MaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.user = request.user
            material.save()
            return redirect('/')
        return render(request, 'shop/material_form.html', {'form': form})
