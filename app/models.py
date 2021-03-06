from django.core.urlresolvers import reverse
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=250)
    slug = models.CharField(max_length=250)
    description = models.CharField(max_length=500)

    def get_absolute_url(self):
        return reverse('app:detail_category', kwargs={'pk':self.id})

    def __str__(self):
        return self.name



class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    slug = models.CharField(max_length=250)
    description = models.CharField(max_length=500)
    price = models.FloatField(default=0)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()

    def __str__(self):
        return self.name
