from django.contrib import admin
from .models import Menu
from mptt.admin import DraggableMPTTAdmin

admin.site.register(Menu, DraggableMPTTAdmin)
