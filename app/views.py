# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import generic, View
from django.views.generic import CreateView, UpdateView, DeleteView

from app.forms import UserForm, ProductForm
from app.models import Category, Product
from app.service.datetime_service import check_datetime

ADDRESS_MAIN = 'app/main.html'
ADDRESS_LAST_ADDED = 'app/last_added.html'
ADDRESS_CREATE_CATEGORY = 'app/create_category.html'
ADDRESS_REGISTRATION = 'app/registration_form.html'
ADDRESS_DETAIL_CATEGORY = 'app/detail_category.html'
ADDRESS_DETAIL_PRODUCT = 'app/detail_product.html'
ADDRESS_CREATE_PRODUCT = 'app/create_product.html'
ADDRESS_LOGIN_USER = 'app/login.html'
CATEGORY_FIELDS = ['name', 'slug', 'description']


class CategoriesView(generic.ListView):
    """
    @return:    a representation of all categories
    """
    template_name = ADDRESS_MAIN
    context_object_name = 'all_categories'

    def get_queryset(self):
        return Category.objects.all()


class DetailCategoryView(generic.DetailView):
    """
    @return:    a representation of all products in category
    """
    model = Category
    template_name = ADDRESS_DETAIL_CATEGORY


class DetailProductView(generic.DetailView):
    """
    @return:    a representation of product (name, description, price)
    """
    model = Product
    template_name = ADDRESS_DETAIL_PRODUCT


class CategoryCreate(CreateView):
    """
        create a category and save it in db
    """
    template_name = ADDRESS_CREATE_CATEGORY
    model = Category
    fields = CATEGORY_FIELDS


class CategoryUpdate(UpdateView):
    """
       update a category and save it in db
    """
    template_name = ADDRESS_CREATE_CATEGORY
    model = Category
    fields = CATEGORY_FIELDS
    success_url = reverse_lazy('app:main')


class CategoryDelete(DeleteView):
    """
       delete a category from db
    """
    model = Category
    success_url = reverse_lazy('app:main')


class ProductsView(generic.ListView):

    template_name = ADDRESS_LAST_ADDED
    context_object_name = 'all_products'

    @method_decorator(login_required(login_url='app:login_user'))
    def dispatch(self, request, *args, **kwargs):
        """
            checks the user authorization
        """
        return super(ProductsView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        @param products:    the set representation of all products     
        @param result:    the set representation of products added in last 24 hours    
        @return:            a set representation of all products added in last 24 hours
        """
        products = Product.objects.all()
        result = set()
        for product in products:
            if check_datetime(product.created_at):
                result.add(product)
        return result


class UserFormView(View):
    form_class = UserForm
    template_name = ADDRESS_REGISTRATION

    def get(self, request):
        """
        @param form:    the representation of registration form     
        @return:        registration form
        """
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """
        @param form:    the representation of registration form     
        @param user:    the model representation of new user    
        @param username:    the string representation of username data     
        @param password:    the string representation of password data     
        @return:        the representation of main page(success) or registration from(fail)
        """
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()

            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('app:main')

        return render(request, self.template_name, {'form': form})


def logout_user(request):
    """
    @param form:    the Form representation of user to login    
    @return:        the representation of login form
    """
    logout(request)
    form = UserForm(request.POST or None)
    context = {
        "form": form,
    }
    return render(request, ADDRESS_LOGIN_USER, context)


def login_user(request):
    """
    @param user:        the model representation of new user   
    @param username:    the string representation of username data     
    @param password:    the string representation of password data 
    @return:            the representation of main page(success) or login page(fail)
    """
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                categories = Category.objects.all()
                return render(request, ADDRESS_MAIN, {'all_categories': categories})
            else:
                return render(request, ADDRESS_LOGIN_USER, {'error_message': 'Your account has been disabled'})
        else:
            return render(request, ADDRESS_LOGIN_USER, {'error_message': 'Invalid login'})
    return render(request, ADDRESS_LOGIN_USER)


def create_song(request, category_slug):
    """
    @param form:        the Form-object representation of product to render page   
    @param category:    the model representation of category of product     
    @param product:    the model representation of new product     
    @return:            the representation of detail category page(If the fields are filled) 
                            or create_product page(If the fields are empty)
    """
    form = ProductForm(request.POST or None, request.FILES or None)
    category = get_object_or_404(Category, slug=category_slug)
    context = {
        'category': category,
        'form': form,
    }
    if form.is_valid():
        products = category.product_set.all()
        for p in products:
            if p.name == form.cleaned_data.get("name"):
                context['error_message'] = 'You already added that product'
                return render(request, ADDRESS_CREATE_PRODUCT, context)
        product = form.save(commit=False)
        product.category = category
        product.save()
        return render(request, ADDRESS_DETAIL_CATEGORY, {'category': category})

    return render(request, ADDRESS_CREATE_PRODUCT, context)
