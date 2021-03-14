from django.contrib import admin
from .models import Menu

class MenuAdmin(admin.ModelAdmin):
    search_fields = ['title']

admin.site.register(Menu, MenuAdmin)
