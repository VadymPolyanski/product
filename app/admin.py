# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import Category, Product

admin.site.register(Category)
admin.site.register(Product)