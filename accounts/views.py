from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.forms import inlineformset_factory
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .decorators import admin_only, allowed_users, unauthenticated_user
from .filters import OrderFilter
from .forms import CreateUserForm, CustomerForm, OrderForm
from .models import *


@unauthenticated_user
def registerPage(request):

    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, "Account was created for %s" % username)
            return redirect("login")
    context = {"form": form}
    return render(request, "accounts/register.html", context)


@unauthenticated_user
def loginPage(request):

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request=request, username=username, password=password
        )

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.info(request, "Username/Password is not valid")
            return render(request, "accounts/login.html")

    context = {}
    return render(request, "accounts/login.html", context)


def logoutPage(request):
    logout(request)
    return redirect("login")


@login_required(login_url="login")
@admin_only
def home(request):
    customers = Customer.objects.all()
    orders = Order.objects.order_by("-date_created")
    orders_count = orders.count()
    delivered_count = orders.filter(status="Delivered").count()
    pending_count = orders.filter(status="Pending").count()
    context = {
        "customers": customers,
        "orders": orders[:5],
        "orders_count": orders_count,
        "delivered_count": delivered_count,
        "pending_count": pending_count,
    }

    return render(request, "accounts/dashboard.html", context)


@login_required(login_url="login")
@allowed_users(allowed_roles=["customer"])
def userPage(request):
    orders = request.user.customer.order_set.all()
    orders_count = orders.count()
    delivered_count = orders.filter(status="Delivered").count()
    pending_count = orders.filter(status="Pending").count()
    context = {
        "orders": orders,
        "orders_count": orders_count,
        "delivered_count": delivered_count,
        "pending_count": pending_count,
    }
    return render(request, "accounts/user.html", context)


@login_required(login_url="login")
@allowed_users(allowed_roles=["customer"])
def account_settings(request):
    form = CustomerForm(instance=request.user.customer)

    if request.method == "POST":
        form = CustomerForm(
            data=request.POST,
            files=request.FILES,
            instance=request.user.customer,
        )
        if form.is_valid():
            form.save()
    context = {"form": form}
    return render(request, "accounts/account_settings.html", context)


@login_required(login_url="login")
@allowed_users(allowed_roles=["admin"])
def products(request):
    products = Product.objects.all()
    context = {"products": products}
    return render(request, "accounts/products.html", context)


@login_required(login_url="login")
@allowed_users(allowed_roles=["admin"])
def customers(request, pk):
    customer = Customer.objects.get(id=pk)

    orders = customer.order_set.all()
    order_count = orders.count()

    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs
    context = {
        "customer": customer,
        "orders": orders,
        "order_count": order_count,
        "myFilter": myFilter,
    }

    return render(request, "accounts/customers.html", context)


@login_required(login_url="login")
@allowed_users(allowed_roles=["admin"])
def createOrder(request, pk):
    customer = Customer.objects.get(id=pk)
    OrderFormSet = inlineformset_factory(
        Customer, Order, fields=("product", "status"), extra=10
    )
    # form = OrderForm(initial={"customer": customer})
    formset = OrderFormSet(instance=customer, queryset=Order.objects.none())
    if request.method == "POST":
        # print(request.POST)
        formset = OrderFormSet(request.POST, instance=customer)
        if formset.is_valid():
            formset.save()
        return redirect("home")
    context = {"formset": formset, "customer": customer}
    return render(request, "accounts/order_form.html", context)


@login_required(login_url="login")
@allowed_users(allowed_roles=["admin"])
def updateOrder(request, pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)
    if request.method == "POST":
        print(request.POST)
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
        return redirect("home")
    context = {"form": form}
    return render(request, "accounts/order_form.html", context)


@login_required(login_url="login")
@allowed_users(allowed_roles=["admin"])
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == "POST":
        order.delete()
        return redirect("home")
    context = {"item": order}
    return render(request, "accounts/delete.html", context)
