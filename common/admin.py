from django.contrib import admin
from .models import Menu, File
from mptt.admin import DraggableMPTTAdmin

class FileAdmin(admin.ModelAdmin):
    search_fields = ['file_name']

admin.site.register(File, FileAdmin)
admin.site.register(Menu, DraggableMPTTAdmin)
